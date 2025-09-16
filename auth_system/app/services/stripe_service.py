"""
Stripe Integration Service
"""

from datetime import datetime
from typing import Any

import stripe
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import SubscriptionTier, User

# Configure Stripe
stripe.api_key = settings.STRIPE_API_KEY

async def create_stripe_customer(email: str, name: str | None = None) -> dict[str, Any]:
    """Create a Stripe customer."""
    try:
        customer = stripe.Customer.create(
            email=email,
            name=name,
            metadata={
                "platform": "synapse",
                "created_via": "auth_system"
            }
        )
        return customer
    except stripe.error.StripeError as e:
        print(f"Stripe error creating customer: {e}")
        # Return a mock customer for development
        return {
            "id": f"cus_dev_{datetime.utcnow().timestamp()}",
            "email": email,
            "name": name
        }

async def create_subscription(
    user: User,
    price_id: str,
    payment_method_id: str | None = None,
    db: Session = None
) -> dict[str, Any]:
    """Create a Stripe subscription for a user."""
    try:
        # Attach payment method if provided
        if payment_method_id:
            stripe.PaymentMethod.attach(
                payment_method_id,
                customer=user.stripe_customer_id
            )

            # Set as default payment method
            stripe.Customer.modify(
                user.stripe_customer_id,
                invoice_settings={
                    "default_payment_method": payment_method_id
                }
            )

        # Create subscription
        subscription = stripe.Subscription.create(
            customer=user.stripe_customer_id,
            items=[{"price": price_id}],
            expand=["latest_invoice.payment_intent"]
        )

        # Update user subscription info
        if db:
            user.stripe_subscription_id = subscription.id
            user.subscription_status = subscription.status

            # Map price to tier
            tier = get_tier_from_price_id(price_id)
            if tier:
                user.subscription_tier = tier

            db.commit()

        return subscription

    except stripe.error.StripeError as e:
        print(f"Stripe error creating subscription: {e}")
        raise

async def cancel_subscription(user: User, db: Session) -> dict[str, Any]:
    """Cancel a user's subscription."""
    try:
        if not user.stripe_subscription_id:
            return {"status": "no_subscription"}

        # Cancel at period end
        subscription = stripe.Subscription.modify(
            user.stripe_subscription_id,
            cancel_at_period_end=True
        )

        # Update user status
        user.subscription_status = "canceling"
        db.commit()

        return subscription

    except stripe.error.StripeError as e:
        print(f"Stripe error canceling subscription: {e}")
        raise

async def update_subscription(
    user: User,
    new_price_id: str,
    db: Session
) -> dict[str, Any]:
    """Update a user's subscription to a different plan."""
    try:
        if not user.stripe_subscription_id:
            # Create new subscription
            return await create_subscription(user, new_price_id, db=db)

        # Get current subscription
        subscription = stripe.Subscription.retrieve(user.stripe_subscription_id)

        # Update subscription item
        stripe.Subscription.modify(
            user.stripe_subscription_id,
            items=[{
                "id": subscription["items"]["data"][0].id,
                "price": new_price_id
            }],
            proration_behavior="create_prorations"
        )

        # Update user tier
        tier = get_tier_from_price_id(new_price_id)
        if tier:
            user.subscription_tier = tier
            db.commit()

        return subscription

    except stripe.error.StripeError as e:
        print(f"Stripe error updating subscription: {e}")
        raise

async def create_checkout_session(
    user: User,
    price_id: str,
    success_url: str,
    cancel_url: str
) -> dict[str, Any]:
    """Create a Stripe Checkout session."""
    try:
        session = stripe.checkout.Session.create(
            customer=user.stripe_customer_id,
            payment_method_types=["card"],
            mode="subscription",
            line_items=[{
                "price": price_id,
                "quantity": 1
            }],
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "user_id": str(user.id),
                "username": user.username
            }
        )
        return session

    except stripe.error.StripeError as e:
        print(f"Stripe error creating checkout session: {e}")
        raise

async def create_customer_portal_session(
    user: User,
    return_url: str
) -> dict[str, Any]:
    """Create a Stripe Customer Portal session."""
    try:
        session = stripe.billing_portal.Session.create(
            customer=user.stripe_customer_id,
            return_url=return_url
        )
        return session

    except stripe.error.StripeError as e:
        print(f"Stripe error creating portal session: {e}")
        raise

async def get_subscription_info(user: User) -> dict[str, Any] | None:
    """Get current subscription information."""
    try:
        if not user.stripe_subscription_id:
            return None

        subscription = stripe.Subscription.retrieve(
            user.stripe_subscription_id,
            expand=["default_payment_method"]
        )

        return {
            "id": subscription.id,
            "status": subscription.status,
            "current_period_start": datetime.fromtimestamp(subscription.current_period_start),
            "current_period_end": datetime.fromtimestamp(subscription.current_period_end),
            "cancel_at_period_end": subscription.cancel_at_period_end,
            "canceled_at": datetime.fromtimestamp(subscription.canceled_at) if subscription.canceled_at else None,
            "items": subscription.items.data
        }

    except stripe.error.StripeError as e:
        print(f"Stripe error getting subscription: {e}")
        return None

async def record_usage(
    user: User,
    quantity: int,
    metric: str,
    timestamp: int | None = None
) -> dict[str, Any]:
    """Record usage for metered billing."""
    try:
        if not user.stripe_subscription_id:
            return {"status": "no_subscription"}

        # Get subscription
        subscription = stripe.Subscription.retrieve(user.stripe_subscription_id)

        # Find metered price item
        metered_item = None
        for item in subscription.items.data:
            if item.price.recurring.usage_type == "metered":
                metered_item = item
                break

        if not metered_item:
            return {"status": "no_metered_items"}

        # Create usage record
        usage_record = stripe.SubscriptionItem.create_usage_record(
            metered_item.id,
            quantity=quantity,
            timestamp=timestamp or int(datetime.utcnow().timestamp()),
            action="increment"
        )

        return usage_record

    except stripe.error.StripeError as e:
        print(f"Stripe error recording usage: {e}")
        raise

def get_tier_from_price_id(price_id: str) -> SubscriptionTier | None:
    """Map Stripe price ID to subscription tier."""
    price_tier_map = {
        settings.STRIPE_PRICE_ID_STARTER_MONTHLY: SubscriptionTier.STARTER,
        settings.STRIPE_PRICE_ID_STARTER_YEARLY: SubscriptionTier.STARTER,
        settings.STRIPE_PRICE_ID_PRO_MONTHLY: SubscriptionTier.PROFESSIONAL,
        settings.STRIPE_PRICE_ID_PRO_YEARLY: SubscriptionTier.PROFESSIONAL,
        settings.STRIPE_PRICE_ID_ENTERPRISE_MONTHLY: SubscriptionTier.ENTERPRISE,
        settings.STRIPE_PRICE_ID_ENTERPRISE_YEARLY: SubscriptionTier.ENTERPRISE,
        settings.STRIPE_PRICE_ID_QUANTUM_MONTHLY: SubscriptionTier.QUANTUM,
        settings.STRIPE_PRICE_ID_QUANTUM_YEARLY: SubscriptionTier.QUANTUM,
    }

    return price_tier_map.get(price_id)

def get_price_id_for_tier(tier: SubscriptionTier, billing_cycle: str = "monthly") -> str | None:
    """Get Stripe price ID for a subscription tier."""
    if billing_cycle == "monthly":
        tier_price_map = {
            SubscriptionTier.STARTER: settings.STRIPE_PRICE_ID_STARTER_MONTHLY,
            SubscriptionTier.PROFESSIONAL: settings.STRIPE_PRICE_ID_PRO_MONTHLY,
            SubscriptionTier.ENTERPRISE: settings.STRIPE_PRICE_ID_ENTERPRISE_MONTHLY,
            SubscriptionTier.QUANTUM: settings.STRIPE_PRICE_ID_QUANTUM_MONTHLY,
        }
    else:  # yearly
        tier_price_map = {
            SubscriptionTier.STARTER: settings.STRIPE_PRICE_ID_STARTER_YEARLY,
            SubscriptionTier.PROFESSIONAL: settings.STRIPE_PRICE_ID_PRO_YEARLY,
            SubscriptionTier.ENTERPRISE: settings.STRIPE_PRICE_ID_ENTERPRISE_YEARLY,
            SubscriptionTier.QUANTUM: settings.STRIPE_PRICE_ID_QUANTUM_YEARLY,
        }

    return tier_price_map.get(tier)
