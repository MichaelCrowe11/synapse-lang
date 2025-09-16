"""
Pydantic Schemas for Request/Response Models
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, EmailStr, Field, validator


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    DEVELOPER = "developer"
    RESEARCHER = "researcher"

class SubscriptionTier(str, Enum):
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    QUANTUM = "quantum"

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: str | None = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)

    @validator("password")
    def validate_password(cls, v):
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(char.islower() for char in v):
            raise ValueError("Password must contain at least one lowercase letter")
        return v

class UserUpdate(BaseModel):
    full_name: str | None = None
    bio: str | None = None
    company: str | None = None
    location: str | None = None
    website: str | None = None
    preferences: dict[str, Any] | None = None

class UserInDB(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    role: UserRole
    stripe_customer_id: str | None
    subscription_tier: SubscriptionTier
    subscription_status: str
    created_at: datetime

    class Config:
        from_attributes = True

class UserResponse(UserInDB):
    """User response without sensitive data."""
    pass

# Authentication Schemas
class Token(BaseModel):
    access_token: str
    refresh_token: str | None
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: int | None = None
    username: str | None = None
    scopes: list[str] = []

class LoginRequest(BaseModel):
    username: str  # Can be username or email
    password: str

class RegisterRequest(UserCreate):
    accept_terms: bool = Field(..., description="User must accept terms of service")

class RegisterResponse(BaseModel):
    user: UserResponse
    message: str = "Registration successful. Please verify your email."

# Password Reset Schemas
class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)

# Email Verification
class EmailVerificationRequest(BaseModel):
    token: str

# API Key Schemas
class APIKeyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    scopes: list[str] | None = []
    expires_in_days: int | None = None

class APIKeyResponse(BaseModel):
    id: int
    key: str
    name: str
    scopes: list[str]
    is_active: bool
    created_at: datetime
    last_used: datetime | None

    class Config:
        from_attributes = True

# Usage Tracking Schemas
class UsageStats(BaseModel):
    api_calls: int
    quantum_simulations: int
    gpu_hours: float
    storage_gb: float
    period_start: datetime
    period_end: datetime

class UsageLimits(BaseModel):
    tier: SubscriptionTier
    api_calls_limit: int
    quantum_simulations_limit: int
    gpu_hours_limit: float
    storage_gb_limit: float

class UsageResponse(BaseModel):
    current_usage: UsageStats
    limits: UsageLimits
    percentage_used: dict[str, float]

# Subscription Schemas
class SubscriptionUpdate(BaseModel):
    tier: SubscriptionTier
    payment_method_id: str | None

class SubscriptionResponse(BaseModel):
    tier: SubscriptionTier
    status: str
    stripe_subscription_id: str | None
    current_period_end: datetime | None
    cancel_at_period_end: bool = False

# Session Schemas
class SessionResponse(BaseModel):
    id: int
    ip_address: str | None
    user_agent: str | None
    device_type: str | None
    created_at: datetime
    last_activity: datetime
    is_active: bool

# Error Schemas
class ErrorResponse(BaseModel):
    detail: str
    code: str | None = None
    field: str | None = None

class ValidationErrorResponse(BaseModel):
    detail: list[dict[str, Any]]

# Health Check
class HealthResponse(BaseModel):
    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str
    services: dict[str, str]

# Additional User Schemas
class UserList(BaseModel):
    users: list[UserResponse]
    total: int
    skip: int
    limit: int

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)

# Additional API Key Schemas
class APIKeyList(BaseModel):
    api_keys: list[APIKeyResponse]
    total: int
    skip: int
    limit: int

class APIKeyWithSecret(APIKeyResponse):
    message: str
    expires_at: datetime | None = None

# Subscription Schemas
class CheckoutSessionRequest(BaseModel):
    tier: str
    billing_cycle: str = "monthly"
    success_url: str
    cancel_url: str

class CheckoutSessionResponse(BaseModel):
    checkout_url: str
    session_id: str
    expires_at: datetime

class PortalSessionRequest(BaseModel):
    return_url: str

class PortalSessionResponse(BaseModel):
    portal_url: str
    session_id: str

class SubscriptionInfo(BaseModel):
    user_id: int
    subscription_tier: str
    subscription_status: str
    stripe_customer_id: str | None
    stripe_subscription_id: str | None
    billing_period_start: datetime | None
    billing_period_end: datetime | None
    cancel_at_period_end: bool = False
    limits: dict[str, Any]
    stripe_details: dict[str, Any] | None

class Invoice(BaseModel):
    id: str
    amount: float
    currency: str
    status: str
    created_at: datetime
    period_start: datetime
    period_end: datetime
    invoice_pdf: str | None
    hosted_invoice_url: str | None

class BillingHistory(BaseModel):
    invoices: list[Invoice]
    has_more: bool
