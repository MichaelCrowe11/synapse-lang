# 🚀 Synapse Language Payment System - Production Deployment Checklist

## Pre-Deployment Requirements

### ✅ Server Setup
- [ ] **Cloud Server**: DigitalOcean, AWS EC2, or similar (2GB+ RAM, 20GB+ storage)
- [ ] **Operating System**: Ubuntu 20.04+ or similar Linux distribution
- [ ] **Domain**: `pay.synapse-lang.com` purchased and DNS configured
- [ ] **SSH Access**: Root/sudo access to server

### ✅ Required Accounts & API Keys
- [x] **Coinbase Commerce**: Account created, API keys generated
- [ ] **SendGrid**: Account created for email delivery (optional but recommended)
- [ ] **SSL Certificate**: Let's Encrypt (automatic via deployment script)

## 🎯 **STEP 1: Deploy to Production Server**

### Option A: Automated Deployment (Recommended)
```bash
# On your production server:
git clone https://github.com/your-username/synapse-lang.git
cd synapse-lang/payment-integration

# Copy your production environment
cp .env.production .env

# Run automated deployment
chmod +x deploy.sh
./deploy.sh
```

### Option B: Manual Deployment
```bash
# 1. Install dependencies
sudo apt-get update
sudo apt-get install -y docker.io docker-compose nginx certbot python3-certbot-nginx

# 2. Start services
docker-compose up -d

# 3. Configure SSL
sudo certbot --nginx -d pay.synapse-lang.com
```

### Verify Deployment
```bash
# Check if services are running
docker-compose ps

# Test API endpoint
curl https://pay.synapse-lang.com/api/products

# Check logs
docker-compose logs -f payment-service
```

---

## 🌐 **STEP 2: Configure Domain (pay.synapse-lang.com)**

### DNS Configuration
```bash
# Add these DNS records to your domain provider:
Type: A
Name: pay
Value: YOUR_SERVER_IP_ADDRESS
TTL: 300

# Optional: Add CNAME for www
Type: CNAME  
Name: www.pay
Value: pay.synapse-lang.com
TTL: 300
```

### SSL Certificate Setup
```bash
# Automatic via deployment script, or manually:
sudo certbot --nginx -d pay.synapse-lang.com --email admin@synapse-lang.com --agree-tos --non-interactive
```

### Nginx Configuration Check
```bash
# Test configuration
sudo nginx -t

# Reload if successful
sudo systemctl reload nginx
```

---

## 📡 **STEP 3: Set up Coinbase Commerce Webhook**

### 1. Access Coinbase Commerce Dashboard
- Go to: https://commerce.coinbase.com/dashboard
- Login with your account
- Navigate to **Settings → Webhooks**

### 2. Create New Webhook
```
Webhook URL: https://pay.synapse-lang.com/api/webhooks/coinbase
Description: Synapse Language Payment Notifications

Events to Subscribe:
✅ charge:confirmed
✅ charge:failed  
✅ charge:pending
✅ charge:delayed (recommended)
✅ charge:resolved (recommended)

Webhook Secret: (Use the secret from your .env file)
Sw3+wuhe84CgNRToB+CmS716P0mxOWi+/Wsh/XKIexams8P6XVa4M2gfKvZ5KrEmDmboYnoEl0Mds/JNjzGHfg==
```

### 3. Test Webhook
```bash
# Coinbase will send a test event - check your logs:
docker-compose logs -f payment-service | grep webhook

# Or test manually:
curl -X POST https://pay.synapse-lang.com/api/webhooks/coinbase \
  -H "Content-Type: application/json" \
  -H "X-CC-Webhook-Signature: test" \
  -d '{"type": "test", "data": {}}'
```

---

## 🎉 **STEP 4: Go Live with Crypto Payments!**

### Final Verification
```bash
# Run complete validation
python validate_setup.py

# Test payment flow end-to-end  
python test_payment_flow.py

# Check all services are healthy
curl https://pay.synapse-lang.com/health
```

### 🔧 Integration with Synapse Language Website

Add payment buttons to your main website:

```html
<!-- Add to synapse-lang.com -->
<div class="crypto-payment-section">
    <h3>💰 Pay with Cryptocurrency</h3>
    <p>Accept Bitcoin, Ethereum, USDC and more!</p>
    
    <a href="https://pay.synapse-lang.com?product=professional" 
       class="crypto-pay-btn professional">
        🚀 Professional License - $499
        <small>Pay with BTC, ETH, USDC</small>
    </a>
    
    <a href="https://pay.synapse-lang.com?product=enterprise" 
       class="crypto-pay-btn enterprise">
        💎 Enterprise License - $4,999  
        <small>Pay with BTC, ETH, USDC</small>
    </a>
    
    <a href="https://pay.synapse-lang.com?product=vscode_extension" 
       class="crypto-pay-btn extension">
        🔧 VS Code Extension - $29
        <small>Pay with BTC, ETH, USDC</small>
    </a>
</div>

<style>
.crypto-pay-btn {
    display: block;
    background: linear-gradient(135deg, #7A5CFF, #43E5FF);
    color: white;
    padding: 15px 25px;
    margin: 10px 0;
    text-decoration: none;
    border-radius: 8px;
    font-weight: bold;
    transition: transform 0.3s;
}

.crypto-pay-btn:hover {
    transform: translateY(-2px);
}

.crypto-pay-btn small {
    display: block;
    opacity: 0.8;
    font-size: 12px;
}
</style>
```

### 📊 Monitor Your Payments

**Real-time Monitoring:**
```bash
# Watch payment logs
tail -f logs/payment_service.log

# Monitor database
docker-compose exec postgres psql -U postgres -c "
SELECT product_type, COUNT(*), SUM(price_paid_usd) as total_revenue 
FROM licenses 
WHERE active=true 
GROUP BY product_type;
"

# Check system health
curl https://pay.synapse-lang.com/api/products | jq
```

**Analytics Dashboard:**
```bash
# Get payment analytics
curl https://pay.synapse-lang.com/api/analytics
```

---

## 🎯 **Success Indicators**

You'll know your crypto payment system is live when:

✅ **Website accessible**: https://pay.synapse-lang.com loads  
✅ **API responsive**: `/api/products` returns product data  
✅ **SSL working**: Green lock in browser  
✅ **Webhook configured**: Coinbase dashboard shows active webhook  
✅ **Test payment**: Can create and view charges  
✅ **Email delivery**: License emails sent successfully  
✅ **Database active**: License data stored correctly  

---

## 🚨 **Troubleshooting**

**Service won't start:**
```bash
docker-compose logs payment-service
# Check .env file has all required variables
```

**Domain not resolving:**
```bash
nslookup pay.synapse-lang.com
# Check DNS propagation (can take up to 48 hours)
```

**Webhook failing:**
```bash
# Check webhook signature verification
# Verify URL is publicly accessible
curl -I https://pay.synapse-lang.com/api/webhooks/coinbase
```

**SSL issues:**
```bash
sudo certbot renew --dry-run
# Check certificate validity
```

---

## 🎉 **You're Live!**

Once deployed, your system will automatically:

🪙 **Accept cryptocurrencies**: Bitcoin, Ethereum, Litecoin, USDC, DAI  
📧 **Send license emails**: Professional HTML templates  
🔐 **Generate licenses**: Unique keys for each purchase  
📊 **Track revenue**: Real-time analytics  
🛡️ **Secure processing**: Webhook verification, rate limiting  
🚀 **Scale automatically**: Docker + Nginx handles traffic  

**Congratulations! Synapse Language now accepts cryptocurrency payments!** 💰⚡

---

## 📞 **Support**

- **Technical Issues**: Check logs first, then contact support
- **Payment Questions**: Coinbase Commerce support  
- **Integration Help**: Synapse Language documentation
- **Emergency**: Server monitoring alerts + on-call support

**Happy crypto payments!** 🚀🪙