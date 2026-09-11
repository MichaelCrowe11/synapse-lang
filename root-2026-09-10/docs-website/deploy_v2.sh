#!/bin/bash
# Synapse Language v2 Documentation - Production Deployment Script
# For Linux/Mac users

echo "================================================"
echo "SYNAPSE v2 DOCS - PRODUCTION DEPLOYMENT"
echo "================================================"
echo ""
echo "Modern UI with Real-time Features"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if fly is installed
if ! command -v fly &> /dev/null; then
    echo -e "${RED}ERROR: Fly CLI is not installed.${NC}"
    echo ""
    echo "Please install Fly CLI first:"
    echo "  Mac: brew install flyctl"
    echo "  Linux: curl -L https://fly.io/install.sh | sh"
    echo ""
    exit 1
fi

echo -e "${YELLOW}[1/5] Checking Fly authentication...${NC}"
if ! fly auth whoami &> /dev/null; then
    echo ""
    echo "You need to login to Fly.io first"
    fly auth login
fi

echo -e "${YELLOW}[2/5] Setting up environment...${NC}"

# Set production secrets
echo ""
echo "Setting production secrets..."
SECRET_KEY=$(openssl rand -hex 32)
fly secrets set SECRET_KEY=$SECRET_KEY --app synapse-lang-docs &> /dev/null

echo -e "${YELLOW}[3/5] Building production image...${NC}"
echo ""

# Use the production configuration
cp fly.toml.v2 fly.toml

echo -e "${YELLOW}[4/5] Deploying to Fly.io...${NC}"
echo ""
echo "This may take a few minutes..."
echo ""

if fly deploy --dockerfile Dockerfile.production; then
    echo ""
    echo -e "${YELLOW}[5/5] Deployment successful! Verifying...${NC}"
    echo ""

    # Wait for deployment to stabilize
    sleep 5

    # Check deployment status
    fly status --app synapse-lang-docs

    echo ""
    echo -e "${GREEN}================================================"
    echo "DEPLOYMENT SUCCESSFUL!"
    echo "================================================${NC}"
    echo ""
    echo "Your v2 documentation site is now live at:"
    echo -e "${GREEN}https://synapse-lang-docs.fly.dev${NC}"
    echo ""
    echo "Features enabled:"
    echo "  ✓ Modern Vercel/npm-inspired design"
    echo "  ✓ Real-time collaboration with WebSocket"
    echo "  ✓ Interactive code playground"
    echo "  ✓ Package explorer with syntax highlighting"
    echo "  ✓ API documentation with try-it-now"
    echo "  ✓ Dark/light theme system"
    echo "  ✓ Analytics dashboard"
    echo ""
    echo "Commands:"
    echo "  View logs:    fly logs --app synapse-lang-docs"
    echo "  Check status: fly status --app synapse-lang-docs"
    echo "  Open site:    fly open --app synapse-lang-docs"
    echo "  SSH console:  fly ssh console --app synapse-lang-docs"
    echo ""
    echo "Opening in browser..."
    sleep 3
    fly open --app synapse-lang-docs
else
    echo ""
    echo -e "${RED}================================================"
    echo "DEPLOYMENT FAILED"
    echo "================================================${NC}"
    echo ""
    echo "Please check the error messages above."
    echo ""
    echo "Troubleshooting:"
    echo "  1. Check logs: fly logs --app synapse-lang-docs"
    echo "  2. Verify Docker build: docker build -f Dockerfile.production ."
    echo "  3. Check app status: fly status --app synapse-lang-docs"
    echo "  4. Review configuration: fly config show --app synapse-lang-docs"
    echo ""
fi