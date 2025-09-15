"""
FastAPI Dependencies for Authentication and Authorization
"""

from fastapi import Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from sqlalchemy.orm import Session
from jose import JWTError
from typing import Optional, List
from datetime import datetime

from app.core.database import get_db
from app.core.security import decode_token, verify_api_key
from app.core.config import settings
from app.models import User, APIKey
from app.schemas import TokenData

# Security schemes
bearer_scheme = HTTPBearer()
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get the current authenticated user from JWT token."""
    
    token = credentials.credentials
    
    # Decode token
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check token type
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user

async def get_current_verified_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Get current verified user."""
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email address"
        )
    return current_user

async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Get current admin user."""
    if not current_user.is_superuser and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

async def get_api_key_user(
    api_key: Optional[str] = Security(api_key_header),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get user from API key."""
    if not api_key:
        return None
    
    # Find API key in database
    api_key_obj = db.query(APIKey).filter(
        APIKey.key == api_key,
        APIKey.is_active == True
    ).first()
    
    if not api_key_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    # Check if API key has expired
    if api_key_obj.expires_at and api_key_obj.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key has expired"
        )
    
    # Update last used timestamp
    api_key_obj.last_used = datetime.utcnow()
    db.commit()
    
    # Get associated user
    user = api_key_obj.user
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return user

async def get_current_user_or_api_key(
    bearer_user: Optional[User] = None,
    api_key_user: Optional[User] = Depends(get_api_key_user),
    credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get user from either JWT token or API key."""
    
    # Try API key first
    if api_key_user:
        return api_key_user
    
    # Then try bearer token
    if credentials:
        return await get_current_user(credentials, db)
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No authentication credentials provided"
    )

class RateLimiter:
    """Rate limiting dependency."""
    
    def __init__(self, calls: int = 10, period: int = 60):
        self.calls = calls
        self.period = period
        self.cache = {}  # In production, use Redis
    
    async def __call__(self, user: User = Depends(get_current_active_user)):
        """Check rate limit for user."""
        if not settings.RATE_LIMIT_ENABLED:
            return
        
        # Get user's tier limits
        tier_limits = settings.TIER_LIMITS.get(user.subscription_tier.value, {})
        
        # Override with tier-specific limits if available
        if user.subscription_tier != "free":
            self.calls = tier_limits.get("api_calls", self.calls) // 60  # Per minute
        
        # Simple in-memory rate limiting (use Redis in production)
        now = datetime.utcnow()
        user_key = f"rate_limit:{user.id}"
        
        if user_key in self.cache:
            calls, reset_time = self.cache[user_key]
            if now < reset_time:
                if calls >= self.calls:
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail=f"Rate limit exceeded. Try again in {(reset_time - now).seconds} seconds"
                    )
                self.cache[user_key] = (calls + 1, reset_time)
            else:
                self.cache[user_key] = (1, now + timedelta(seconds=self.period))
        else:
            self.cache[user_key] = (1, now + timedelta(seconds=self.period))

def check_subscription_tier(required_tier: str):
    """Check if user has required subscription tier."""
    tier_hierarchy = {
        "free": 0,
        "starter": 1,
        "professional": 2,
        "enterprise": 3,
        "quantum": 4
    }
    
    async def tier_checker(user: User = Depends(get_current_verified_user)):
        user_level = tier_hierarchy.get(user.subscription_tier.value, 0)
        required_level = tier_hierarchy.get(required_tier, 0)
        
        if user_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This feature requires {required_tier} tier or higher"
            )
        
        return user
    
    return tier_checker

def check_scopes(required_scopes: List[str]):
    """Check if user has required scopes."""
    
    async def scope_checker(user: User = Depends(get_current_active_user)):
        # Admin has all scopes
        if user.is_superuser or user.role == "admin":
            return user
        
        # Check user scopes (would need to be implemented in User model)
        # For now, just return user
        return user
    
    return scope_checker