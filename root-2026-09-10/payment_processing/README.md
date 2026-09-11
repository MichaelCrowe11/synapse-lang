# Synapse Platform - Payment Processing System

## Overview

Complete Stripe payment integration for the Synapse Language platform, supporting subscriptions, usage-based billing, and one-time payments.

## Features

- **Subscription Management**: Multiple pricing tiers from Free to Quantum Research
- **Usage Tracking**: Monitor API calls, quantum simulations, and GPU hours
- **Webhook Handling**: Real-time payment event processing
- **Checkout Sessions**: Stripe Checkout integration for seamless payments
- **Metered Billing**: Usage-based pricing for resource consumption

## Installation

### 1. Install Stripe CLI

The Stripe CLI is already installed at `~/bin/stripe.exe`

To verify installation:
```bash
~/bin/stripe.exe --version
```

### 2. Configure Stripe API Keys

1. Copy the environment template:
```bash
cp .env.example .env
```

2. Edit `.env` and add your Stripe keys from [Stripe Dashboard](https://dashboard.stripe.com/apikeys)

### 3. Login to Stripe CLI

```bash
~/bin/stripe.exe login
```

Follow the prompts to authenticate with your Stripe account.

## Pricing Tiers

| Tier | Monthly | Yearly | Key Features |
|------|---------|--------|--------------|
| **Free** | $0 | $0 | 1,000 API calls, 2 quantum simulations/day |
| **Starter** | $29 | $290 | 10,000 API calls, 100 quantum simulations/day, 5 GPU hours |
| **Pro** | $99 | $990 | 100,000 API calls, Unlimited quantum, 50 GPU hours, AutoML |
| **Enterprise** | $499 | $4,990 | Unlimited API calls, 500 GPU hours, Distributed training |
| **Quantum** | $1,999 | $19,990 | Real quantum hardware, Unlimited resources, Research support |

## Usage

### Testing the Integration

Run all tests:
```bash
python stripe_cli_test.py all
```

Individual tests:
```bash
python stripe_cli_test.py test       # Test Stripe connection
python stripe_cli_test.py pricing    # Display pricing table
python stripe_cli_test.py customer   # Create test customer
python stripe_cli_test.py subscribe  # Test subscription flow
python stripe_cli_test.py checkout   # Test checkout session
python stripe_cli_test.py usage      # Test usage tracking
```

### Starting the Webhook Server

```bash
python webhook_server.py
```

The server will run on port 8000 by default. Access:
- Webhook endpoint: `http://localhost:8000/stripe/webhook`
- Health check: `http://localhost:8000/health`

### Forwarding Webhooks with Stripe CLI

In a separate terminal, forward Stripe webhooks to your local server:

```bash
~/bin/stripe.exe listen --forward-to http://localhost:8000/stripe/webhook
```

Or use the test tool:
```bash
python stripe_cli_test.py webhooks
```

## API Integration

### Creating a Subscription

```python
from payment_processing.stripe_integration import process_new_subscription

result = process_new_subscription(
    email="user@example.com",
    name="John Doe",
    tier="pro"  # 'starter', 'pro', 'enterprise', or 'quantum'
)

print(f"Customer ID: {result['customer']['id']}")
print(f"Subscription ID: {result['subscription']['id']}")
```

### Creating a Checkout Session

```python
from payment_processing.stripe_integration import create_checkout_link

session = create_checkout_link(
    tier='pro',
    success_url='https://yoursite.com/success',
    cancel_url='https://yoursite.com/cancel'
)

# Redirect user to session['url']
```

### Tracking Usage

```python
from payment_processing.stripe_integration import UsageTracker

tracker = UsageTracker()

# Track API calls
tracker.track_api_call(customer_id, '/api/neural-network/train')

# Track quantum simulations
tracker.track_quantum_simulation(customer_id, circuit_depth=10)

# Track GPU usage
tracker.track_gpu_usage(customer_id, hours=2.5)

# Check limits
usage = tracker.get_usage_summary(customer_id)
exceeded = tracker.check_limits(customer_id, plan)
```

## Webhook Events

The system handles the following Stripe webhook events:

- `customer.subscription.created` - Provision access for new subscriptions
- `customer.subscription.updated` - Update access levels
- `customer.subscription.deleted` - Revoke access on cancellation
- `payment_intent.succeeded` - Confirm successful payments
- `payment_intent.failed` - Handle failed payments
- `invoice.payment_succeeded` - Process successful invoice payments
- `invoice.payment_failed` - Handle failed invoice payments

## Testing with Test Cards

Use these test card numbers in Stripe Checkout:

- **Success**: 4242 4242 4242 4242
- **Decline**: 4000 0000 0000 0002
- **Requires Authentication**: 4000 0025 0000 3155

Use any future expiry date and any 3-digit CVC.

## Project Structure

```
payment_processing/
├── stripe_integration.py    # Core payment processing logic
├── webhook_server.py        # HTTP server for webhook handling
├── stripe_cli_test.py      # CLI testing tool
├── .env.example            # Environment variable template
└── README.md              # This file
```

## Security Best Practices

1. **Never commit `.env` files** - Keep API keys secure
2. **Verify webhook signatures** - Ensure webhooks are from Stripe
3. **Use test mode** - Always test with test keys first
4. **Implement rate limiting** - Protect against abuse
5. **Log all transactions** - Maintain audit trail
6. **Use HTTPS in production** - Secure all communications

## Production Deployment

1. Set environment to production:
```bash
STRIPE_ENV=live
```

2. Use production API keys from Stripe Dashboard

3. Configure webhook endpoint in Stripe:
   - Go to [Stripe Webhooks](https://dashboard.stripe.com/webhooks)
   - Add endpoint: `https://your-domain.com/stripe/webhook`
   - Select events to listen for

4. Deploy webhook server with HTTPS (use nginx/Apache reverse proxy)

5. Implement proper logging and monitoring

## Support

For issues or questions:
- Stripe Documentation: https://stripe.com/docs
- Stripe CLI Reference: https://stripe.com/docs/cli
- Platform Support: support@synapse-platform.com

## License

Copyright (c) 2024 Synapse Language Platform. All rights reserved.