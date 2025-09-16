"""
API Key Management Endpoints
"""

import hashlib
import secrets
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import RateLimiter, get_current_verified_user
from app.core.config import settings
from app.core.database import get_db
from app.models import APIKey, User
from app.schemas import APIKeyCreate, APIKeyList, APIKeyResponse, APIKeyWithSecret

router = APIRouter(prefix="/api-keys", tags=["api-keys"])

# Rate limiter
rate_limiter = RateLimiter(calls=10, period=60)

def generate_api_key(prefix: str = "sk") -> tuple[str, str]:
    """Generate a new API key and its hash."""
    # Generate random key
    secrets.token_bytes(32)
    key_suffix = secrets.token_urlsafe(32)

    # Create the full key
    full_key = f"{prefix}_{key_suffix}"

    # Hash the key for storage
    key_hash = hashlib.sha256(full_key.encode()).hexdigest()

    return full_key, key_hash

@router.get("/", response_model=APIKeyList)
async def list_api_keys(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    is_active: bool | None = None,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """List current user's API keys."""

    query = db.query(APIKey).filter(APIKey.user_id == current_user.id)

    if is_active is not None:
        query = query.filter(APIKey.is_active == is_active)

    # Get total count
    total = query.count()

    # Apply pagination
    api_keys = query.offset(skip).limit(limit).all()

    # Don't return the actual key values
    sanitized_keys = []
    for key in api_keys:
        response = APIKeyResponse.from_orm(key)
        # Show only last 4 characters of the key
        if key.key:
            response.key = f"...{key.key[-4:]}"
        sanitized_keys.append(response)

    return APIKeyList(
        api_keys=sanitized_keys,
        total=total,
        skip=skip,
        limit=limit
    )

@router.post("/", response_model=APIKeyWithSecret)
async def create_api_key(
    key_data: APIKeyCreate,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
    _: None = Depends(rate_limiter)
):
    """Create a new API key."""

    # Check user's API key limit based on subscription tier
    tier_limits = settings.TIER_LIMITS.get(current_user.subscription_tier.value, {})
    max_keys = tier_limits.get("api_keys", 1)

    # Count existing active keys
    active_keys = db.query(APIKey).filter(
        APIKey.user_id == current_user.id,
        APIKey.is_active
    ).count()

    if active_keys >= max_keys:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"API key limit reached. Your {current_user.subscription_tier.value} tier allows {max_keys} keys."
        )

    # Generate new API key
    prefix = "sk_test" if settings.DEBUG else "sk_live"
    full_key, key_hash = generate_api_key(prefix)

    # Calculate expiration
    expires_at = None
    if key_data.expires_in_days:
        expires_at = datetime.utcnow() + timedelta(days=key_data.expires_in_days)

    # Create API key record
    api_key = APIKey(
        user_id=current_user.id,
        name=key_data.name,
        key=key_hash,  # Store the hash
        scopes=key_data.scopes or [],
        expires_at=expires_at
    )

    db.add(api_key)
    db.commit()
    db.refresh(api_key)

    # Return the full key only once
    return APIKeyWithSecret(
        id=api_key.id,
        name=api_key.name,
        key=full_key,  # Return the actual key
        scopes=api_key.scopes,
        created_at=api_key.created_at,
        expires_at=api_key.expires_at,
        last_used=api_key.last_used,
        is_active=api_key.is_active,
        message="Store this key securely. It will not be shown again."
    )

@router.get("/{key_id}", response_model=APIKeyResponse)
async def get_api_key(
    key_id: int,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """Get API key details."""

    api_key = db.query(APIKey).filter(
        APIKey.id == key_id,
        APIKey.user_id == current_user.id
    ).first()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )

    response = APIKeyResponse.from_orm(api_key)
    # Sanitize key display
    if api_key.key:
        response.key = f"...{api_key.key[-4:]}"

    return response

@router.patch("/{key_id}", response_model=APIKeyResponse)
async def update_api_key(
    key_id: int,
    update_data: dict,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """Update API key details."""

    api_key = db.query(APIKey).filter(
        APIKey.id == key_id,
        APIKey.user_id == current_user.id
    ).first()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )

    # Update allowed fields
    if "name" in update_data:
        api_key.name = update_data["name"]

    if "scopes" in update_data:
        api_key.scopes = update_data["scopes"]

    db.commit()
    db.refresh(api_key)

    response = APIKeyResponse.from_orm(api_key)
    response.key = f"...{api_key.key[-4:]}"

    return response

@router.post("/{key_id}/regenerate", response_model=APIKeyWithSecret)
async def regenerate_api_key(
    key_id: int,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
    _: None = Depends(rate_limiter)
):
    """Regenerate an API key."""

    api_key = db.query(APIKey).filter(
        APIKey.id == key_id,
        APIKey.user_id == current_user.id
    ).first()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )

    # Generate new key
    prefix = "sk_test" if settings.DEBUG else "sk_live"
    full_key, key_hash = generate_api_key(prefix)

    # Update the key
    api_key.key = key_hash
    api_key.created_at = datetime.utcnow()
    api_key.last_used = None

    db.commit()
    db.refresh(api_key)

    return APIKeyWithSecret(
        id=api_key.id,
        name=api_key.name,
        key=full_key,
        scopes=api_key.scopes,
        created_at=api_key.created_at,
        expires_at=api_key.expires_at,
        last_used=api_key.last_used,
        is_active=api_key.is_active,
        message="New key generated. Store it securely."
    )

@router.post("/{key_id}/revoke")
async def revoke_api_key(
    key_id: int,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """Revoke an API key."""

    api_key = db.query(APIKey).filter(
        APIKey.id == key_id,
        APIKey.user_id == current_user.id
    ).first()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )

    api_key.is_active = False
    db.commit()

    return {"message": f"API key '{api_key.name}' has been revoked"}

@router.post("/{key_id}/activate")
async def activate_api_key(
    key_id: int,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """Reactivate a revoked API key."""

    api_key = db.query(APIKey).filter(
        APIKey.id == key_id,
        APIKey.user_id == current_user.id
    ).first()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )

    # Check if expired
    if api_key.expires_at and api_key.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot activate expired API key"
        )

    api_key.is_active = True
    db.commit()

    return {"message": f"API key '{api_key.name}' has been activated"}

@router.delete("/{key_id}")
async def delete_api_key(
    key_id: int,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """Delete an API key permanently."""

    api_key = db.query(APIKey).filter(
        APIKey.id == key_id,
        APIKey.user_id == current_user.id
    ).first()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )

    db.delete(api_key)
    db.commit()

    return {"message": f"API key '{api_key.name}' has been deleted"}

@router.get("/validate/{key}")
async def validate_api_key(
    key: str,
    db: Session = Depends(get_db)
):
    """Validate an API key (public endpoint)."""

    # Hash the provided key
    key_hash = hashlib.sha256(key.encode()).hexdigest()

    # Find the API key
    api_key = db.query(APIKey).filter(
        APIKey.key == key_hash,
        APIKey.is_active
    ).first()

    if not api_key:
        return {"valid": False, "message": "Invalid API key"}

    # Check expiration
    if api_key.expires_at and api_key.expires_at < datetime.utcnow():
        return {"valid": False, "message": "API key has expired"}

    # Update last used
    api_key.last_used = datetime.utcnow()
    db.commit()

    return {
        "valid": True,
        "scopes": api_key.scopes,
        "user_id": api_key.user_id
    }
