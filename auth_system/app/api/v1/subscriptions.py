"""
Subscription and Billing Management Endpoints
"""

from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import RateLimiter, get_current_verified_user
from app.core.config import settings
from app.core.database import get_db
from app.models import SubscriptionTier, User
from app.schemas import (
    BillingHistory,
    CheckoutSessionRequest,
    CheckoutSessionResponse,
    Invoice,
    PortalSessionRequest,
    PortalSessionResponse,
    SubscriptionInfo,
    SubscriptionUpdate,
)
from app.services import stripe_service

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])

# Rate limiter
rate_limiter = RateLimiter(calls=20, period=60)

@router.get("/current", response_model=SubscriptionInfo)
async def get_current_subscription(
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """Get current user's subscription information."""

    # Get subscription info from Stripe
    stripe_info = await stripe_service.get_subscription_info(current_user)

    # Get tier limits
    tier_limits = settings.TIER_LIMITS.get(current_user.subscription_tier.value, {})

    return SubscriptionInfo(
        user_id=current_user.id,
        subscription_tier=current_user.subscription_tier.value,
        subscription_status=current_user.subscription_status,
        stripe_customer_id=current_user.stripe_customer_id,
        stripe_subscription_id=current_user.stripe_subscription_id,
        billing_period_start=current_user.billing_period_start,
        billing_period_end=current_user.billing_period_end,
        cancel_at_period_end=stripe_info.get("cancel_at_period_end", False) if stripe_info else False,
        limits=tier_limits,
        stripe_details=stripe_info
    )

@router.get("/plans")
async def get_available_plans():
    """Get all available subscription plans."""

    plans = []

    for tier in ["starter", "professional", "enterprise", "quantum"]:
        tier_limits = settings.TIER_LIMITS.get(tier, {})

        # Get pricing
        monthly_price_id = getattr(settings, f"STRIPE_PRICE_ID_{tier.upper()}_MONTHLY", None)
        yearly_price_id = getattr(settings, f"STRIPE_PRICE_ID_{tier.upper()}_YEARLY", None)

        plan = {
            "tier": tier,
            "name": tier.replace("_", " ").title(),
            "limits": tier_limits,
            "pricing": {
                "monthly": {
                    "price": tier_limits.get("monthly_price", 0),
                    "price_id": monthly_price_id
                },
                "yearly": {
                    "price": tier_limits.get("yearly_price", 0),
                    "price_id": yearly_price_id,
                    "savings": tier_limits.get("yearly_savings", 0)
                }
            },
            "features": get_tier_features(tier)
        }

        plans.append(plan)

    return {"plans": plans}

@router.post("/checkout", response_model=CheckoutSessionResponse)
async def create_checkout_session(
    request: CheckoutSessionRequest,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
    _: None = Depends(rate_limiter)
):
    """Create a Stripe Checkout session for subscription."""

    # Get price ID for the requested tier and billing cycle
    price_id = stripe_service.get_price_id_for_tier(
        SubscriptionTier[request.tier.upper()],
        request.billing_cycle
    )

    if not price_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid tier or billing cycle"
        )

    # Create checkout session
    session = await stripe_service.create_checkout_session(
        user=current_user,
        price_id=price_id,
        success_url=request.success_url,
        cancel_url=request.cancel_url
    )

    return CheckoutSessionResponse(
        checkout_url=session.url,
        session_id=session.id,
        expires_at=datetime.fromtimestamp(session.expires_at)
    )

@router.post("/portal", response_model=PortalSessionResponse)
async def create_portal_session(
    request: PortalSessionRequest,
    current_user: User = Depends(get_current_verified_user),
    _: None = Depends(rate_limiter)
):
    """Create a Stripe Customer Portal session."""

    if not current_user.stripe_customer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No billing account found"
        )

    # Create portal session
    session = await stripe_service.create_customer_portal_session(
        user=current_user,
        return_url=request.return_url
    )

    return PortalSessionResponse(
        portal_url=session.url,
        session_id=session.id
    )

@router.post("/upgrade", response_model=SubscriptionInfo)
async def upgrade_subscription(
    request: SubscriptionUpdate,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
    _: None = Depends(rate_limiter)
):
    """Upgrade or downgrade subscription."""

    # Check if upgrading or downgrading
    tier_hierarchy = {
        "free": 0,
        "starter": 1,
        "professional": 2,
        "enterprise": 3,
        "quantum": 4
    }

    current_level = tier_hierarchy.get(current_user.subscription_tier.value, 0)
    new_level = tier_hierarchy.get(request.tier, 0)

    if current_level == new_level:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already on this subscription tier"
        )

    # Get price ID
    price_id = stripe_service.get_price_id_for_tier(
        SubscriptionTier[request.tier.upper()],
        request.billing_cycle
    )

    if not price_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid tier or billing cycle"
        )

    # Update subscription
    await stripe_service.update_subscription(
        user=current_user,
        new_price_id=price_id,
        db=db
    )

    # Return updated subscription info
    return await get_current_subscription(current_user, db)

@router.post("/cancel")
async def cancel_subscription(
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
    _: None = Depends(rate_limiter)
):
    """Cancel subscription at period end."""

    if not current_user.stripe_subscription_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active subscription found"
        )

    # Cancel subscription
    result = await stripe_service.cancel_subscription(current_user, db)

    return {
        "message": "Subscription will be canceled at the end of the billing period",
        "cancel_at": result.get("cancel_at_period_end")
    }

@router.post("/reactivate")
async def reactivate_subscription(
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db),
    _: None = Depends(rate_limiter)
):
    """Reactivate a canceled subscription."""

    if not current_user.stripe_subscription_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No subscription found"
        )

    if current_user.subscription_status != "canceling":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subscription is not scheduled for cancellation"
        )

    # Reactivate via Stripe
    import stripe
    stripe.api_key = settings.STRIPE_API_KEY

    try:
        stripe.Subscription.modify(
            current_user.stripe_subscription_id,
            cancel_at_period_end=False
        )

        # Update user status
        current_user.subscription_status = "active"
        db.commit()

        return {"message": "Subscription reactivated successfully"}

    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/invoices", response_model=BillingHistory)
async def get_billing_history(
    limit: int = 10,
    current_user: User = Depends(get_current_verified_user)
):
    """Get billing history and invoices."""

    if not current_user.stripe_customer_id:
        return BillingHistory(invoices=[], has_more=False)

    import stripe
    stripe.api_key = settings.STRIPE_API_KEY

    try:
        # Get invoices from Stripe
        invoices = stripe.Invoice.list(
            customer=current_user.stripe_customer_id,
            limit=limit
        )

        invoice_list = []
        for inv in invoices.data:
            invoice_list.append(Invoice(
                id=inv.id,
                amount=inv.amount_paid / 100,  # Convert from cents
                currency=inv.currency,
                status=inv.status,
                created_at=datetime.fromtimestamp(inv.created),
                period_start=datetime.fromtimestamp(inv.period_start),
                period_end=datetime.fromtimestamp(inv.period_end),
                invoice_pdf=inv.invoice_pdf,
                hosted_invoice_url=inv.hosted_invoice_url
            ))

        return BillingHistory(
            invoices=invoice_list,
            has_more=invoices.has_more
        )

    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/usage/report")
async def report_usage(
    metric: str,
    quantity: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """Report usage for metered billing."""

    # Record usage in database
    from app.models import UsageRecord

    usage = UsageRecord(
        user_id=current_user.id,
        metric=metric,
        quantity=quantity
    )

    db.add(usage)
    db.commit()

    # Report to Stripe if on metered plan
    if current_user.subscription_tier in [SubscriptionTier.ENTERPRISE, SubscriptionTier.QUANTUM]:
        background_tasks.add_task(
            stripe_service.record_usage,
            current_user,
            quantity,
            metric
        )

    return {"message": "Usage recorded", "metric": metric, "quantity": quantity}

def get_tier_features(tier: str) -> list:
    """Get features for a subscription tier."""

    features_map = {
        "starter": [
            "10,000 API calls per month",
            "100 compute minutes",
            "5 GB storage",
            "Email support",
            "Basic analytics",
            "2 API keys"
        ],
        "professional": [
            "100,000 API calls per month",
            "1,000 compute minutes",
            "50 GB storage",
            "Priority email support",
            "Advanced analytics",
            "10 API keys",
            "Custom integrations",
            "SLA guarantee"
        ],
        "enterprise": [
            "1,000,000 API calls per month",
            "10,000 compute minutes",
            "500 GB storage",
            "24/7 phone & email support",
            "Enterprise analytics",
            "Unlimited API keys",
            "Custom contracts",
            "Dedicated account manager",
            "99.9% uptime SLA"
        ],
        "quantum": [
            "Unlimited API calls",
            "Unlimited compute minutes",
            "Unlimited storage",
            "White-glove support",
            "Custom analytics",
            "Unlimited everything",
            "Quantum acceleration",
            "Direct engineering support",
            "99.99% uptime SLA",
            "Custom deployment options"
        ]
    }

    return features_map.get(tier, [])
