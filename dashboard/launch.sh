#!/bin/bash

# 🚀 Automated Vercel Deployment Script
# Deploys Crowe Code & Synapse-Code to production

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 DEPLOYING CROWE CODE & SYNAPSE-CODE TO VERCEL"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: Must run from dashboard directory"
    echo "Run: cd /home/user/synapse-lang/dashboard"
    exit 1
fi

echo "📍 Current directory: $(pwd)"
echo ""

# Check for Vercel CLI
if ! command -v vercel &> /dev/null && ! command -v npx &> /dev/null; then
    echo "❌ Vercel CLI not found. Installing..."
    npm install -g vercel
fi

echo "✅ Vercel CLI ready"
echo ""

# Check for authentication
echo "🔐 Checking Vercel authentication..."
echo ""

if [ -n "$VERCEL_TOKEN" ]; then
    echo "✅ VERCEL_TOKEN found in environment"
    DEPLOY_CMD="npx vercel --prod --yes --token $VERCEL_TOKEN"
else
    echo "⚠️  No VERCEL_TOKEN found"
    echo ""
    echo "📋 Two options:"
    echo ""
    echo "  Option 1: Deploy with browser login"
    echo "    - Will open browser for authentication"
    echo "    - Run: npx vercel --prod"
    echo ""
    echo "  Option 2: Use token"
    echo "    - Get token from: https://vercel.com/account/tokens"
    echo "    - Run: export VERCEL_TOKEN='your-token'"
    echo "    - Then run this script again"
    echo ""

    read -p "Continue with browser login? (y/n) " -n 1 -r
    echo ""

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo "ℹ️  To deploy manually:"
        echo "   1. Get token: https://vercel.com/account/tokens"
        echo "   2. export VERCEL_TOKEN='your-token'"
        echo "   3. npx vercel --prod --yes --token \$VERCEL_TOKEN"
        echo ""
        exit 0
    fi

    DEPLOY_CMD="npx vercel --prod"
fi

echo ""
echo "📦 Installing dependencies..."
npm install --legacy-peer-deps --silent

echo "🔨 Building production bundle..."
npm run build

echo ""
echo "🚀 Deploying to Vercel..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

$DEPLOY_CMD

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ DEPLOYMENT COMPLETE!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🎉 Your app is now live!"
echo ""
echo "📱 Visit your deployment:"
echo "   Home:         https://your-url.vercel.app/"
echo "   Crowe Code:   https://your-url.vercel.app/crowe-code"
echo "   Synapse-Code: https://your-url.vercel.app/synapse-code"
echo ""
echo "📊 View deployment details:"
echo "   https://vercel.com/dashboard"
echo ""
