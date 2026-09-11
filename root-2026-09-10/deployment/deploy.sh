#!/bin/bash

# Quantum Trinity Playground - Deployment Script
# Automated deployment to synapse-lang.com

set -e  # Exit on error
set -u  # Exit on undefined variable

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
DOMAIN="synapse-lang.com"
APP_NAME="quantum-trinity-playground"
DEPLOY_PATH="/var/www/synapse-lang"
BACKUP_PATH="/var/backups/synapse-lang"

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check environment file
    if [ ! -f ".env" ]; then
        log_error ".env file not found. Copy .env.example and configure it."
        exit 1
    fi
    
    log_info "Prerequisites check passed"
}

# Backup current deployment
backup_current() {
    log_info "Creating backup..."
    
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_DIR="${BACKUP_PATH}/${TIMESTAMP}"
    
    mkdir -p "${BACKUP_DIR}"
    
    # Backup database
    docker exec -t synapse_db pg_dump -U postgres synapse_playground > "${BACKUP_DIR}/database.sql"
    
    # Backup user files
    cp -r "${DEPLOY_PATH}/user_saves" "${BACKUP_DIR}/" 2>/dev/null || true
    
    # Backup environment
    cp "${DEPLOY_PATH}/.env" "${BACKUP_DIR}/.env.backup"
    
    log_info "Backup created at ${BACKUP_DIR}"
}

# Pull latest code
update_code() {
    log_info "Pulling latest code..."
    
    cd "${DEPLOY_PATH}"
    git pull origin production
    
    # Update permissions
    chmod +x deployment/deploy.sh
    chmod 600 .env
}

# Build and deploy containers
deploy_containers() {
    log_info "Building and deploying containers..."
    
    cd "${DEPLOY_PATH}"
    
    # Build images
    docker-compose -f deployment/deploy.yaml build --no-cache
    
    # Start services with zero downtime
    log_info "Starting services..."
    
    # Scale up new containers
    docker-compose -f deployment/deploy.yaml up -d --no-deps --scale app=2 app
    
    # Wait for health check
    sleep 30
    
    # Remove old containers
    docker-compose -f deployment/deploy.yaml up -d --remove-orphans
    
    # Verify deployment
    if curl -f "http://localhost:5000/api/health" > /dev/null 2>&1; then
        log_info "Health check passed"
    else
        log_error "Health check failed"
        rollback
        exit 1
    fi
}

# Run database migrations
run_migrations() {
    log_info "Running database migrations..."
    
    docker exec synapse_app python -c "
from flask import Flask
from flask_migrate import upgrade
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']

with app.app_context():
    upgrade()
"
    
    log_info "Migrations completed"
}

# Setup SSL certificates
setup_ssl() {
    log_info "Setting up SSL certificates..."
    
    # Check if certificates exist
    if [ ! -f "/etc/nginx/ssl/fullchain.pem" ]; then
        log_info "Requesting SSL certificate from Let's Encrypt..."
        
        docker run -it --rm \
            -v /etc/letsencrypt:/etc/letsencrypt \
            -v /var/lib/letsencrypt:/var/lib/letsencrypt \
            certbot/certbot certonly \
            --webroot \
            --webroot-path=/var/www/certbot \
            --email admin@synapse-lang.com \
            --agree-tos \
            --no-eff-email \
            -d ${DOMAIN} \
            -d www.${DOMAIN}
        
        # Copy certificates
        cp /etc/letsencrypt/live/${DOMAIN}/fullchain.pem /etc/nginx/ssl/
        cp /etc/letsencrypt/live/${DOMAIN}/privkey.pem /etc/nginx/ssl/
        cp /etc/letsencrypt/live/${DOMAIN}/chain.pem /etc/nginx/ssl/
    else
        log_info "SSL certificates already exist"
    fi
    
    # Setup auto-renewal
    echo "0 0 * * * root certbot renew --quiet && nginx -s reload" > /etc/cron.d/certbot-renew
}

# Clear caches
clear_caches() {
    log_info "Clearing caches..."
    
    # Clear Redis cache
    docker exec synapse_redis redis-cli FLUSHALL
    
    # Clear Cloudflare cache
    if [ ! -z "${CLOUDFLARE_API_TOKEN}" ]; then
        curl -X POST "https://api.cloudflare.com/client/v4/zones/${CLOUDFLARE_ZONE_ID}/purge_cache" \
            -H "Authorization: Bearer ${CLOUDFLARE_API_TOKEN}" \
            -H "Content-Type: application/json" \
            --data '{"purge_everything":true}'
    fi
    
    log_info "Caches cleared"
}

# Rollback deployment
rollback() {
    log_error "Rolling back deployment..."
    
    # Find latest backup
    LATEST_BACKUP=$(ls -t "${BACKUP_PATH}" | head -1)
    
    if [ ! -z "${LATEST_BACKUP}" ]; then
        # Restore database
        docker exec -i synapse_db psql -U postgres synapse_playground < "${BACKUP_PATH}/${LATEST_BACKUP}/database.sql"
        
        # Restore previous version
        cd "${DEPLOY_PATH}"
        git reset --hard HEAD~1
        
        # Restart services
        docker-compose -f deployment/deploy.yaml up -d
        
        log_info "Rollback completed"
    else
        log_error "No backup found for rollback"
    fi
}

# Monitor deployment
monitor_deployment() {
    log_info "Monitoring deployment..."
    
    # Check service status
    docker-compose -f deployment/deploy.yaml ps
    
    # Check logs for errors
    docker-compose -f deployment/deploy.yaml logs --tail=50 app | grep -i error || true
    
    # Performance check
    curl -w "\n\nResponse time: %{time_total}s\n" -o /dev/null -s "https://${DOMAIN}"
}

# Send notification
send_notification() {
    local status=$1
    local message=$2
    
    # Slack notification
    if [ ! -z "${SLACK_WEBHOOK}" ]; then
        curl -X POST "${SLACK_WEBHOOK}" \
            -H 'Content-Type: application/json' \
            -d "{\"text\":\"Deployment ${status}: ${message}\"}"
    fi
    
    # Email notification
    if [ ! -z "${SMTP_USER}" ]; then
        echo "${message}" | mail -s "Deployment ${status}" admin@synapse-lang.com
    fi
}

# Main deployment process
main() {
    log_info "Starting deployment to ${DOMAIN}"
    
    # Load environment
    source .env
    
    # Run deployment steps
    check_prerequisites
    backup_current
    update_code
    deploy_containers
    run_migrations
    setup_ssl
    clear_caches
    monitor_deployment
    
    # Clean up
    docker system prune -f
    
    log_info "Deployment completed successfully!"
    send_notification "SUCCESS" "Deployment to ${DOMAIN} completed successfully"
}

# Handle errors
trap 'log_error "Deployment failed"; rollback; send_notification "FAILED" "Deployment to ${DOMAIN} failed"; exit 1' ERR

# Run main function
main "$@"