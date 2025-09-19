#!/bin/bash

# Synapse Language v2.3.0 - Docker Publishing Script
# This script builds and publishes the Docker image to Docker Hub

set -e

# Configuration
IMAGE_NAME="synapse-lang/synapse-lang"
VERSION="2.3.0"
PLATFORMS="linux/amd64,linux/arm64"

echo "================================================"
echo "🐳 SYNAPSE LANGUAGE DOCKER PUBLISHER"
echo "================================================"
echo ""
echo "Image: ${IMAGE_NAME}:${VERSION}"
echo "Platforms: ${PLATFORMS}"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if logged into Docker Hub
if ! docker info 2>/dev/null | grep -q "Username"; then
    echo "📝 Please log in to Docker Hub:"
    docker login
fi

echo ""
echo "🏗️  Building Docker image..."
echo "------------------------------"

# Build for multiple platforms if buildx is available
if docker buildx version &> /dev/null; then
    echo "Using Docker Buildx for multi-platform build..."

    # Create builder if it doesn't exist
    if ! docker buildx ls | grep -q synapse-builder; then
        docker buildx create --name synapse-builder --use
    else
        docker buildx use synapse-builder
    fi

    # Build and push multi-platform image
    docker buildx build \
        --platform ${PLATFORMS} \
        -t ${IMAGE_NAME}:${VERSION} \
        -t ${IMAGE_NAME}:latest \
        --push \
        .

    echo "✅ Multi-platform image built and pushed!"
else
    echo "Using standard Docker build..."

    # Build image
    docker build -t ${IMAGE_NAME}:${VERSION} -t ${IMAGE_NAME}:latest .

    echo ""
    echo "📤 Pushing to Docker Hub..."
    echo "------------------------------"

    # Push both tags
    docker push ${IMAGE_NAME}:${VERSION}
    docker push ${IMAGE_NAME}:latest

    echo "✅ Image pushed successfully!"
fi

echo ""
echo "🔍 Verifying publication..."
echo "------------------------------"

# Pull the image to verify
docker pull ${IMAGE_NAME}:${VERSION}

echo ""
echo "📊 Image Information:"
docker images ${IMAGE_NAME}

echo ""
echo "================================================"
echo "✅ DOCKER PUBLICATION COMPLETE!"
echo "================================================"
echo ""
echo "📦 Published to Docker Hub:"
echo "   https://hub.docker.com/r/${IMAGE_NAME}"
echo ""
echo "🚀 Installation Commands:"
echo "   docker pull ${IMAGE_NAME}:${VERSION}"
echo "   docker pull ${IMAGE_NAME}:latest"
echo ""
echo "💻 Run Commands:"
echo "   # Interactive Python shell"
echo "   docker run -it ${IMAGE_NAME}:${VERSION}"
echo ""
echo "   # Jupyter notebook"
echo "   docker run -p 8888:8888 ${IMAGE_NAME}:${VERSION} jupyter notebook --ip=0.0.0.0 --allow-root"
echo ""
echo "   # Mount local directory"
echo "   docker run -it -v \$(pwd):/workspace ${IMAGE_NAME}:${VERSION}"
echo ""
echo "🎉 Success! Synapse Language v${VERSION} is now available on Docker Hub!"