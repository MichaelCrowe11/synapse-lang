# Multi-stage build for Synapse-Lang
FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    cmake \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --user --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 synapse && \
    mkdir -p /home/synapse/.synapse-lang

# Copy Python packages from builder
COPY --from=builder /root/.local /home/synapse/.local

# Set working directory
WORKDIR /app

# Copy application files
COPY --chown=synapse:synapse . .

# Set PATH
ENV PATH=/home/synapse/.local/bin:$PATH
ENV PYTHONPATH=/app:$PYTHONPATH

# Switch to non-root user
USER synapse

# Expose port for license server (if running)
EXPOSE 8000

# Default command - run REPL
CMD ["python", "synapse_interpreter_enhanced.py"]

# Labels
LABEL maintainer="Michael Benjamin Crowe <michael@synapse-lang.com>"
LABEL version="1.0.0"
LABEL description="Synapse-Lang - Scientific Computing Language with Parallel Execution"