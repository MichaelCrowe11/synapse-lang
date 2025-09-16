"""
Application Configuration
"""

import secrets

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Application
    APP_NAME: str = "Synapse Platform Auth"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # API
    API_V1_PREFIX: str = "/api/v1"

    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS: int = 24
    EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS: int = 48

    # CORS
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8000",
        "https://synapse-platform.com"
    ]

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/synapse_auth"
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10

    # Redis (for session storage and caching)
    REDIS_URL: str = "redis://localhost:6379/0"

    # Stripe
    STRIPE_API_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_PRICE_ID_STARTER_MONTHLY: str = ""
    STRIPE_PRICE_ID_STARTER_YEARLY: str = ""
    STRIPE_PRICE_ID_PRO_MONTHLY: str = ""
    STRIPE_PRICE_ID_PRO_YEARLY: str = ""
    STRIPE_PRICE_ID_ENTERPRISE_MONTHLY: str = ""
    STRIPE_PRICE_ID_ENTERPRISE_YEARLY: str = ""
    STRIPE_PRICE_ID_QUANTUM_MONTHLY: str = ""
    STRIPE_PRICE_ID_QUANTUM_YEARLY: str = ""

    # Email (for notifications)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM_NAME: str = "Synapse Platform"
    EMAIL_FROM_ADDRESS: str = "noreply@synapse-platform.com"

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60

    # Usage Limits by Tier
    TIER_LIMITS: dict = {
        "free": {
            "api_calls": 1000,
            "quantum_simulations": 60,
            "gpu_hours": 0,
            "storage_gb": 1
        },
        "starter": {
            "api_calls": 10000,
            "quantum_simulations": 3000,
            "gpu_hours": 5,
            "storage_gb": 10
        },
        "professional": {
            "api_calls": 100000,
            "quantum_simulations": -1,  # Unlimited
            "gpu_hours": 50,
            "storage_gb": 100
        },
        "enterprise": {
            "api_calls": -1,
            "quantum_simulations": -1,
            "gpu_hours": 500,
            "storage_gb": 1000
        },
        "quantum": {
            "api_calls": -1,
            "quantum_simulations": -1,
            "gpu_hours": -1,
            "storage_gb": -1
        }
    }

    # OAuth Providers (optional)
    GOOGLE_CLIENT_ID: str | None = None
    GOOGLE_CLIENT_SECRET: str | None = None
    GITHUB_CLIENT_ID: str | None = None
    GITHUB_CLIENT_SECRET: str | None = None

    # Frontend URLs
    FRONTEND_URL: str = "http://localhost:3000"
    PASSWORD_RESET_URL: str = "http://localhost:3000/reset-password"
    EMAIL_VERIFICATION_URL: str = "http://localhost:3000/verify-email"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
