"""
User Management API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models import User
from app.schemas import (
    UserResponse, UserUpdate, UserList,
    ChangePasswordRequest, UsageStats
)
from app.api.dependencies import (
    get_current_user, get_current_verified_user,
    get_current_admin_user, RateLimiter
)
from app.core.security import verify_password, get_password_hash

router = APIRouter(prefix="/users", tags=["users"])

# Rate limiter instance
rate_limiter = RateLimiter(calls=100, period=60)

@router.get("/", response_model=UserList, dependencies=[Depends(get_current_admin_user)])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    subscription_tier: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """List all users (admin only)."""
    
    query = db.query(User)
    
    # Apply filters
    if search:
        query = query.filter(
            (User.email.contains(search)) | 
            (User.username.contains(search)) |
            (User.full_name.contains(search))
        )
    
    if subscription_tier:
        query = query.filter(User.subscription_tier == subscription_tier)
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    users = query.offset(skip).limit(limit).all()
    
    return UserList(
        users=users,
        total=total,
        skip=skip,
        limit=limit
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current user profile."""
    return current_user

@router.get("/me/usage", response_model=UsageStats)
async def get_usage_stats(
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """Get current user's usage statistics."""
    
    # Calculate usage stats
    from sqlalchemy import func
    from app.models import UsageRecord
    
    # Get current billing period
    now = datetime.utcnow()
    if current_user.billing_period_start:
        period_start = current_user.billing_period_start
    else:
        period_start = datetime(now.year, now.month, 1)
    
    # Query usage records
    usage = db.query(
        func.sum(UsageRecord.api_calls).label("api_calls"),
        func.sum(UsageRecord.compute_minutes).label("compute_minutes"),
        func.sum(UsageRecord.storage_gb).label("storage_gb"),
        func.sum(UsageRecord.bandwidth_gb).label("bandwidth_gb")
    ).filter(
        UsageRecord.user_id == current_user.id,
        UsageRecord.created_at >= period_start
    ).first()
    
    return UsageStats(
        user_id=current_user.id,
        billing_period_start=period_start,
        billing_period_end=current_user.billing_period_end,
        api_calls=usage.api_calls or 0,
        compute_minutes=usage.compute_minutes or 0,
        storage_gb=usage.storage_gb or 0,
        bandwidth_gb=usage.bandwidth_gb or 0,
        subscription_tier=current_user.subscription_tier.value
    )

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get user by ID (admin only)."""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
    _: None = Depends(rate_limiter)
):
    """Update current user profile."""
    
    # Update allowed fields
    if update_data.full_name is not None:
        current_user.full_name = update_data.full_name
    
    if update_data.bio is not None:
        current_user.bio = update_data.bio
    
    if update_data.company is not None:
        current_user.company = update_data.company
    
    if update_data.location is not None:
        current_user.location = update_data.location
    
    if update_data.website is not None:
        current_user.website = update_data.website
    
    if update_data.preferences is not None:
        current_user.preferences = update_data.preferences
    
    db.commit()
    db.refresh(current_user)
    
    return current_user

@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    update_data: UserUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update user by ID (admin only)."""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update fields
    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    return user

@router.post("/me/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change current user's password."""
    
    # Verify current password
    if not verify_password(request.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # Update password
    current_user.hashed_password = get_password_hash(request.new_password)
    
    # Invalidate all sessions
    from app.models import UserSession
    db.query(UserSession).filter(
        UserSession.user_id == current_user.id
    ).update({"is_active": False})
    
    db.commit()
    
    return {"message": "Password changed successfully"}

@router.delete("/me")
async def delete_current_user(
    confirmation: str = Query(..., description="Type 'DELETE' to confirm"),
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """Delete current user account."""
    
    if confirmation != "DELETE":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid confirmation. Type 'DELETE' to confirm account deletion."
        )
    
    # Cancel Stripe subscription if exists
    if current_user.stripe_subscription_id:
        from app.services.stripe_service import cancel_subscription
        try:
            await cancel_subscription(current_user, db)
        except Exception as e:
            print(f"Error canceling subscription: {e}")
    
    # Soft delete user
    current_user.is_active = False
    current_user.deleted_at = datetime.utcnow()
    
    # Invalidate all sessions
    from app.models import UserSession
    db.query(UserSession).filter(
        UserSession.user_id == current_user.id
    ).update({"is_active": False})
    
    db.commit()
    
    return {"message": "Account deleted successfully"}

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Delete user by ID (admin only)."""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent deleting self
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account via admin endpoint"
        )
    
    # Soft delete
    user.is_active = False
    user.deleted_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": f"User {user.username} deleted"}

@router.post("/{user_id}/activate")
async def activate_user(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Activate user account (admin only)."""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = True
    user.deleted_at = None
    
    db.commit()
    
    return {"message": f"User {user.username} activated"}

@router.post("/{user_id}/deactivate")
async def deactivate_user(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Deactivate user account (admin only)."""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = False
    
    db.commit()
    
    return {"message": f"User {user.username} deactivated"}