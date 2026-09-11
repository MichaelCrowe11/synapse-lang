"""
Authentication API Endpoints
"""

from datetime import datetime, timedelta

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_email_verification_token,
    generate_password_reset_token,
    get_password_hash,
    verify_password,
)
from app.models import EmailVerification, PasswordReset, User, UserSession
from app.schemas import (
    EmailVerificationRequest,
    PasswordResetConfirm,
    PasswordResetRequest,
    RegisterRequest,
    RegisterResponse,
    Token,
    UserResponse,
)
from app.services.email import send_password_reset_email, send_verification_email
from app.services.stripe_service import create_stripe_customer

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=RegisterResponse)
async def register(
    request: RegisterRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Register a new user."""

    # Check if user exists
    existing_user = db.query(User).filter(
        (User.email == request.email) | (User.username == request.username)
    ).first()

    if existing_user:
        if existing_user.email == request.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )

    # Create Stripe customer
    stripe_customer = await create_stripe_customer(request.email, request.full_name)

    # Create new user
    user = User(
        email=request.email,
        username=request.username,
        full_name=request.full_name,
        hashed_password=get_password_hash(request.password),
        stripe_customer_id=stripe_customer["id"],
        subscription_tier="free",
        subscription_status="active"
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # Create email verification token
    verification_token = generate_email_verification_token()
    verification = EmailVerification(
        email=user.email,
        token=verification_token,
        expires_at=datetime.utcnow() + timedelta(hours=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS)
    )
    db.add(verification)
    db.commit()

    # Send verification email in background
    background_tasks.add_task(
        send_verification_email,
        user.email,
        user.full_name or user.username,
        verification_token
    )

    return RegisterResponse(
        user=UserResponse.from_orm(user),
        message="Registration successful. Please check your email to verify your account."
    )

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login with username/email and password."""

    # Find user by username or email
    user = db.query(User).filter(
        (User.username == form_data.username) | (User.email == form_data.username)
    ).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )

    # Create tokens
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username}
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id), "username": user.username}
    )

    # Create session record
    session = UserSession(
        user_id=user.id,
        session_token=access_token,
        refresh_token=refresh_token,
        expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    db.add(session)

    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )

@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token."""

    # Decode refresh token
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    # Get user
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == int(user_id)).first()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )

    # Create new access token
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username}
    )

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Logout current user (invalidate session)."""

    # Invalidate all user sessions
    db.query(UserSession).filter(
        UserSession.user_id == current_user.id,
        UserSession.is_active
    ).update({"is_active": False})

    db.commit()

    return {"message": "Successfully logged out"}

@router.post("/verify-email")
async def verify_email(
    request: EmailVerificationRequest,
    db: Session = Depends(get_db)
):
    """Verify email address with token."""

    # Find verification record
    verification = db.query(EmailVerification).filter(
        EmailVerification.token == request.token,
        not EmailVerification.verified
    ).first()

    if not verification:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )

    # Check expiration
    if verification.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification token has expired"
        )

    # Mark email as verified
    verification.verified = True

    # Update user
    user = db.query(User).filter(User.email == verification.email).first()
    if user:
        user.is_verified = True

    db.commit()

    return {"message": "Email successfully verified"}

@router.post("/resend-verification")
async def resend_verification(
    email: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Resend email verification."""

    # Find user
    user = db.query(User).filter(User.email == email).first()

    if not user:
        # Don't reveal if email exists
        return {"message": "If the email exists, a verification link has been sent"}

    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified"
        )

    # Create new verification token
    verification_token = generate_email_verification_token()
    verification = EmailVerification(
        email=user.email,
        token=verification_token,
        expires_at=datetime.utcnow() + timedelta(hours=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS)
    )
    db.add(verification)
    db.commit()

    # Send email
    background_tasks.add_task(
        send_verification_email,
        user.email,
        user.full_name or user.username,
        verification_token
    )

    return {"message": "Verification email sent"}

@router.post("/forgot-password")
async def forgot_password(
    request: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Request password reset."""

    # Find user
    user = db.query(User).filter(User.email == request.email).first()

    if not user:
        # Don't reveal if email exists
        return {"message": "If the email exists, a password reset link has been sent"}

    # Create reset token
    reset_token = generate_password_reset_token()
    reset = PasswordReset(
        email=user.email,
        token=reset_token,
        expires_at=datetime.utcnow() + timedelta(hours=settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS)
    )
    db.add(reset)
    db.commit()

    # Send email
    background_tasks.add_task(
        send_password_reset_email,
        user.email,
        user.full_name or user.username,
        reset_token
    )

    return {"message": "Password reset email sent"}

@router.post("/reset-password")
async def reset_password(
    request: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """Reset password with token."""

    # Find reset record
    reset = db.query(PasswordReset).filter(
        PasswordReset.token == request.token,
        not PasswordReset.used
    ).first()

    if not reset:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )

    # Check expiration
    if reset.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has expired"
        )

    # Update user password
    user = db.query(User).filter(User.email == reset.email).first()
    if user:
        user.hashed_password = get_password_hash(request.new_password)
        reset.used = True

        # Invalidate all sessions
        db.query(UserSession).filter(
            UserSession.user_id == user.id
        ).update({"is_active": False})

        db.commit()

    return {"message": "Password successfully reset"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information."""
    return current_user
