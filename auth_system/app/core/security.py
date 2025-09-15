"""
Security utilities for authentication and authorization
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from jose import JWTError, jwt
from passlib.context import CryptContext
import secrets
import string
from app.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create a JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> Dict[str, Any]:
    """Decode and verify a JWT token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)

def generate_token(length: int = 32) -> str:
    """Generate a random token."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_api_key() -> str:
    """Generate a unique API key."""
    prefix = "sk_"  # Similar to Stripe's format
    if settings.DEBUG:
        prefix = "sk_test_"
    return prefix + secrets.token_urlsafe(32)

def generate_password_reset_token() -> str:
    """Generate a password reset token."""
    return secrets.token_urlsafe(32)

def generate_email_verification_token() -> str:
    """Generate an email verification token."""
    return secrets.token_urlsafe(32)

def verify_token_type(payload: Dict[str, Any], expected_type: str) -> bool:
    """Verify that a token has the expected type."""
    return payload.get("type") == expected_type

def create_token_data(user_id: int, username: str, scopes: List[str] = None) -> Dict[str, Any]:
    """Create token data payload."""
    return {
        "sub": str(user_id),
        "username": username,
        "scopes": scopes or []
    }

def hash_api_key(api_key: str) -> str:
    """Hash an API key for storage."""
    # Only store a hash of the API key
    return pwd_context.hash(api_key)

def verify_api_key(plain_key: str, hashed_key: str) -> bool:
    """Verify an API key against its hash."""
    return pwd_context.verify(plain_key, hashed_key)

def check_permission(required_scopes: List[str], user_scopes: List[str]) -> bool:
    """Check if user has required permissions."""
    if not required_scopes:
        return True
    
    # Admin has all permissions
    if "admin" in user_scopes:
        return True
    
    # Check if user has all required scopes
    return all(scope in user_scopes for scope in required_scopes)

def generate_session_token() -> str:
    """Generate a session token."""
    return secrets.token_urlsafe(32)

def mask_email(email: str) -> str:
    """Mask email for privacy (e.g., j***@example.com)."""
    parts = email.split('@')
    if len(parts) != 2:
        return email
    
    username = parts[0]
    domain = parts[1]
    
    if len(username) <= 2:
        masked_username = username[0] + '*' * (len(username) - 1)
    else:
        masked_username = username[0] + '*' * (len(username) - 2) + username[-1]
    
    return f"{masked_username}@{domain}"

def is_strong_password(password: str) -> bool:
    """Check if password meets strength requirements."""
    if len(password) < 8:
        return False
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
    
    return all([has_upper, has_lower, has_digit])