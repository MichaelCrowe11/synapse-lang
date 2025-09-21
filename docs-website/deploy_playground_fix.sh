#!/bin/bash

echo "================================================"
echo "DEPLOYING FIXED PLAYGROUND TO PRODUCTION"
echo "================================================"
echo ""

echo "Step 1: Updating Dockerfile for production..."
cat > Dockerfile.production <<'EOF'
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc g++ \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy synapse_lang module
COPY ../synapse_lang /app/synapse_lang

# Copy website files
COPY . /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements_v2.txt

# Install additional dependencies for code execution
RUN pip install --no-cache-dir psutil

# Create non-root user for security
RUN useradd -m -u 1000 synapse && chown -R synapse:synapse /app

USER synapse

EXPOSE 8080

# Run with eventlet worker for WebSocket support
CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "--bind", "0.0.0.0:8080", "--timeout", "120", "app_v2_socket:app"]
EOF

echo "Step 2: Deploying to Fly.io..."
fly deploy --dockerfile Dockerfile.production --app synapse-lang-docs

if [ $? -eq 0 ]; then
    echo ""
    echo "================================================"
    echo "DEPLOYMENT SUCCESSFUL!"
    echo "================================================"
    echo ""
    echo "The playground now has REAL code execution!"
    echo ""
    echo "Testing the live site..."
    curl -s https://synapse-lang-docs.fly.dev/health | head -n 5
    echo ""
    echo "Visit: https://synapse-lang-docs.fly.dev/playground"
else
    echo ""
    echo "Deployment failed. Check the errors above."
fi
