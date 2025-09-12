# 🔗 Synapse Language Payment Integration Guide

Step-by-step guide to integrate cryptocurrency payments into your Synapse Language ecosystem.

## 🏁 Quick Setup (5 minutes)

### 1. Get API Keys

**Coinbase Commerce** (Required)
1. Visit https://commerce.coinbase.com
2. Create account and verify business
3. Navigate to Settings → API Keys
4. Generate API key and webhook secret
5. Note both values

**SendGrid** (Optional - for emails)
1. Visit https://sendgrid.com 
2. Create free account (100 emails/day)
3. Go to Settings → API Keys
4. Create API key with "Mail Send" permissions

### 2. Environment Configuration

```bash
cd synapse-lang/payment-integration
cp .env.example .env
```

Edit `.env`:
```bash
# Required for production
COINBASE_COMMERCE_API_KEY=your_coinbase_api_key_here
COINBASE_COMMERCE_WEBHOOK_SECRET=your_webhook_secret_here

# Optional
SENDGRID_API_KEY=your_sendgrid_key_here
FROM_EMAIL=noreply@yourdomain.com
```

### 3. Start Service

**Development:**
```bash
chmod +x start_local.sh
./start_local.sh
```

**Production:**
```bash
chmod +x deploy.sh
./deploy.sh
```

### 4. Test Integration

```bash
# Run test suite
python test_payment_flow.py

# Manual test
curl http://localhost:5000/api/products
```

## 🌐 Website Integration

### Add Payment Button to Your Site

```html
<!-- Simple integration -->
<a href="https://pay.synapse-lang.com" 
   class="synapse-crypto-pay" 
   data-product="professional">
   🪙 Pay with Crypto - $499
</a>

<!-- Advanced integration with JavaScript -->
<button onclick="openCryptoPayment('professional')">
   Buy Professional License
</button>

<script>
async function openCryptoPayment(productType) {
    const response = await fetch('https://pay.synapse-lang.com/api/create-charge', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            product_type: productType,
            customer_email: userEmail, // from your system
            customer_name: userName
        })
    });
    
    const data = await response.json();
    if (data.success) {
        window.location.href = data.hosted_url;
    }
}
</script>
```

### Custom Payment Flow

```javascript
class SynapsePayments {
    constructor(baseUrl = 'https://pay.synapse-lang.com') {
        this.baseUrl = baseUrl;
    }
    
    async getProducts() {
        const response = await fetch(`${this.baseUrl}/api/products`);
        return response.json();
    }
    
    async createCharge(productType, customerEmail, customerName) {
        const response = await fetch(`${this.baseUrl}/api/create-charge`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                product_type: productType,
                customer_email: customerEmail,
                customer_name: customerName
            })
        });
        
        return response.json();
    }
    
    async validateLicense(licenseKey) {
        const response = await fetch(`${this.baseUrl}/api/validate-license`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ license_key: licenseKey })
        });
        
        return response.json();
    }
}

// Usage
const payments = new SynapsePayments();
const charge = await payments.createCharge('professional', 'user@example.com', 'John Doe');
```

## 🔧 Synapse Language Integration

### License Validation

```python
# synapse_license_validator.py
import requests
import os
from typing import Tuple, Dict

class SynapseLicenseValidator:
    def __init__(self, api_url: str = "https://pay.synapse-lang.com"):
        self.api_url = api_url
        self.license_cache = {}
    
    def validate_license(self, license_key: str) -> Tuple[bool, Dict]:
        """Validate a Synapse Language license key."""
        
        # Check cache first
        if license_key in self.license_cache:
            cached_result = self.license_cache[license_key]
            if cached_result['cached_at'] + 3600 > time.time():  # 1 hour cache
                return cached_result['valid'], cached_result['data']
        
        try:
            response = requests.post(
                f"{self.api_url}/api/validate-license",
                json={"license_key": license_key},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                is_valid = result.get('valid', False)
                license_data = result.get('license_data', {})
                
                # Cache result
                self.license_cache[license_key] = {
                    'valid': is_valid,
                    'data': license_data,
                    'cached_at': time.time()
                }
                
                return is_valid, license_data
            else:
                return False, {'error': f'Validation service error: {response.status_code}'}
                
        except Exception as e:
            return False, {'error': f'License validation failed: {str(e)}'}
    
    def get_license_info(self, license_key: str) -> Dict:
        """Get detailed license information."""
        is_valid, license_data = self.validate_license(license_key)
        
        if is_valid:
            return {
                'valid': True,
                'product_type': license_data.get('product_type'),
                'expires_at': license_data.get('expires_at'),
                'customer_email': license_data.get('customer_email'),
                'features_enabled': self._get_enabled_features(license_data.get('product_type'))
            }
        else:
            return {'valid': False, 'error': license_data.get('error', 'Invalid license')}
    
    def _get_enabled_features(self, product_type: str) -> Dict[str, bool]:
        """Map product types to enabled features."""
        feature_matrix = {
            'professional': {
                'gpu_acceleration': True,
                'commercial_use': True,
                'priority_support': True,
                'quantum_modules': False,
                'unlimited_resources': False
            },
            'enterprise': {
                'gpu_acceleration': True,
                'commercial_use': True,
                'priority_support': True,
                'quantum_modules': True,
                'unlimited_resources': True
            },
            'vscode_extension': {
                'advanced_debugging': True,
                'profiling_tools': True,
                'cloud_integration': True
            }
        }
        
        return feature_matrix.get(product_type, {})

# Usage in Synapse Language core
validator = SynapseLicenseValidator()

def check_professional_features():
    license_key = os.getenv('SYNAPSE_LICENSE_KEY')
    if not license_key:
        return False
    
    is_valid, license_data = validator.validate_license(license_key)
    return is_valid and license_data.get('product_type') in ['professional', 'enterprise']
```

### Feature Gating

```python
# synapse_lang/core/license_manager.py
import functools
from typing import Callable, Any

def requires_license(product_type: str = None, feature: str = None):
    """Decorator to require valid license for features."""
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            license_key = os.getenv('SYNAPSE_LICENSE_KEY')
            
            if not license_key:
                raise LicenseError(f"License required for {func.__name__}. Get yours at https://pay.synapse-lang.com")
            
            validator = SynapseLicenseValidator()
            is_valid, license_data = validator.validate_license(license_key)
            
            if not is_valid:
                raise LicenseError(f"Invalid license. Please check your key or renew at https://pay.synapse-lang.com")
            
            # Check product type
            if product_type and license_data.get('product_type') != product_type:
                if not (product_type == 'professional' and license_data.get('product_type') == 'enterprise'):
                    raise LicenseError(f"Feature requires {product_type} license. Upgrade at https://pay.synapse-lang.com")
            
            # Check specific feature
            if feature:
                features = validator._get_enabled_features(license_data.get('product_type'))
                if not features.get(feature, False):
                    raise LicenseError(f"Feature '{feature}' not available in your license. Upgrade at https://pay.synapse-lang.com")
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

# Usage examples
@requires_license(product_type='professional')
def enable_gpu_acceleration():
    """GPU acceleration requires Professional+ license."""
    pass

@requires_license(feature='quantum_modules')
def quantum_circuit_builder():
    """Quantum features require Enterprise license."""
    pass
```

## 📧 Email Notifications

### Webhook Integration

Set up webhook endpoint in Coinbase Commerce:
```
Webhook URL: https://pay.synapse-lang.com/api/webhooks/coinbase
Events: charge:confirmed, charge:failed
```

### Custom Email Templates

```python
# custom_email_templates.py
def create_custom_license_email(customer_data):
    return f"""
    <html>
    <body style="font-family: Arial, sans-serif;">
        <h1 style="color: #7A5CFF;">Welcome to Synapse Language!</h1>
        
        <p>Hi {customer_data['name']},</p>
        
        <p>Your cryptocurrency payment has been confirmed. Here are your license details:</p>
        
        <div style="background: #f0f8ff; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h3>License Information</h3>
            <p><strong>Product:</strong> {customer_data['product_name']}</p>
            <p><strong>License Key:</strong> <code>{customer_data['license_key']}</code></p>
            <p><strong>Expires:</strong> {customer_data['expires_at']}</p>
        </div>
        
        <h3>Getting Started</h3>
        <ol>
            <li>Install: <code>pip install synapse-lang</code></li>
            <li>Set license: <code>export SYNAPSE_LICENSE_KEY={customer_data['license_key']}</code></li>
            <li>Start coding with quantum features!</li>
        </ol>
        
        <p>Questions? Reply to this email or visit our <a href="https://docs.synapse-lang.com">documentation</a>.</p>
        
        <p>Welcome to the future of scientific computing!</p>
        <p>The Synapse Language Team</p>
    </body>
    </html>
    """
```

## 🚀 Production Deployment

### Domain Setup

1. **Purchase domain** (e.g., pay.synapse-lang.com)
2. **Point A record** to your server IP
3. **Run deployment script**:
   ```bash
   ./deploy.sh
   ```

### SSL Certificate

Automatic via Let's Encrypt:
```bash
# Included in deploy.sh
sudo certbot --nginx -d pay.synapse-lang.com
```

### Monitoring

```bash
# Check service health
curl https://pay.synapse-lang.com/health

# View logs
docker-compose logs -f payment-service

# Monitor database
docker-compose exec postgres psql -U postgres -c "SELECT COUNT(*) FROM licenses;"
```

## 📊 Analytics Integration

### Revenue Tracking

```python
# analytics.py
def get_payment_analytics():
    with open('licenses.json', 'r') as f:
        licenses = json.load(f)
    
    revenue_by_product = {}
    total_revenue = 0
    
    for license in licenses:
        product = license['product_type']
        price = license['price_paid_usd']
        
        revenue_by_product[product] = revenue_by_product.get(product, 0) + price
        total_revenue += price
    
    return {
        'total_revenue_usd': total_revenue,
        'revenue_by_product': revenue_by_product,
        'total_licenses': len(licenses),
        'active_licenses': len([l for l in licenses if l['active']])
    }
```

### Customer Success

```python
def track_license_usage():
    """Track how customers are using their licenses."""
    usage_data = {
        'activation_rate': calculate_activation_rate(),
        'feature_adoption': track_feature_usage(),
        'renewal_probability': predict_renewals(),
        'support_tickets': count_support_requests()
    }
    
    return usage_data
```

## 🛡️ Security Best Practices

### 1. Environment Variables
```bash
# Never commit these to git
export COINBASE_COMMERCE_API_KEY="live_key_here"
export COINBASE_COMMERCE_WEBHOOK_SECRET="secret_here"
export SENDGRID_API_KEY="sg.key_here"
```

### 2. Webhook Security
```python
# Always verify webhook signatures
def verify_coinbase_webhook(payload, signature, secret):
    computed_signature = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(computed_signature, signature)
```

### 3. Rate Limiting
```python
# Implement rate limiting
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/create-charge', methods=['POST'])
@limiter.limit("10 per minute")
def create_charge():
    # Protected endpoint
    pass
```

## 🆘 Troubleshooting

### Common Issues

**Payments not processing:**
```bash
# Check webhook configuration
curl -X POST https://commerce.coinbase.com/webhooks \
  -H "X-CC-Api-Key: YOUR_API_KEY" \
  -d '{"url": "https://pay.synapse-lang.com/api/webhooks/coinbase"}'
```

**License validation failing:**
```bash
# Test license validation
curl -X POST http://localhost:5000/api/validate-license \
  -H "Content-Type: application/json" \
  -d '{"license_key": "SYN-SAMPLE123456"}'
```

**Email not sending:**
```bash
# Test SendGrid configuration
python -c "
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content

sg = sendgrid.SendGridAPIClient(api_key='YOUR_KEY')
message = Mail(
    from_email='test@yourdomain.com',
    to_emails='test@example.com',
    subject='Test',
    html_content='Test email'
)
response = sg.send(message)
print(f'Status: {response.status_code}')
"
```

## 📞 Support

- **Documentation**: https://docs.synapse-lang.com/payments
- **GitHub Issues**: https://github.com/synapse-lang/synapse-lang/issues
- **Email**: support@synapse-lang.com
- **Discord**: Join our community for real-time help

---

**Ready to start accepting crypto payments! 🚀💰**

Need help? Our team is available 24/7 to assist with integration.