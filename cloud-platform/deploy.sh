#!/bin/bash

# Synapse Cloud Platform Deployment Script
# Automated deployment for development and production environments

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-development}
REGION=${2:-us-west-2}
CLUSTER_NAME="synapse-platform-${ENVIRONMENT}"

echo -e "${BLUE}🚀 Synapse Cloud Platform Deployment${NC}"
echo -e "${BLUE}Environment: ${ENVIRONMENT}${NC}"
echo -e "${BLUE}Region: ${REGION}${NC}"
echo ""

# Function to check prerequisites
check_prerequisites() {
    echo -e "${YELLOW}Checking prerequisites...${NC}"
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Error: Docker is not installed${NC}"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}Error: Docker Compose is not installed${NC}"
        exit 1
    fi
    
    # Check kubectl for production
    if [[ "$ENVIRONMENT" == "production" ]]; then
        if ! command -v kubectl &> /dev/null; then
            echo -e "${RED}Error: kubectl is not installed${NC}"
            exit 1
        fi
        
        if ! command -v helm &> /dev/null; then
            echo -e "${RED}Error: Helm is not installed${NC}"
            exit 1
        fi
    fi
    
    echo -e "${GREEN}✓ Prerequisites check passed${NC}"
}

# Function to setup environment variables
setup_environment() {
    echo -e "${YELLOW}Setting up environment variables...${NC}"
    
    # Create .env file if it doesn't exist
    if [[ ! -f .env ]]; then
        cp .env.example .env
        echo -e "${YELLOW}Created .env file from template. Please update with your values.${NC}"
    fi
    
    # Load environment variables
    export $(cat .env | grep -v '#' | xargs)
    
    # Validate required variables
    required_vars=("JWT_SECRET" "POSTGRES_PASSWORD" "REDIS_PASSWORD")
    
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var}" ]]; then
            echo -e "${RED}Error: $var is not set in .env file${NC}"
            exit 1
        fi
    done
    
    echo -e "${GREEN}✓ Environment variables configured${NC}"
}

# Function to build Docker images
build_images() {
    echo -e "${YELLOW}Building Docker images...${NC}"
    
    # Build all service images
    docker-compose build --parallel
    
    # Tag images for environment
    services=("api-gateway" "quantum-executor" "package-registry" "user-service")
    
    for service in "${services[@]}"; do
        docker tag "synapse-${service}:latest" "synapse-${service}:${ENVIRONMENT}"
        echo -e "${GREEN}✓ Built ${service}${NC}"
    done
    
    echo -e "${GREEN}✓ All images built successfully${NC}"
}

# Function to deploy to development
deploy_development() {
    echo -e "${YELLOW}Deploying to development environment...${NC}"
    
    # Start services with Docker Compose
    docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
    
    # Wait for services to be healthy
    echo -e "${YELLOW}Waiting for services to be ready...${NC}"
    sleep 30
    
    # Run database migrations
    docker-compose exec api-gateway python -c "from main import create_tables; import asyncio; asyncio.run(create_tables())"
    
    # Check service health
    check_service_health
    
    echo -e "${GREEN}✓ Development deployment completed${NC}"
    echo -e "${BLUE}API Gateway: http://localhost:8000${NC}"
    echo -e "${BLUE}Package Registry: http://localhost:8001${NC}"
    echo -e "${BLUE}Grafana: http://localhost:3000 (admin/admin)${NC}"
    echo -e "${BLUE}Prometheus: http://localhost:9090${NC}"
}

# Function to deploy to production
deploy_production() {
    echo -e "${YELLOW}Deploying to production environment...${NC}"
    
    # Check if Kubernetes cluster exists
    if ! kubectl cluster-info &> /dev/null; then
        echo -e "${RED}Error: Cannot connect to Kubernetes cluster${NC}"
        exit 1
    fi
    
    # Create namespace if it doesn't exist
    kubectl create namespace synapse-platform --dry-run=client -o yaml | kubectl apply -f -
    
    # Deploy with Helm
    helm upgrade --install synapse-platform ./helm/synapse-platform \
        --namespace synapse-platform \
        --set environment=production \
        --set image.tag=${ENVIRONMENT} \
        --set ingress.enabled=true \
        --set autoscaling.enabled=true \
        --wait
    
    # Check deployment status
    kubectl rollout status deployment/api-gateway -n synapse-platform
    kubectl rollout status deployment/quantum-executor -n synapse-platform
    kubectl rollout status deployment/package-registry -n synapse-platform
    kubectl rollout status deployment/user-service -n synapse-platform
    
    echo -e "${GREEN}✓ Production deployment completed${NC}"
    
    # Get external IP
    EXTERNAL_IP=$(kubectl get service synapse-ingress -n synapse-platform -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
    if [[ -n "$EXTERNAL_IP" ]]; then
        echo -e "${BLUE}Platform URL: https://${EXTERNAL_IP}${NC}"
    fi
}

# Function to check service health
check_service_health() {
    echo -e "${YELLOW}Checking service health...${NC}"
    
    services=(
        "http://localhost:8000/api/v1/health:API Gateway"
        "http://localhost:8001/api/v1/health:Package Registry"
        "http://localhost:8002/api/v1/health:User Service"
    )
    
    for service in "${services[@]}"; do
        IFS=':' read -r url name <<< "$service"
        
        max_attempts=30
        attempt=1
        
        while [[ $attempt -le $max_attempts ]]; do
            if curl -f -s "$url" > /dev/null; then
                echo -e "${GREEN}✓ $name is healthy${NC}"
                break
            fi
            
            if [[ $attempt -eq $max_attempts ]]; then
                echo -e "${RED}✗ $name failed health check${NC}"
                return 1
            fi
            
            echo -e "${YELLOW}Waiting for $name... (attempt $attempt/$max_attempts)${NC}"
            sleep 5
            ((attempt++))
        done
    done
    
    echo -e "${GREEN}✓ All services are healthy${NC}"
}

# Function to setup monitoring
setup_monitoring() {
    echo -e "${YELLOW}Setting up monitoring...${NC}"
    
    # Import Grafana dashboards
    if [[ "$ENVIRONMENT" == "development" ]]; then
        # Wait for Grafana to be ready
        while ! curl -f -s http://localhost:3000/api/health > /dev/null; do
            echo "Waiting for Grafana..."
            sleep 5
        done
        
        # Import dashboards
        for dashboard in monitoring/grafana-dashboards/*.json; do
            curl -X POST \
                -H "Content-Type: application/json" \
                -d @"$dashboard" \
                http://admin:admin@localhost:3000/api/dashboards/db
        done
    fi
    
    echo -e "${GREEN}✓ Monitoring setup completed${NC}"
}

# Function to run tests
run_tests() {
    echo -e "${YELLOW}Running integration tests...${NC}"
    
    # Run API tests
    python -m pytest tests/integration/ -v
    
    # Run load tests if available
    if [[ -f "tests/load/test_quantum_execution.py" ]]; then
        python tests/load/test_quantum_execution.py
    fi
    
    echo -e "${GREEN}✓ Tests completed${NC}"
}

# Function to cleanup
cleanup() {
    echo -e "${YELLOW}Cleaning up...${NC}"
    
    if [[ "$ENVIRONMENT" == "development" ]]; then
        docker-compose down
        docker system prune -f
    else
        kubectl delete namespace synapse-platform --ignore-not-found=true
    fi
    
    echo -e "${GREEN}✓ Cleanup completed${NC}"
}

# Function to show logs
show_logs() {
    echo -e "${YELLOW}Showing service logs...${NC}"
    
    if [[ "$ENVIRONMENT" == "development" ]]; then
        docker-compose logs -f
    else
        kubectl logs -n synapse-platform -l app=synapse-platform -f
    fi
}

# Function to show status
show_status() {
    echo -e "${BLUE}Synapse Platform Status${NC}"
    echo ""
    
    if [[ "$ENVIRONMENT" == "development" ]]; then
        docker-compose ps
    else
        kubectl get pods -n synapse-platform
        kubectl get services -n synapse-platform
    fi
}

# Main deployment logic
main() {
    case "${3:-deploy}" in
        "deploy")
            check_prerequisites
            setup_environment
            build_images
            
            if [[ "$ENVIRONMENT" == "production" ]]; then
                deploy_production
            else
                deploy_development
            fi
            
            setup_monitoring
            run_tests
            show_status
            ;;
        "cleanup")
            cleanup
            ;;
        "logs")
            show_logs
            ;;
        "status")
            show_status
            ;;
        "test")
            run_tests
            ;;
        *)
            echo "Usage: $0 [environment] [region] [action]"
            echo "  environment: development (default), staging, production"
            echo "  region: AWS region (default: us-west-2)"
            echo "  action: deploy (default), cleanup, logs, status, test"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"