/**
 * Synapse API Gateway
 * Unified entry point with rate limiting, load balancing, and service discovery
 */

const express = require('express');
const helmet = require('helmet');
const cors = require('cors');
const compression = require('compression');
const morgan = require('morgan');
const { createProxyMiddleware } = require('http-proxy-middleware');
const rateLimit = require('express-rate-limit');
const { RedisStore } = require('rate-limit-redis');
const Redis = require('ioredis');
const jwt = require('jsonwebtoken');
const winston = require('winston');
const { v4: uuidv4 } = require('uuid');
require('dotenv').config();

// Create Express app
const app = express();

// Logger configuration
const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.Console({
      format: winston.format.simple()
    }),
    new winston.transports.File({ filename: 'api-gateway.log' })
  ]
});

// Redis client for rate limiting and caching
let redis = null;
let redisAvailable = false;

try {
  redis = new Redis({
    host: process.env.REDIS_HOST || 'localhost',
    port: process.env.REDIS_PORT || 6379,
    retryStrategy: (times) => {
      if (times > 3) {
        console.log('Redis unavailable, using in-memory fallback');
        return null;
      }
      return Math.min(times * 50, 2000);
    },
    lazyConnect: true
  });
  
  redis.on('connect', () => {
    redisAvailable = true;
    logger.info('Redis connected');
  });
  
  redis.on('error', (err) => {
    redisAvailable = false;
    logger.warn('Redis error:', err.message);
  });
  
  redis.connect().catch(() => {
    redisAvailable = false;
    logger.warn('Redis connection failed, using in-memory fallback');
  });
} catch (error) {
  logger.warn('Redis initialization failed:', error.message);
}

// Service registry - defines all backend services
const services = {
  auth: {
    url: process.env.AUTH_SERVICE_URL || 'http://localhost:8001',
    path: '/api/v1/auth',
    rateLimit: { windowMs: 60 * 1000, max: 10 },
    description: 'Authentication and user management'
  },
  users: {
    url: process.env.AUTH_SERVICE_URL || 'http://localhost:8001',
    path: '/api/v1/users',
    rateLimit: { windowMs: 60 * 1000, max: 100 },
    description: 'User profile management'
  },
  subscriptions: {
    url: process.env.AUTH_SERVICE_URL || 'http://localhost:8001',
    path: '/api/v1/subscriptions',
    rateLimit: { windowMs: 60 * 1000, max: 50 },
    description: 'Subscription and billing'
  },
  'api-keys': {
    url: process.env.AUTH_SERVICE_URL || 'http://localhost:8001',
    path: '/api/v1/api-keys',
    rateLimit: { windowMs: 60 * 1000, max: 20 },
    description: 'API key management'
  },
  stripe: {
    url: process.env.STRIPE_SERVICE_URL || 'http://localhost:8000',
    path: '/stripe',
    rateLimit: { windowMs: 60 * 1000, max: 30 },
    description: 'Stripe webhook processing'
  },
  mcp: {
    url: process.env.MCP_SERVICE_URL || 'http://localhost:3002',
    path: '/mcp',
    rateLimit: { windowMs: 60 * 1000, max: 100 },
    description: 'Model Context Protocol server'
  },
  quantum: {
    url: process.env.QUANTUM_SERVICE_URL || 'http://localhost:5000',
    path: '/api/v1/quantum',
    rateLimit: { windowMs: 60 * 1000, max: 50 },
    description: 'Quantum computing simulations'
  },
  ai: {
    url: process.env.AI_SERVICE_URL || 'http://localhost:5001',
    path: '/api/v1/ai',
    rateLimit: { windowMs: 60 * 1000, max: 50 },
    description: 'AI/ML processing'
  }
};

// Tier-based rate limits (requests per minute)
const tierLimits = {
  free: { rpm: 10, rph: 100, rpd: 500 },
  starter: { rpm: 100, rph: 5000, rpd: 50000 },
  professional: { rpm: 500, rph: 25000, rpd: 500000 },
  enterprise: { rpm: 2000, rph: 100000, rpd: 2000000 },
  quantum: { rpm: -1, rph: -1, rpd: -1 } // Unlimited
};

// Middleware

// Security headers
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      scriptSrc: ["'self'", "'unsafe-inline'"],
      imgSrc: ["'self'", "data:", "https:"],
    },
  },
}));

// CORS configuration
app.use(cors({
  origin: process.env.CORS_ORIGINS?.split(',') || ['http://localhost:3000'],
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-API-Key', 'X-Request-ID']
}));

// Compression
app.use(compression());

// Request logging
app.use(morgan('combined', {
  stream: { write: message => logger.info(message.trim()) }
}));

// Body parsing
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Request ID middleware
app.use((req, res, next) => {
  req.id = req.headers['x-request-id'] || uuidv4();
  res.setHeader('X-Request-ID', req.id);
  req.startTime = Date.now();
  next();
});

// JWT verification middleware
const verifyToken = async (req, res, next) => {
  try {
    const token = req.headers.authorization?.replace('Bearer ', '');
    const apiKey = req.headers['x-api-key'];
    
    if (token) {
      // Verify JWT token
      const decoded = jwt.verify(token, process.env.JWT_SECRET || 'secret');
      req.user = decoded;
      req.userTier = await getUserTier(decoded.sub);
    } else if (apiKey) {
      // Verify API key
      const keyData = await verifyApiKey(apiKey);
      if (keyData) {
        req.user = { id: keyData.userId };
        req.userTier = keyData.tier;
      }
    }
    
    next();
  } catch (error) {
    logger.error('Auth verification error:', error);
    next(); // Continue without auth - individual services will handle authorization
  }
};

// Get user tier from cache or database
async function getUserTier(userId) {
  try {
    // Check Redis cache first if available
    if (redisAvailable && redis) {
      const cached = await redis.get(`user:${userId}:tier`);
      if (cached) return cached;
    }
    
    // Default to free tier if not found
    return 'free';
  } catch (error) {
    logger.error('Error getting user tier:', error);
    return 'free';
  }
}

// Verify API key
async function verifyApiKey(apiKey) {
  try {
    // Check Redis cache for API key if available
    if (redisAvailable && redis) {
      const cached = await redis.get(`apikey:${apiKey}`);
      if (cached) return JSON.parse(cached);
    }
    
    // Would normally check database here
    return null;
  } catch (error) {
    logger.error('Error verifying API key:', error);
    return null;
  }
}

// Dynamic rate limiter based on user tier
const createTierRateLimiter = (baseLimit) => {
  const config = {
    windowMs: 60 * 1000, // 1 minute
    max: (req, res) => {
      const tier = req.userTier || 'free';
      const limits = tierLimits[tier];
      
      if (limits.rpm === -1) return 999999; // Unlimited
      
      // Use base limit or tier limit, whichever is lower
      return Math.min(baseLimit, limits.rpm);
    },
    standardHeaders: true,
    legacyHeaders: false,
    keyGenerator: (req) => {
      // Rate limit by user ID or IP
      return req.user?.id || req.ip;
    },
    handler: (req, res) => {
      logger.warn(`Rate limit exceeded for ${req.user?.id || req.ip}`);
      res.status(429).json({
        error: 'Too many requests',
        message: 'Rate limit exceeded. Please upgrade your plan for higher limits.',
        retryAfter: res.getHeader('Retry-After')
      });
    }
  };
  
  // Use Redis store if available, otherwise use in-memory store
  if (redisAvailable && redis) {
    config.store = new RedisStore({
      client: redis,
      prefix: 'rl:',
    });
  }
  
  return rateLimit(config);
};

// Circuit breaker for service health
class CircuitBreaker {
  constructor(threshold = 5, timeout = 60000) {
    this.failures = new Map();
    this.threshold = threshold;
    this.timeout = timeout;
  }

  async call(serviceName, fn) {
    const state = this.getState(serviceName);
    
    if (state === 'open') {
      throw new Error(`Service ${serviceName} is currently unavailable`);
    }
    
    try {
      const result = await fn();
      this.onSuccess(serviceName);
      return result;
    } catch (error) {
      this.onFailure(serviceName);
      throw error;
    }
  }

  getState(serviceName) {
    const failures = this.failures.get(serviceName) || { count: 0, lastFailure: 0 };
    
    if (failures.count >= this.threshold) {
      if (Date.now() - failures.lastFailure < this.timeout) {
        return 'open';
      } else {
        // Reset after timeout
        this.failures.delete(serviceName);
        return 'closed';
      }
    }
    
    return 'closed';
  }

  onSuccess(serviceName) {
    this.failures.delete(serviceName);
  }

  onFailure(serviceName) {
    const failures = this.failures.get(serviceName) || { count: 0, lastFailure: 0 };
    failures.count++;
    failures.lastFailure = Date.now();
    this.failures.set(serviceName, failures);
  }
}

const circuitBreaker = new CircuitBreaker();

// Create proxy middleware for each service
Object.entries(services).forEach(([name, config]) => {
  const proxyMiddleware = createProxyMiddleware({
    target: config.url,
    changeOrigin: true,
    pathRewrite: {
      [`^/api/gateway/${name}`]: config.path
    },
    onProxyReq: (proxyReq, req, res) => {
      // Add tracking headers
      proxyReq.setHeader('X-Request-ID', req.id);
      proxyReq.setHeader('X-Gateway-Time', Date.now());
      
      // Forward user info
      if (req.user) {
        proxyReq.setHeader('X-User-ID', req.user.id);
        proxyReq.setHeader('X-User-Tier', req.userTier);
      }
      
      logger.info(`Proxying ${req.method} ${req.url} to ${name} service`);
    },
    onProxyRes: (proxyRes, req, res) => {
      // Add response headers
      const duration = Date.now() - req.startTime;
      res.setHeader('X-Response-Time', `${duration}ms`);
      
      // Log response
      logger.info(`Response from ${name}: ${proxyRes.statusCode} in ${duration}ms`);
      
      // Track usage for billing
      if (req.user) {
        trackUsage(req.user.id, name, req.method);
      }
    },
    onError: (err, req, res) => {
      logger.error(`Proxy error for ${name}:`, err);
      
      res.status(502).json({
        error: 'Service unavailable',
        message: `The ${name} service is currently unavailable`,
        requestId: req.id
      });
    }
  });

  // Apply middleware with rate limiting
  app.use(
    `/api/gateway/${name}`,
    verifyToken,
    createTierRateLimiter(config.rateLimit.max),
    (req, res, next) => {
      circuitBreaker.call(name, () => {
        return new Promise((resolve, reject) => {
          proxyMiddleware(req, res, (err) => {
            if (err) reject(err);
            else resolve();
          });
        });
      }).catch(next);
    }
  );
});

// Track API usage for billing
async function trackUsage(userId, service, method) {
  try {
    if (redisAvailable && redis) {
      const key = `usage:${userId}:${service}:${new Date().toISOString().split('T')[0]}`;
      await redis.hincrby(key, method, 1);
      await redis.expire(key, 86400 * 30); // Keep for 30 days
    }
  } catch (error) {
    logger.error('Error tracking usage:', error);
  }
}

// Health check endpoint
app.get('/health', async (req, res) => {
  const health = {
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    services: {}
  };

  // Check each service health
  for (const [name, config] of Object.entries(services)) {
    try {
      const axios = require('axios');
      const response = await axios.get(`${config.url}/health`, { timeout: 2000 });
      health.services[name] = {
        status: 'healthy',
        responseTime: response.headers['x-response-time']
      };
    } catch (error) {
      health.services[name] = {
        status: 'unhealthy',
        error: error.message
      };
    }
  }

  // Overall health status
  const unhealthyServices = Object.values(health.services).filter(s => s.status === 'unhealthy');
  if (unhealthyServices.length > 0) {
    health.status = 'degraded';
  }

  res.json(health);
});

// Service discovery endpoint
app.get('/api/gateway/services', (req, res) => {
  const serviceList = Object.entries(services).map(([name, config]) => ({
    name,
    path: `/api/gateway/${name}`,
    description: config.description,
    rateLimit: config.rateLimit,
    status: circuitBreaker.getState(name) === 'open' ? 'unavailable' : 'available'
  }));

  res.json({
    services: serviceList,
    tiers: tierLimits,
    timestamp: new Date().toISOString()
  });
});

// Usage statistics endpoint
app.get('/api/gateway/usage', verifyToken, async (req, res) => {
  if (!req.user) {
    return res.status(401).json({ error: 'Authentication required' });
  }

  try {
    const today = new Date().toISOString().split('T')[0];
    let usage = {};
    
    if (redisAvailable && redis) {
      const pattern = `usage:${req.user.id}:*:${today}`;
      const keys = await redis.keys(pattern);
      
      for (const key of keys) {
        const parts = key.split(':');
        const service = parts[2];
        const data = await redis.hgetall(key);
        usage[service] = data;
      }
    }

    res.json({
      userId: req.user.id,
      date: today,
      usage,
      tier: req.userTier,
      limits: tierLimits[req.userTier],
      redisAvailable
    });
  } catch (error) {
    logger.error('Error fetching usage:', error);
    res.status(500).json({ error: 'Failed to fetch usage data' });
  }
});

// Error handling middleware
app.use((err, req, res, next) => {
  logger.error('Unhandled error:', err);
  
  res.status(err.status || 500).json({
    error: 'Internal server error',
    message: process.env.NODE_ENV === 'development' ? err.message : 'An error occurred',
    requestId: req.id
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    error: 'Not found',
    message: 'The requested endpoint does not exist',
    availableServices: '/api/gateway/services'
  });
});

// Start server
const PORT = process.env.PORT || 4000;

app.listen(PORT, () => {
  logger.info(`
    ===================================
    🚀 Synapse API Gateway Started
    ===================================
    Port: ${PORT}
    Environment: ${process.env.NODE_ENV || 'development'}
    Services: ${Object.keys(services).length}
    Redis: ${redis.status}
    
    Available endpoints:
    - Health: http://localhost:${PORT}/health
    - Services: http://localhost:${PORT}/api/gateway/services
    - Usage: http://localhost:${PORT}/api/gateway/usage
    
    Service routes:
    ${Object.entries(services).map(([name, config]) => 
      `- ${name}: http://localhost:${PORT}/api/gateway/${name}`
    ).join('\n    ')}
    ===================================
  `);
});

// Graceful shutdown
process.on('SIGTERM', async () => {
  logger.info('SIGTERM received, shutting down gracefully...');
  
  // Close Redis connection if available
  if (redis) {
    try {
      await redis.quit();
    } catch (error) {
      logger.error('Error closing Redis connection:', error);
    }
  }
  
  // Exit
  process.exit(0);
});

module.exports = app;