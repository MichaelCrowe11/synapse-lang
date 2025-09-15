@echo off
echo 🚀 Setting up MCP Stripe Server for Claude Desktop...
echo.

REM Create Claude Desktop config directory if it doesn't exist
if not exist "%APPDATA%\Claude" mkdir "%APPDATA%\Claude"

echo 📝 Creating Claude Desktop MCP configuration...

REM Copy the MCP configuration to Claude Desktop config directory
copy claude-desktop-config.json "%APPDATA%\Claude\claude_desktop_config.json"

echo ✅ MCP configuration installed to: %APPDATA%\Claude\claude_desktop_config.json
echo.

echo 📋 Configuration details:
echo   - Server Name: synapse-stripe
echo   - Port: 3002
echo   - Tools Available: 8 Stripe integration tools
echo   - Webhook Endpoint: http://localhost:8000/stripe/webhook
echo.

echo 🎯 Next Steps:
echo   1. Restart Claude Desktop application
echo   2. The MCP server will automatically start when Claude Desktop launches
echo   3. Available Stripe tools will appear in Claude Desktop
echo.

echo 🛠️  Available MCP Tools:
echo   - stripe-create-customer: Create new Stripe customers
echo   - stripe-create-subscription: Create subscriptions
echo   - stripe-create-checkout: Create checkout sessions
echo   - stripe-cancel-subscription: Cancel subscriptions
echo   - stripe-get-customer: Get customer details
echo   - stripe-list-subscriptions: List subscriptions
echo   - stripe-create-portal: Create customer portal
echo   - stripe-webhook-handler: Handle webhook events
echo.

echo ⚠️  Important Notes:
echo   - Your CROWE LOGIC Stripe account is configured
echo   - Test mode keys are being used (safe for development)
echo   - Webhook listener is running on port 8000
echo   - Authentication system is running on port 8001
echo.

echo 🎉 Setup complete! Restart Claude Desktop to enable MCP integration.
pause