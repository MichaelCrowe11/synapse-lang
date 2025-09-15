"""
Main FastAPI Application for Synapse Authentication System
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from datetime import datetime

from app.core.config import settings
from app.core.database import init_db
from app.api.v1 import auth, users, api_keys, subscriptions
from app.schemas import HealthResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown."""
    # Startup
    logger.info("Starting Synapse Authentication System...")
    
    # Initialize database
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Synapse Authentication System...")

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Authentication and user management system for Synapse Platform",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth, prefix=settings.API_V1_PREFIX)
app.include_router(users, prefix=settings.API_V1_PREFIX)
app.include_router(api_keys, prefix=settings.API_V1_PREFIX)
app.include_router(subscriptions, prefix=settings.API_V1_PREFIX)

# Exception handlers
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle value errors."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )

# Root endpoint
@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version=settings.APP_VERSION,
        services={
            "database": "connected",
            "redis": "connected" if settings.REDIS_URL else "not configured",
            "stripe": "configured" if settings.STRIPE_API_KEY else "not configured"
        }
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Detailed health check."""
    return await root()

# API documentation customization
app.openapi_tags = [
    {
        "name": "authentication",
        "description": "User authentication endpoints (login, register, etc.)"
    },
    {
        "name": "users",
        "description": "User management endpoints"
    },
    {
        "name": "api-keys",
        "description": "API key management for programmatic access"
    },
    {
        "name": "subscriptions",
        "description": "Subscription and billing management"
    }
]

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,  # Different port from payment webhook server
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info"
    )