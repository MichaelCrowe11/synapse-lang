#!/bin/bash
# Setup Synapse Language Payment Service with live Coinbase Commerce credentials

set -e

echo "🚀 Setting up Synapse Language Payment Service for Production..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Step 1: Copy production environment file
if [ ! -f ".env" ]; then
    echo "Setting up production environment..."
    cp .env.production .env
    print_status "Production environment file created"
else
    print_warning ".env file already exists, not overwriting"
fi

# Step 2: Set up Coinbase Commerce webhook
echo ""
echo "📡 Coinbase Commerce Webhook Configuration"
echo "=========================================="
echo "1. Go to https://commerce.coinbase.com/dashboard/settings"
echo "2. Navigate to 'Webhooks' section"
echo "3. Add new webhook with these settings:"
echo "   - URL: https://pay.synapse-lang.com/api/webhooks/coinbase"
echo "   - Events: charge:confirmed, charge:failed, charge:pending"
echo "   - Secret: Already configured in .env file"
echo ""

# Step 3: Test API connection
echo "🔧 Testing Coinbase Commerce API connection..."

if command -v python3 &> /dev/null; then
    python3 -c "
import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('COINBASE_COMMERCE_API_KEY')
if not api_key:
    print('❌ API key not found in .env file')
    exit(1)

headers = {
    'Content-Type': 'application/json',
    'X-CC-Api-Key': api_key,
    'X-CC-Version': '2018-03-22'
}

try:
    response = requests.get('https://api.commerce.coinbase.com/charges', headers=headers)
    if response.status_code == 200:
        print('✅ Coinbase Commerce API connection successful!')
    else:
        print(f'❌ API connection failed: {response.status_code}')
        print(response.text)
except Exception as e:
    print(f'❌ Connection error: {str(e)}')
    " 2>/dev/null || echo "Python not available for API test"
else
    print_warning "Python not found, skipping API test"
fi

# Step 4: Create necessary directories
echo ""
echo "📁 Creating required directories..."
mkdir -p logs ssl backups
print_status "Directories created"

# Step 5: Set up SSL certificates (Let's Encrypt)
echo ""
echo "🔒 SSL Certificate Setup"
echo "======================="
echo "Run these commands on your server to set up SSL:"
echo ""
echo "sudo apt-get update"
echo "sudo apt-get install -y certbot python3-certbot-nginx"
echo "sudo certbot --nginx -d pay.synapse-lang.com --email admin@synapse-lang.com --agree-tos --non-interactive"
echo ""

# Step 6: Database setup instructions
echo "🗄️ Database Setup"
echo "================"
echo "1. Install PostgreSQL:"
echo "   sudo apt-get install -y postgresql postgresql-contrib"
echo ""
echo "2. Create database and user:"
echo "   sudo -u postgres createdb synapse_payments"
echo "   sudo -u postgres psql -c \"CREATE USER synapse_user WITH PASSWORD 'YOUR_SECURE_PASSWORD';\""
echo "   sudo -u postgres psql -c \"GRANT ALL PRIVILEGES ON DATABASE synapse_payments TO synapse_user;\""
echo ""
echo "3. Update DATABASE_URL in .env with your secure password"
echo ""

# Step 7: SendGrid setup
echo "📧 Email Service Setup"
echo "===================="
echo "1. Sign up at https://sendgrid.com (free tier: 100 emails/day)"
echo "2. Create API key with 'Mail Send' permissions"
echo "3. Add your SendGrid API key to .env file"
echo "4. Verify sender identity for your domain"
echo ""

# Step 8: Production deployment
echo "🚀 Production Deployment"
echo "======================="
echo "Once all credentials are configured, run:"
echo "   chmod +x deploy.sh"
echo "   ./deploy.sh"
echo ""

# Step 9: Testing
echo "🧪 Testing Your Setup"
echo "===================="
echo "1. Start the service:"
echo "   docker-compose up -d"
echo ""
echo "2. Run tests:"
echo "   python test_payment_flow.py"
echo ""
echo "3. Test payment flow:"
echo "   curl https://pay.synapse-lang.com/api/products"
echo ""

# Step 10: Monitoring setup
echo "📊 Monitoring & Analytics"
echo "========================"
echo "Set up monitoring with these tools:"
echo "• Uptime monitoring: UptimeRobot, Pingdom"
echo "• Error tracking: Sentry"
echo "• Analytics: Google Analytics"
echo "• Server monitoring: New Relic, DataDog"
echo ""

# Step 11: Security checklist
echo "🔒 Security Checklist"
echo "===================="
echo "□ API keys stored securely in environment variables"
echo "□ Webhook signatures properly verified"
echo "□ SSL certificates installed and auto-renewing"
echo "□ Firewall configured (ports 80, 443, 22 only)"
echo "□ Database passwords changed from defaults"
echo "□ Rate limiting enabled"
echo "□ Log monitoring configured"
echo "□ Regular backups scheduled"
echo ""

print_status "Production setup guide complete!"
echo ""
echo "🎯 Next Steps:"
echo "1. Complete the manual steps outlined above"
echo "2. Test all integrations thoroughly"
echo "3. Run ./deploy.sh to go live"
echo ""
echo "💰 Your payment system will be ready to accept:"
echo "   • Bitcoin (BTC)"
echo "   • Ethereum (ETH)"  
echo "   • Litecoin (LTC)"
echo "   • Bitcoin Cash (BCH)"
echo "   • USD Coin (USDC)"
echo "   • DAI Stablecoin"
echo ""
echo "🌐 Access your payment system at: https://pay.synapse-lang.com"
echo ""
echo "Need help? Contact: support@synapse-lang.com"