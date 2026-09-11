#!/bin/bash

# Start script for MCP Stripe Server
echo "🚀 Starting MCP Stripe Server..."

# Source environment variables
if [ -f /app/.env ]; then
    source /app/.env
    echo "✅ Environment variables loaded"
else
    echo "⚠️  Warning: .env file not found"
fi

# Check Stripe configuration
if [ -z "$STRIPE_API_KEY" ]; then
    echo "❌ Error: STRIPE_API_KEY not set"
    exit 1
fi

if [ -z "$STRIPE_WEBHOOK_SECRET" ]; then
    echo "⚠️  Warning: STRIPE_WEBHOOK_SECRET not set - webhooks will not work"
fi

echo "✅ Stripe configuration validated"

# Start Python authentication service in background
echo "🔐 Starting authentication service..."
cd /app/auth_system && python -m app.main &
AUTH_PID=$!

# Start webhook listener in background
echo "🪝 Starting Stripe webhook listener..."
cd /app && stripe listen --forward-to http://localhost:8000/stripe/webhook &
WEBHOOK_PID=$!

# Start MCP server
echo "📡 Starting MCP server on port ${MCP_SERVER_PORT:-3000}..."
cd /app/mcp-server && npm start &
MCP_PID=$!

# Function to cleanup processes on exit
cleanup() {
    echo "🛑 Shutting down services..."
    kill $AUTH_PID $WEBHOOK_PID $MCP_PID 2>/dev/null
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

# Wait for all services to be ready
sleep 5

echo "🎉 All services started successfully!"
echo "📍 Services running:"
echo "   - MCP Server: http://localhost:${MCP_SERVER_PORT:-3000}"
echo "   - Authentication API: http://localhost:8001"
echo "   - Stripe Webhooks: http://localhost:8000"
echo "   - WebSocket MCP: ws://localhost:${MCP_SERVER_PORT:-3000}/mcp"

# Keep the container running
wait