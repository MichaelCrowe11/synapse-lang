#!/bin/bash
# Synapse Language Payment Service Deployment Script

set -e

echo "🚀 Deploying Synapse Language Payment Service..."

# Configuration
PROJECT_NAME="synapse-payment-service"
DOMAIN="pay.synapse-lang.com"
BACKUP_DIR="/var/backups/synapse-payments"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root for security reasons"
   exit 1
fi

# Check required environment variables
check_env_vars() {
    print_status "Checking environment variables..."
    
    required_vars=(
        "COINBASE_COMMERCE_API_KEY"
        "COINBASE_COMMERCE_WEBHOOK_SECRET"
        "POSTGRES_PASSWORD"
        "SENDGRID_API_KEY"
    )
    
    missing_vars=()
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var}" ]]; then
            missing_vars+=("$var")
        fi
    done
    
    if [[ ${#missing_vars[@]} -gt 0 ]]; then
        print_error "Missing required environment variables:"
        for var in "${missing_vars[@]}"; do
            echo "  - $var"
        done
        print_error "Please set these variables and run again"
        exit 1
    fi
    
    print_success "All required environment variables are set"
}

# Install system dependencies
install_dependencies() {
    print_status "Installing system dependencies..."
    
    sudo apt-get update
    sudo apt-get install -y \
        docker.io \
        docker-compose \
        nginx \
        certbot \
        python3-certbot-nginx \
        postgresql-client \
        curl \
        jq
    
    # Add user to docker group
    sudo usermod -aG docker $USER
    
    print_success "System dependencies installed"
}

# Setup SSL certificate
setup_ssl() {
    print_status "Setting up SSL certificate for $DOMAIN..."
    
    if [[ ! -f "/etc/letsencrypt/live/$DOMAIN/cert.pem" ]]; then
        print_status "Obtaining SSL certificate..."
        sudo certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email admin@synapse-lang.com
    else
        print_success "SSL certificate already exists"
    fi
    
    # Create SSL directory for Docker
    sudo mkdir -p ssl/
    sudo cp "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ssl/cert.pem
    sudo cp "/etc/letsencrypt/live/$DOMAIN/privkey.pem" ssl/key.pem
    sudo chown $USER:$USER ssl/*
    
    print_success "SSL certificate configured"
}

# Create backup
create_backup() {
    print_status "Creating backup..."
    
    sudo mkdir -p $BACKUP_DIR
    timestamp=$(date +"%Y%m%d_%H%M%S")
    backup_file="$BACKUP_DIR/backup_$timestamp.tar.gz"
    
    # Backup database if it exists
    if docker-compose ps postgres | grep -q "Up"; then
        print_status "Backing up database..."
        docker-compose exec -T postgres pg_dump -U postgres synapse_payments > "db_backup_$timestamp.sql"
        sudo mv "db_backup_$timestamp.sql" $BACKUP_DIR/
    fi
    
    # Backup application data
    tar -czf "$backup_file" \
        --exclude="node_modules" \
        --exclude="__pycache__" \
        --exclude="*.pyc" \
        --exclude=".git" \
        ./ || print_warning "Backup creation failed"
    
    print_success "Backup created: $backup_file"
}

# Deploy application
deploy_application() {
    print_status "Deploying application..."
    
    # Stop existing containers
    docker-compose down || true
    
    # Remove old images
    docker system prune -f
    
    # Build and start services
    print_status "Building Docker containers..."
    docker-compose build --no-cache
    
    print_status "Starting services..."
    docker-compose up -d
    
    # Wait for services to be ready
    print_status "Waiting for services to start..."
    sleep 30
    
    # Check service health
    check_service_health
    
    print_success "Application deployed successfully"
}

# Check service health
check_service_health() {
    print_status "Checking service health..."
    
    max_attempts=30
    attempt=0
    
    while [[ $attempt -lt $max_attempts ]]; do
        if curl -f -s http://localhost:5000/api/products > /dev/null; then
            print_success "Payment service is healthy"
            break
        fi
        
        attempt=$((attempt + 1))
        print_status "Attempt $attempt/$max_attempts - waiting for service..."
        sleep 10
    done
    
    if [[ $attempt -eq $max_attempts ]]; then
        print_error "Service health check failed"
        docker-compose logs
        exit 1
    fi
    
    # Test database connection
    if docker-compose exec -T postgres psql -U postgres -d synapse_payments -c "SELECT 1;" > /dev/null; then
        print_success "Database is healthy"
    else
        print_error "Database connection failed"
        exit 1
    fi
}

# Setup monitoring
setup_monitoring() {
    print_status "Setting up monitoring..."
    
    # Create log rotation
    sudo tee /etc/logrotate.d/synapse-payment > /dev/null <<EOF
/var/log/synapse-payment/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        docker-compose restart payment-service
    endscript
}
EOF
    
    # Create monitoring script
    tee monitor.sh > /dev/null <<'EOF'
#!/bin/bash
# Synapse Payment Service Monitoring

check_service() {
    local service=$1
    if ! docker-compose ps $service | grep -q "Up"; then
        echo "$(date): $service is down, restarting..." >> /var/log/synapse-monitor.log
        docker-compose restart $service
    fi
}

check_service payment-service
check_service postgres
check_service redis
check_service nginx

# Check disk space
if [[ $(df / | awk 'NR==2 {print $5}' | sed 's/%//') -gt 90 ]]; then
    echo "$(date): Disk space critical" >> /var/log/synapse-monitor.log
fi
EOF
    
    chmod +x monitor.sh
    
    # Add to crontab
    (crontab -l 2>/dev/null || true; echo "*/5 * * * * $PWD/monitor.sh") | crontab -
    
    print_success "Monitoring configured"
}

# Setup firewall
setup_firewall() {
    print_status "Configuring firewall..."
    
    sudo ufw --force enable
    sudo ufw default deny incoming
    sudo ufw default allow outgoing
    
    # Allow SSH
    sudo ufw allow ssh
    
    # Allow HTTP/HTTPS
    sudo ufw allow 80
    sudo ufw allow 443
    
    # Allow specific IPs for management (add your IPs here)
    # sudo ufw allow from YOUR_IP_ADDRESS to any port 22
    
    print_success "Firewall configured"
}

# Main deployment function
main() {
    print_status "Starting Synapse Language Payment Service deployment"
    
    # Pre-deployment checks
    check_env_vars
    
    # Installation steps
    install_dependencies
    setup_ssl
    create_backup
    deploy_application
    setup_monitoring
    setup_firewall
    
    print_success "🎉 Deployment completed successfully!"
    print_status "Service is now available at: https://$DOMAIN"
    print_status "Monitor logs with: docker-compose logs -f"
    print_status "Check service status: docker-compose ps"
    
    # Display useful commands
    echo ""
    print_status "Useful commands:"
    echo "  - View logs: docker-compose logs -f"
    echo "  - Restart service: docker-compose restart payment-service"
    echo "  - Update service: git pull && docker-compose build --no-cache && docker-compose up -d"
    echo "  - Database backup: docker-compose exec postgres pg_dump -U postgres synapse_payments > backup.sql"
    echo "  - Monitor service: curl https://$DOMAIN/health"
}

# Run main function
main "$@"