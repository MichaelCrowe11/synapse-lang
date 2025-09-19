FROM python:3.10-slim

LABEL maintainer="Michael Benjamin Crowe"
LABEL version="2.3.2"
LABEL description="Synapse Language - Scientific computing with quantum, AI, and blockchain"
LABEL org.opencontainers.image.source="https://github.com/synapse-lang/synapse-lang"
LABEL org.opencontainers.image.version="2.3.2"
LABEL org.opencontainers.image.title="Synapse Language"
LABEL org.opencontainers.image.description="Revolutionary scientific programming language with uncertainty quantification, quantum computing, real-time collaboration, and blockchain verification"

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc g++ gfortran \
    libopenblas-dev liblapack-dev \
    git curl wget \
    && rm -rf /var/lib/apt/lists/*

# Install Synapse from PyPI (v2.3.2 with PEP 625 compliant naming)
RUN pip install --no-cache-dir synapse-lang==2.3.2

# Install scientific computing dependencies
RUN pip install --no-cache-dir \
    numpy scipy pandas matplotlib \
    jupyter notebook ipython \
    networkx sympy \
    plotly seaborn \
    numba

# Create workspace directory
RUN mkdir -p /workspace
WORKDIR /workspace

# Add helpful startup message
RUN echo '#!/bin/bash\n\
echo ""\n\
echo "🧠 Synapse Language v2.3.2 - Docker Container"\n\
echo "============================================"\n\
echo ""\n\
echo "Available commands:"\n\
echo "  python           - Python interpreter with Synapse"\n\
echo "  ipython          - Interactive Python shell"\n\
echo "  jupyter notebook - Launch Jupyter notebook server"\n\
echo ""\n\
echo "To test Synapse:"\n\
echo "  python -c \"import synapse_lang; print(synapse_lang.__version__)\""\n\
echo ""\n\
exec "$@"' > /entrypoint.sh && chmod +x /entrypoint.sh

# Expose Jupyter port
EXPOSE 8888

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"]

# Default command
CMD ["python"]
