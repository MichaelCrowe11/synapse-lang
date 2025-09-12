#!/bin/bash
# Start Synapse Language Payment Service locally for development

echo "Starting Synapse Language Payment Service locally..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found. Creating from template..."
    cp .env.example .env
    echo "Please edit .env with your API keys before running in production"
fi

# Set development environment variables
export FLASK_ENV=development
export COINBASE_COMMERCE_API_KEY=${COINBASE_COMMERCE_API_KEY:-"demo_key"}
export COINBASE_COMMERCE_WEBHOOK_SECRET=${COINBASE_COMMERCE_WEBHOOK_SECRET:-"demo_secret"}

echo ""
echo "============================================"
echo "🚀 Starting Payment Service on port 5000"
echo "============================================"
echo "Access at: http://localhost:5000"
echo "API docs: http://localhost:5000/api/products"
echo "Press Ctrl+C to stop"
echo ""

# Start the service
python payment_service.py