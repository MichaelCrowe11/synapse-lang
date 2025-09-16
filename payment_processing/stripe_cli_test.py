#!/usr/bin/env python3
"""
Stripe CLI Testing Tool for Synapse Platform

Test Stripe integration using the Stripe CLI.
"""

import os
import subprocess
import sys

from stripe_integration import (
    PricingTier,
    create_checkout_link,
    create_payment_processor,
)


def run_stripe_cli_command(command: str) -> str:
    """Run a Stripe CLI command."""
    stripe_exe = os.path.expanduser("~/bin/stripe.exe")

    if not os.path.exists(stripe_exe):
        print("Error: Stripe CLI not found at ~/bin/stripe.exe")
        print("Please ensure Stripe CLI is installed correctly.")
        return None

    try:
        result = subprocess.run(
            f"{stripe_exe} {command}",
            shell=True,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            return result.stdout
        else:
            print(f"Error: {result.stderr}")
            return None

    except Exception as e:
        print(f"Failed to run Stripe CLI: {e}")
        return None

def test_stripe_connection():
    """Test Stripe API connection."""
    print("Testing Stripe Connection...")
    print("-" * 40)

    output = run_stripe_cli_command("--version")
    if output:
        print(f"Stripe CLI Version: {output.strip()}")

    # Test API connection (requires login)
    print("\nChecking Stripe account status...")
    output = run_stripe_cli_command("config --list")
    if output:
        print("Stripe CLI is configured.")
    else:
        print("Please login to Stripe CLI using: ~/bin/stripe.exe login")

def forward_webhooks(port: int = 8000):
    """Forward Stripe webhooks to local server."""
    print(f"Forwarding Stripe webhooks to http://localhost:{port}/stripe/webhook")
    print("Press Ctrl+C to stop...")

    command = f"listen --forward-to http://localhost:{port}/stripe/webhook"
    run_stripe_cli_command(command)

def create_test_customer():
    """Create a test customer."""
    print("Creating Test Customer...")
    print("-" * 40)

    processor = create_payment_processor(test_mode=True)

    customer = processor.create_customer(
        email="test@synapse-platform.com",
        name="Test User",
        metadata={
            "platform": "synapse",
            "test": "true"
        }
    )

    print(f"Customer created: {customer['id']}")
    print(f"Email: {customer['email']}")

    return customer

def test_subscription_flow():
    """Test the complete subscription flow."""
    print("Testing Subscription Flow...")
    print("-" * 40)

    # Test each pricing tier
    tiers = [
        PricingTier.STARTER,
        PricingTier.PRO,
        PricingTier.ENTERPRISE
    ]

    processor = create_payment_processor(test_mode=True)

    for tier in tiers:
        print(f"\nTesting {tier.value} tier:")

        # Create customer
        customer = processor.create_customer(
            email=f"{tier.value}@test.com",
            name=f"Test {tier.value.title()}"
        )

        # Create subscription
        subscription = processor.create_subscription(
            customer["id"],
            tier,
            "monthly"
        )

        print(f"  Customer: {customer['id']}")
        print(f"  Subscription: {subscription['id']}")
        print(f"  Status: {subscription['status']}")
        print(f"  Price: ${subscription['plan']['price_monthly']}/month")

def test_checkout_session():
    """Test checkout session creation."""
    print("Testing Checkout Session...")
    print("-" * 40)

    session = create_checkout_link(
        tier="pro",
        success_url="https://synapse-platform.com/success",
        cancel_url="https://synapse-platform.com/cancel"
    )

    print(f"Checkout URL: {session['url']}")
    print("\nTo test the checkout flow:")
    print("1. Open the checkout URL in a browser")
    print("2. Use test card: 4242 4242 4242 4242")
    print("3. Any future expiry date and any CVC")

def test_usage_tracking():
    """Test usage tracking system."""
    print("Testing Usage Tracking...")
    print("-" * 40)

    from stripe_integration import PricingTier, UsageTracker

    tracker = UsageTracker()
    customer_id = "test_customer_123"

    # Track various usage
    print("Tracking usage events...")
    for i in range(100):
        tracker.track_api_call(customer_id, f"/api/endpoint_{i}")

    for i in range(5):
        tracker.track_quantum_simulation(customer_id, circuit_depth=10)

    tracker.track_gpu_usage(customer_id, 2.5)

    # Get usage summary
    usage = tracker.get_usage_summary(customer_id)
    print(f"\nUsage Summary for {customer_id}:")
    print(f"  API Calls: {usage['api_calls']}")
    print(f"  Quantum Simulations: {usage['quantum_simulations']}")
    print(f"  GPU Hours: {usage['gpu_hours']}")

    # Check limits for different plans
    processor = create_payment_processor()

    for tier in [PricingTier.FREE, PricingTier.STARTER, PricingTier.PRO]:
        plan = processor.pricing_plans[tier]
        exceeded = tracker.check_limits(customer_id, plan)

        print(f"\n{tier.value.title()} Plan Limits:")
        for metric, is_exceeded in exceeded.items():
            status = "EXCEEDED" if is_exceeded else "OK"
            limit = plan.limits[metric]
            limit_str = "Unlimited" if limit == -1 else str(limit)
            print(f"  {metric}: {status} (limit: {limit_str})")

def display_pricing_table():
    """Display pricing table."""
    print("\nSynapse Platform Pricing")
    print("=" * 80)

    processor = create_payment_processor()

    for tier, plan in processor.pricing_plans.items():
        print(f"\n{plan.name} ({tier.value})")
        print("-" * 40)
        print(f"Monthly: ${plan.price_monthly}")
        print(f"Yearly: ${plan.price_yearly} (save ${plan.price_monthly * 12 - plan.price_yearly})")
        print("\nFeatures:")
        for feature in plan.features:
            print(f"  - {feature}")
        print("\nLimits:")
        for metric, limit in plan.limits.items():
            limit_str = "Unlimited" if limit == -1 else str(limit)
            print(f"  {metric}: {limit_str}")

def main():
    """Main CLI interface."""
    print("Synapse Platform - Stripe Integration Test Tool")
    print("=" * 60)

    if len(sys.argv) < 2:
        print("\nUsage: python stripe_cli_test.py <command>")
        print("\nCommands:")
        print("  test        - Test Stripe connection")
        print("  webhooks    - Forward webhooks to local server")
        print("  customer    - Create test customer")
        print("  subscribe   - Test subscription flow")
        print("  checkout    - Test checkout session")
        print("  usage       - Test usage tracking")
        print("  pricing     - Display pricing table")
        print("  all         - Run all tests")
        return

    command = sys.argv[1]

    if command == "test":
        test_stripe_connection()
    elif command == "webhooks":
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
        forward_webhooks(port)
    elif command == "customer":
        create_test_customer()
    elif command == "subscribe":
        test_subscription_flow()
    elif command == "checkout":
        test_checkout_session()
    elif command == "usage":
        test_usage_tracking()
    elif command == "pricing":
        display_pricing_table()
    elif command == "all":
        test_stripe_connection()
        print("\n" + "=" * 60)
        display_pricing_table()
        print("\n" + "=" * 60)
        create_test_customer()
        print("\n" + "=" * 60)
        test_subscription_flow()
        print("\n" + "=" * 60)
        test_checkout_session()
        print("\n" + "=" * 60)
        test_usage_tracking()
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
