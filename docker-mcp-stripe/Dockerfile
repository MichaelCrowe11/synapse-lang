# Docker MCP Server with Stripe Integration
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js for MCP server
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs

# Set working directory
WORKDIR /app

# Copy Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy MCP server configuration
COPY mcp-server/ ./mcp-server/

# Install MCP dependencies
WORKDIR /app/mcp-server
RUN npm install

# Copy environment variables
COPY .env /app/.env

# Expose ports
EXPOSE 3000 8000 8001

# Set environment variables
ENV MCP_SERVER_PORT=3000
ENV STRIPE_ENABLED=true
ENV PYTHONUNBUFFERED=1

# Start script
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

WORKDIR /app

# Run the MCP server with Stripe integration
CMD ["/app/start.sh"]