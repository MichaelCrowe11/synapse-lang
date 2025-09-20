#!/bin/bash
# Synapse Language Documentation - Deploy to Fly.io (Linux/Mac)

echo "================================================"
echo "SYNAPSE DOCS DEPLOYMENT TO FLY.IO"
echo "================================================"
echo

# Check if fly is installed
if ! command -v fly &> /dev/null; then
    echo "ERROR: Fly CLI is not installed."
    echo
    echo "Please install Fly CLI first:"
    echo "  Mac: brew install flyctl"
    echo "  Linux: curl -L https://fly.io/install.sh | sh"
    echo
    exit 1
fi

echo "Fly CLI found. Proceeding with deployment..."
echo

# Navigate to docs-website directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/docs-website"

# Check if already initialized
if [ -f fly.toml ]; then
    echo "Fly app already configured. Deploying..."
    fly deploy
else
    echo "Initializing new Fly app..."
    echo
    echo "IMPORTANT: When prompted:"
    echo "  - App name: synapse-lang-docs (or your choice)"
    echo "  - Region: iad (US East) or your nearest region"
    echo "  - Database: NO"
    echo "  - Redis: NO"
    echo "  - Deploy now: YES"
    echo
    fly launch
fi

if [ $? -eq 0 ]; then
    echo
    echo "================================================"
    echo "DEPLOYMENT SUCCESSFUL!"
    echo "================================================"
    echo
    echo "Your documentation is now live!"
    echo
    echo "Opening in browser..."
    fly open
    echo
    echo "Useful commands:"
    echo "  fly logs       - View application logs"
    echo "  fly status     - Check deployment status"
    echo "  fly deploy     - Deploy updates"
    echo
else
    echo
    echo "================================================"
    echo "DEPLOYMENT FAILED"
    echo "================================================"
    echo
    echo "Please check the error messages above."
    echo "You may need to:"
    echo "  1. Run 'fly auth login' to authenticate"
    echo "  2. Check your internet connection"
    echo "  3. Verify the app name is unique"
    echo
fi