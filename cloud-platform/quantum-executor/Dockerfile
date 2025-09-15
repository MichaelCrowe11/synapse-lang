FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libblas-dev \
    liblapack-dev \
    gfortran \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY main.py .

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV RAY_DISABLE_IMPORT_WARNING=1
ENV OMP_NUM_THREADS=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD python -c "import ray; ray.is_initialized()"

# Run application
CMD ["python", "main.py"]