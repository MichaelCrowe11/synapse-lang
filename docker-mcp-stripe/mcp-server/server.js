/**
 * MCP Server with Stripe Integration
 * Provides Model Context Protocol server with Stripe payment capabilities
 */

const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const { WebSocketServer } = require('ws');
const { createServer } = require('http');
const Stripe = require('stripe');
require('dotenv').config();

// Initialize Stripe
const stripe = Stripe(process.env.STRIPE_API_KEY);

// Create Express app
const app = express();
const server = createServer(app);

// Middleware
app.use(helmet());
app.use(cors({
  origin: process.env.CORS_ORIGINS?.split(',') || ['http://localhost:3000', 'http://localhost:8001'],
  credentials: true
}));
app.use(express.json());
app.use(express.raw({ type: 'application/webhook' }));

// MCP Protocol Implementation
class MCPStripeServer {
  constructor() {
    this.clients = new Set();
    this.tools = {
      'stripe-create-customer': this.createCustomer.bind(this),
      'stripe-create-subscription': this.createSubscription.bind(this),
      'stripe-create-checkout': this.createCheckoutSession.bind(this),
      'stripe-cancel-subscription': this.cancelSubscription.bind(this),
      'stripe-get-customer': this.getCustomer.bind(this),
      'stripe-list-subscriptions': this.listSubscriptions.bind(this),
      'stripe-create-portal': this.createPortalSession.bind(this),
      'stripe-webhook-handler': this.handleWebhook.bind(this)
    };
  }

  // Stripe Customer Management
  async createCustomer(params) {
    try {
      const { email, name, metadata } = params;
      
      const customer = await stripe.customers.create({
        email,
        name,
        metadata: {
          platform: 'synapse',
          ...metadata
        }
      });

      return {
        success: true,
        customer: {
          id: customer.id,
          email: customer.email,
          name: customer.name,
          created: customer.created
        }
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  // Stripe Subscription Management
  async createSubscription(params) {
    try {
      const { customerId, priceId, paymentMethodId } = params;

      if (paymentMethodId) {
        await stripe.paymentMethods.attach(paymentMethodId, {
          customer: customerId
        });

        await stripe.customers.update(customerId, {
          invoice_settings: {
            default_payment_method: paymentMethodId
          }
        });
      }

      const subscription = await stripe.subscriptions.create({
        customer: customerId,
        items: [{ price: priceId }],
        expand: ['latest_invoice.payment_intent']
      });

      return {
        success: true,
        subscription: {
          id: subscription.id,
          status: subscription.status,
          current_period_end: subscription.current_period_end,
          latest_invoice: subscription.latest_invoice
        }
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  // Stripe Checkout Session
  async createCheckoutSession(params) {
    try {
      const { 
        customerId, 
        priceId, 
        successUrl, 
        cancelUrl,
        mode = 'subscription'
      } = params;

      const sessionConfig = {
        customer: customerId,
        payment_method_types: ['card'],
        mode,
        success_url: successUrl,
        cancel_url: cancelUrl,
        metadata: {
          platform: 'synapse',
          timestamp: new Date().toISOString()
        }
      };

      if (mode === 'subscription') {
        sessionConfig.line_items = [{
          price: priceId,
          quantity: 1
        }];
      } else {
        sessionConfig.line_items = [{
          price_data: {
            currency: 'usd',
            product_data: {
              name: params.productName || 'Synapse Platform Access'
            },
            unit_amount: params.amount
          },
          quantity: 1
        }];
      }

      const session = await stripe.checkout.sessions.create(sessionConfig);

      return {
        success: true,
        session: {
          id: session.id,
          url: session.url,
          expires_at: session.expires_at
        }
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  // Cancel Subscription
  async cancelSubscription(params) {
    try {
      const { subscriptionId, cancelAtPeriodEnd = true } = params;

      const subscription = await stripe.subscriptions.update(subscriptionId, {
        cancel_at_period_end: cancelAtPeriodEnd
      });

      return {
        success: true,
        subscription: {
          id: subscription.id,
          status: subscription.status,
          cancel_at_period_end: subscription.cancel_at_period_end
        }
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  // Get Customer
  async getCustomer(params) {
    try {
      const { customerId } = params;
      
      const customer = await stripe.customers.retrieve(customerId);

      return {
        success: true,
        customer: {
          id: customer.id,
          email: customer.email,
          name: customer.name,
          created: customer.created,
          subscriptions: customer.subscriptions?.data || []
        }
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  // List Subscriptions
  async listSubscriptions(params) {
    try {
      const { customerId, limit = 10 } = params;
      
      const subscriptions = await stripe.subscriptions.list({
        customer: customerId,
        limit
      });

      return {
        success: true,
        subscriptions: subscriptions.data.map(sub => ({
          id: sub.id,
          status: sub.status,
          current_period_end: sub.current_period_end,
          items: sub.items.data
        }))
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  // Create Customer Portal Session
  async createPortalSession(params) {
    try {
      const { customerId, returnUrl } = params;
      
      const session = await stripe.billingPortal.sessions.create({
        customer: customerId,
        return_url: returnUrl
      });

      return {
        success: true,
        session: {
          id: session.id,
          url: session.url
        }
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  // Handle Stripe Webhooks
  async handleWebhook(params) {
    try {
      const { payload, signature } = params;
      
      const event = stripe.webhooks.constructEvent(
        payload,
        signature,
        process.env.STRIPE_WEBHOOK_SECRET
      );

      // Process webhook event
      switch (event.type) {
        case 'customer.subscription.created':
          console.log('Subscription created:', event.data.object.id);
          break;
        case 'customer.subscription.updated':
          console.log('Subscription updated:', event.data.object.id);
          break;
        case 'customer.subscription.deleted':
          console.log('Subscription deleted:', event.data.object.id);
          break;
        case 'invoice.payment_succeeded':
          console.log('Payment succeeded:', event.data.object.id);
          break;
        case 'invoice.payment_failed':
          console.log('Payment failed:', event.data.object.id);
          break;
        default:
          console.log('Unhandled event type:', event.type);
      }

      return {
        success: true,
        event: {
          id: event.id,
          type: event.type,
          processed: true
        }
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  // Process MCP request
  async processRequest(request) {
    const { method, params } = request;

    if (!this.tools[method]) {
      return {
        error: {
          code: -32601,
          message: `Method not found: ${method}`
        }
      };
    }

    try {
      const result = await this.tools[method](params);
      return { result };
    } catch (error) {
      return {
        error: {
          code: -32603,
          message: error.message
        }
      };
    }
  }
}

// Initialize MCP server
const mcpServer = new MCPStripeServer();

// WebSocket server for MCP protocol
const wss = new WebSocketServer({ server, path: '/mcp' });

wss.on('connection', (ws) => {
  console.log('MCP client connected');
  mcpServer.clients.add(ws);

  ws.on('message', async (data) => {
    try {
      const request = JSON.parse(data.toString());
      const response = await mcpServer.processRequest(request);
      
      ws.send(JSON.stringify({
        jsonrpc: '2.0',
        id: request.id,
        ...response
      }));
    } catch (error) {
      ws.send(JSON.stringify({
        jsonrpc: '2.0',
        id: request?.id || null,
        error: {
          code: -32700,
          message: 'Parse error'
        }
      }));
    }
  });

  ws.on('close', () => {
    console.log('MCP client disconnected');
    mcpServer.clients.delete(ws);
  });

  // Send server capabilities
  ws.send(JSON.stringify({
    jsonrpc: '2.0',
    method: 'initialize',
    params: {
      protocolVersion: '2024-11-05',
      capabilities: {
        tools: Object.keys(mcpServer.tools).map(name => ({
          name,
          description: `Stripe ${name.replace('stripe-', '').replace('-', ' ')}`
        }))
      },
      serverInfo: {
        name: 'mcp-stripe-server',
        version: '1.0.0'
      }
    }
  }));
});

// REST API endpoints
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    mcp: {
      connected_clients: mcpServer.clients.size,
      available_tools: Object.keys(mcpServer.tools).length
    },
    stripe: {
      configured: !!process.env.STRIPE_API_KEY,
      webhook_secret: !!process.env.STRIPE_WEBHOOK_SECRET
    }
  });
});

app.get('/tools', (req, res) => {
  res.json({
    tools: Object.keys(mcpServer.tools),
    count: Object.keys(mcpServer.tools).length
  });
});

// Stripe webhook endpoint
app.post('/stripe/webhook', async (req, res) => {
  const sig = req.headers['stripe-signature'];
  
  try {
    const result = await mcpServer.handleWebhook({
      payload: req.body,
      signature: sig
    });
    
    if (result.success) {
      res.json({ received: true });
    } else {
      res.status(400).json({ error: result.error });
    }
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

// Start server
const PORT = process.env.MCP_SERVER_PORT || 3000;

server.listen(PORT, () => {
  console.log(`🚀 MCP Stripe Server running on port ${PORT}`);
  console.log(`📡 WebSocket endpoint: ws://localhost:${PORT}/mcp`);
  console.log(`🏥 Health check: http://localhost:${PORT}/health`);
  console.log(`🔧 Available tools: ${Object.keys(mcpServer.tools).length}`);
  console.log(`💳 Stripe integration: ${process.env.STRIPE_API_KEY ? 'Enabled' : 'Disabled'}`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('Shutting down MCP Stripe Server...');
  server.close(() => {
    console.log('Server closed');
    process.exit(0);
  });
});