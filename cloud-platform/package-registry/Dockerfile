FROM python:3.11-slim

WORKDIR /app

# Create packages directory
RUN mkdir -p /app/packages

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY main.py .

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PACKAGE_STORAGE_PATH=/app/packages

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8001/api/v1/health')"

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "2"]