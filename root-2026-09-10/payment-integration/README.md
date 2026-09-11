# 🪙 Synapse Language - Cryptocurrency Payment Integration

Complete cryptocurrency payment system for Synapse Language using Coinbase Commerce.

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Clone the repository
cd synapse-lang/payment-integration

# Copy environment file
cp .env.example .env

# Edit .env with your API keys
nano .env
```

### 2. Required API Keys

Sign up for these services and add keys to `.env`:

- **Coinbase Commerce**: https://commerce.coinbase.com
- **SendGrid**: https://sendgrid.com (for email notifications)
- **PostgreSQL**: Database for license storage

### 3. Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Start development server
python payment_service.py
```

Visit: http://localhost:5000

### 4. Production Deployment

```bash
# Make deployment script executable
chmod +x deploy.sh

# Set environment variables
export COINBASE_COMMERCE_API_KEY="your_key"
export COINBASE_COMMERCE_WEBHOOK_SECRET="your_secret"
export POSTGRES_PASSWORD="secure_password"
export SENDGRID_API_KEY="your_sendgrid_key"

# Deploy
./deploy.sh
```

## 📋 Features

### ✅ Supported Cryptocurrencies
- Bitcoin (BTC)
- Ethereum (ETH)
- Litecoin (LTC)
- Bitcoin Cash (BCH)
- USD Coin (USDC)
- DAI Stablecoin

### 🛍️ Products Available
- **Professional License**: $499/year
- **Enterprise License**: $4,999/year  
- **VS Code Extension Pro**: $29 (lifetime)
- **Advanced Tutorials**: $99 (lifetime)
- **Consulting Hour**: $200

### 🔧 System Components
- **Payment API**: Flask-based REST API
- **Database**: PostgreSQL for license storage
- **Email Service**: SendGrid integration
- **Webhooks**: Coinbase Commerce event handling
- **Frontend**: Responsive payment UI
- **Monitoring**: Health checks and logging

## 🏗️ Architecture

```
User → Website → Coinbase Commerce → Webhook → Backend → Database
                     ↓
               Payment Confirmation → License Generation → Email Delivery
```

## 📁 File Structure

```
payment-integration/
├── payment_service.py      # Main Flask application
├── email_service.py        # Email notification service
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker container config
├── docker-compose.yml     # Multi-service orchestration
├── nginx.conf             # Reverse proxy configuration
├── init.sql              # Database schema
├── deploy.sh             # Production deployment script
├── test_payment_flow.py  # Comprehensive test suite
└── coinbase-setup.md     # Detailed setup guide
```

## 🧪 Testing

### Run Test Suite

```bash
# Start local service
python payment_service.py

# Run tests (in another terminal)
python test_payment_flow.py
```

### Test Coverage
- ✅ Service health checks
- ✅ Product listing validation
- ✅ Charge creation process
- ✅ Webhook signature verification
- ✅ License validation system
- ✅ Error handling scenarios
- ✅ Performance benchmarking

## 📊 API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/products` | List available products |
| POST | `/api/create-charge` | Create cryptocurrency charge |
| GET | `/api/charge/{id}` | Get charge status |
| POST | `/api/validate-license` | Validate license key |
| POST | `/api/webhooks/coinbase` | Coinbase webhook handler |

### Example Usage

```javascript
// Create a charge
const response = await fetch('/api/create-charge', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        product_type: 'professional',
        customer_email: 'user@example.com',
        customer_name: 'John Doe'
    })
});

const data = await response.json();
// Redirect to: data.hosted_url
```

## 🔐 Security Features

### Payment Security
- ✅ Webhook signature verification
- ✅ HTTPS/TLS encryption
- ✅ Rate limiting protection
- ✅ Input validation & sanitization
- ✅ SQL injection prevention

### Infrastructure Security
- ✅ Firewall configuration
- ✅ SSL certificate automation
- ✅ Database access controls
- ✅ Container security hardening
- ✅ Log monitoring & rotation

## 🚨 Monitoring & Maintenance

### Health Checks
```bash
# Service status
curl https://pay.synapse-lang.com/health

# Database connection
docker-compose exec postgres psql -U postgres -c "SELECT 1;"

# View logs
docker-compose logs -f payment-service
```

### Backup & Recovery
```bash
# Database backup
docker-compose exec postgres pg_dump -U postgres synapse_payments > backup.sql

# Restore database
docker-compose exec -T postgres psql -U postgres synapse_payments < backup.sql
```

## 💰 Revenue Analytics

### Payment Tracking
- Real-time payment notifications
- Revenue by cryptocurrency type
- Geographic payment distribution
- Conversion rate optimization
- Monthly/yearly revenue trends

### License Management  
- Active license tracking
- Expiration monitoring
- Usage analytics
- Customer lifecycle management

## 🌐 Integration

### Website Integration
```html
<!-- Add to your website -->
<a href="https://pay.synapse-lang.com" class="crypto-payment-btn">
    🪙 Pay with Crypto
</a>
```

### Synapse Language Integration
```python
# Validate license in your application
import requests

def validate_synapse_license(license_key):
    response = requests.post('https://pay.synapse-lang.com/api/validate-license', 
                           json={'license_key': license_key})
    return response.json()['valid']
```

## 🔧 Configuration

### Environment Variables

```bash
# Required
COINBASE_COMMERCE_API_KEY=your_api_key
COINBASE_COMMERCE_WEBHOOK_SECRET=your_webhook_secret
SENDGRID_API_KEY=your_sendgrid_key
POSTGRES_PASSWORD=secure_password

# Optional
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://localhost:6379
LOG_LEVEL=INFO
```

### Docker Configuration

```yaml
# docker-compose.override.yml for custom settings
version: '3.8'
services:
  payment-service:
    environment:
      - CUSTOM_SETTING=value
    ports:
      - "5001:5000"  # Custom port
```

## 🆘 Troubleshooting

### Common Issues

**Service won't start**
```bash
# Check logs
docker-compose logs payment-service

# Verify environment variables
env | grep COINBASE

# Test database connection
docker-compose exec postgres psql -U postgres
```

**Payments not processing**
```bash
# Check webhook configuration
curl -X POST https://pay.synapse-lang.com/api/webhooks/coinbase \
  -H "X-CC-Webhook-Signature: test" \
  -d '{"type": "test"}'

# Verify API keys
python -c "import os; print('API Key set:', bool(os.getenv('COINBASE_COMMERCE_API_KEY')))"
```

**Email not sending**
```bash
# Test SendGrid configuration
python -c "
import sendgrid
sg = sendgrid.SendGridAPIClient(api_key='your_key')
print('SendGrid configured correctly')
"
```

## 📞 Support

- **Documentation**: https://docs.synapse-lang.com/payments
- **Issues**: https://github.com/synapse-lang/payment-integration/issues
- **Email**: support@synapse-lang.com
- **Discord**: https://discord.gg/synapse-lang

## 📜 License

MIT License - see [LICENSE](../LICENSE) for details.

---

**Ready to accept cryptocurrency payments for Synapse Language! 🪙⚡**

For detailed setup instructions, see [coinbase-setup.md](./coinbase-setup.md)