FROM python:3.10-slim

LABEL maintainer="Michael Benjamin Crowe"
LABEL version="2.3.3"
LABEL description="Synapse Language - Scientific computing with quantum, AI, and blockchain"
LABEL org.opencontainers.image.source="https://github.com/synapse-lang/synapse-lang"
LABEL org.opencontainers.image.version="2.3.3"
LABEL org.opencontainers.image.title="Synapse Language"
LABEL org.opencontainers.image.description="Revolutionary scientific programming language with uncertainty quantification, quantum computing, real-time collaboration, and blockchain verification"

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc g++ gfortran \
    libopenblas-dev liblapack-dev \
    git curl wget \
    && rm -rf /var/lib/apt/lists/*

# Install Synapse from PyPI (now that it's published!)
RUN pip install --no-cache-dir synapse-lang==2.3.3

# Install scientific computing dependencies
RUN pip install --no-cache-dir \
    numpy scipy pandas matplotlib \
    jupyter notebook ipython \
    networkx sympy \
    plotly seaborn numba

# Create workspace directory
RUN mkdir -p /workspace
WORKDIR /workspace

# Add helpful startup message
RUN echo '#!/bin/bash' > /entrypoint.sh && \
    echo 'echo ""' >> /entrypoint.sh && \
    echo 'echo "🧠 Synapse Language v2.3.3 - Docker Container"' >> /entrypoint.sh && \
    echo 'echo "============================================"' >> /entrypoint.sh && \
    echo 'echo ""' >> /entrypoint.sh && \
    echo 'echo "Available commands:"' >> /entrypoint.sh && \
    echo 'echo "  python           - Python interpreter with Synapse"' >> /entrypoint.sh && \
    echo 'echo "  ipython          - Interactive Python shell"' >> /entrypoint.sh && \
    echo 'echo "  jupyter notebook - Launch Jupyter notebook server"' >> /entrypoint.sh && \
    echo 'echo ""' >> /entrypoint.sh && \
    echo 'echo "To test Synapse:"' >> /entrypoint.sh && \
    echo 'echo "  python -c \\"import synapse_lang; print(synapse_lang.__version__)\\""' >> /entrypoint.sh && \
    echo 'echo ""' >> /entrypoint.sh && \
    echo 'exec "$@"' >> /entrypoint.sh && \
    chmod +x /entrypoint.sh

# Expose Jupyter port
EXPOSE 8888

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"]

# Default command
CMD ["python"]
