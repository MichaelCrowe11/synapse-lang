# Docker MCP Server with Stripe Integration

A containerized Model Context Protocol (MCP) server with full Stripe payment integration for the Synapse quantum computing platform.

## Features

- **MCP Protocol Support**: Full WebSocket-based MCP server implementation
- **Stripe Integration**: Complete payment processing capabilities
- **Authentication**: JWT-based user authentication system
- **Webhook Handling**: Real-time Stripe event processing
- **Multi-Service Architecture**: Authentication, payments, and MCP in one container

## Quick Start

### 1. Build and Run with Docker Compose

```bash
cd docker-mcp-stripe
docker-compose up --build
```

### 2. Run with Docker

```bash
# Build the image
docker build -t synapse-mcp-stripe .

# Run the container
docker run -p 3000:3000 -p 8000:8000 -p 8001:8001 --env-file .env synapse-mcp-stripe
```

### 3. Manual Setup

```bash
# Install dependencies
cd mcp-server && npm install
cd .. && pip install -r requirements.txt

# Start services
chmod +x start.sh
./start.sh
```

## Services

Once running, the following services will be available:

- **MCP Server**: `http://localhost:3000`
- **Authentication API**: `http://localhost:8001` 
- **Stripe Webhooks**: `http://localhost:8000`
- **WebSocket MCP**: `ws://localhost:3000/mcp`

## MCP Tools Available

The server provides these Stripe-integrated MCP tools:

### Customer Management
- `stripe-create-customer` - Create new Stripe customers
- `stripe-get-customer` - Retrieve customer details

### Subscription Management  
- `stripe-create-subscription` - Create subscriptions
- `stripe-cancel-subscription` - Cancel subscriptions
- `stripe-list-subscriptions` - List customer subscriptions

### Payment Processing
- `stripe-create-checkout` - Create Stripe Checkout sessions
- `stripe-create-portal` - Create customer portal sessions

### Webhook Processing
- `stripe-webhook-handler` - Process Stripe webhook events

## Configuration

### Environment Variables

Key configuration options in `.env`:

```env
# Stripe (using your CROWE LOGIC account)
STRIPE_API_KEY=sk_test_51RkUYkQ6s74Bq3bW...
STRIPE_WEBHOOK_SECRET=whsec_...

# Server Settings
MCP_SERVER_PORT=3000
CORS_ORIGINS=http://localhost:3000,http://localhost:8001

# Platform URLs
PLATFORM_URL=http://localhost:3000
SUCCESS_URL=http://localhost:3000/payment/success
CANCEL_URL=http://localhost:3000/payment/cancel
```

### Stripe Price IDs

The server is pre-configured with your Synapse pricing tiers:
- **Starter**: Monthly/Yearly options
- **Professional**: Monthly/Yearly options  
- **Enterprise**: Monthly/Yearly options
- **Quantum**: Monthly/Yearly options

## Usage Examples

### Connect to MCP Server

```javascript
const ws = new WebSocket('ws://localhost:3000/mcp');

ws.on('message', (data) => {
  const response = JSON.parse(data);
  console.log('MCP Response:', response);
});

// Create a customer
ws.send(JSON.stringify({
  jsonrpc: '2.0',
  id: 1,
  method: 'stripe-create-customer',
  params: {
    email: 'user@example.com',
    name: 'John Doe',
    metadata: { source: 'synapse-platform' }
  }
}));
```

### Create Subscription

```javascript
ws.send(JSON.stringify({
  jsonrpc: '2.0', 
  id: 2,
  method: 'stripe-create-subscription',
  params: {
    customerId: 'cus_...',
    priceId: 'price_1S6U8fQ6s74Bq3bW9I2Ff3qW', // Starter Monthly
    paymentMethodId: 'pm_...'
  }
}));
```

### Create Checkout Session

```javascript
ws.send(JSON.stringify({
  jsonrpc: '2.0',
  id: 3,
  method: 'stripe-create-checkout',
  params: {
    customerId: 'cus_...',
    priceId: 'price_1S6U9QQ6s74Bq3bWN63Ooijg', // Professional Monthly
    successUrl: 'http://localhost:3000/success',
    cancelUrl: 'http://localhost:3000/cancel'
  }
}));
```

## Health Checks

Check server status:

```bash
curl http://localhost:3000/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2025-09-12T11:00:00.000Z",
  "mcp": {
    "connected_clients": 2,
    "available_tools": 8
  },
  "stripe": {
    "configured": true,
    "webhook_secret": true
  }
}
```

## Integration with Synapse Platform

This MCP server integrates seamlessly with:

- **Authentication System** (port 8001) - User management and JWT tokens
- **Stripe Webhooks** (port 8000) - Real-time payment event processing  
- **Quantum Computing Platform** - Usage tracking and billing enforcement

## Development

### Adding New MCP Tools

1. Add tool method to `MCPStripeServer` class in `server.js`
2. Register tool in constructor's `this.tools` object
3. Implement error handling and response formatting

### Testing

```bash
# Test MCP connection
node test-mcp-client.js

# Test Stripe integration
npm test
```

## Production Deployment

For production:

1. Set `NODE_ENV=production` in environment
2. Use live Stripe keys instead of test keys
3. Configure proper SSL/TLS certificates
4. Set up monitoring and logging
5. Use external Redis/PostgreSQL instances

## Security Notes

- All Stripe API keys are environment variables
- WebSocket connections can be authenticated via JWT
- CORS is configured for allowed origins only
- Webhook signatures are verified against Stripe

## Support

For issues or questions:
- Check logs: `docker logs synapse-mcp-stripe`
- Review health endpoint: `http://localhost:3000/health`
- Verify Stripe webhook events in dashboard