FROM python:3.10-slim

LABEL maintainer="synapse-team"
LABEL version="2.2.0"
LABEL description="Synapse scientific programming language"

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc g++ gfortran \
    libopenblas-dev liblapack-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy package
COPY . .

# Install Synapse
RUN pip install --no-cache-dir -e .

# Install optional dependencies
RUN pip install --no-cache-dir \
    numpy scipy pandas matplotlib \
    jupyter notebook

EXPOSE 8888

CMD ["synapse", "--repl"]
