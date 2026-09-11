#!/usr/bin/env python3
"""
Synapse Language Cryptocurrency Payment Service
Handles Coinbase Commerce integration for crypto payments
"""

import hashlib
import hmac
import json
import os
import uuid
from datetime import datetime, timedelta

import requests
from flask import Flask, jsonify, render_template_string, request
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
class Config:
    COINBASE_COMMERCE_API_KEY = os.getenv("COINBASE_COMMERCE_API_KEY")
    COINBASE_COMMERCE_WEBHOOK_SECRET = os.getenv("COINBASE_COMMERCE_WEBHOOK_SECRET")
    COINBASE_API_BASE = "https://api.commerce.coinbase.com"

    # Product pricing in USD
    PRODUCTS = {
        "professional": {
            "name": "Synapse Language Professional",
            "price": 499.00,
            "duration_days": 365,
            "description": "GPU acceleration, commercial use, priority support"
        },
        "enterprise": {
            "name": "Synapse Language Enterprise",
            "price": 4999.00,
            "duration_days": 365,
            "description": "Unlimited resources, quantum modules, custom development"
        },
        "vscode_extension": {
            "name": "Synapse VS Code Extension Pro",
            "price": 29.00,
            "duration_days": 999999,  # Lifetime
            "description": "Advanced debugging, profiling, cloud integration"
        },
        "tutorials": {
            "name": "Advanced Synapse Tutorials",
            "price": 99.00,
            "duration_days": 999999,  # Lifetime access
            "description": "Complete video course series"
        },
        "consulting": {
            "name": "Synapse Consulting Hour",
            "price": 200.00,
            "duration_days": 30,  # Must be used within 30 days
            "description": "1 hour expert consultation"
        }
    }

class SynapsePaymentService:
    """Main payment service class for handling crypto payments."""

    def __init__(self):
        self.api_key = Config.COINBASE_COMMERCE_API_KEY
        self.webhook_secret = Config.COINBASE_COMMERCE_WEBHOOK_SECRET
        self.base_url = Config.COINBASE_API_BASE

        if not self.api_key:
            raise ValueError("COINBASE_COMMERCE_API_KEY environment variable is required")

    def create_charge(self, product_type: str, customer_email: str,
                     customer_name: str = None) -> dict:
        """Create a new cryptocurrency charge."""

        if product_type not in Config.PRODUCTS:
            raise ValueError(f"Invalid product type: {product_type}")

        product = Config.PRODUCTS[product_type]

        # Create charge data
        charge_data = {
            "name": product["name"],
            "description": product["description"],
            "local_price": {
                "amount": str(product["price"]),
                "currency": "USD"
            },
            "pricing_type": "fixed_price",
            "requested_info": ["email"],
            "metadata": {
                "product_type": product_type,
                "customer_email": customer_email,
                "customer_name": customer_name or "",
                "synapse_version": "2.0.0",
                "created_at": datetime.utcnow().isoformat()
            },
            "redirect_url": f"https://synapse-lang.com/payment-success?product={product_type}",
            "cancel_url": "https://synapse-lang.com/payment-cancel"
        }

        # Make API request to Coinbase Commerce
        headers = {
            "Content-Type": "application/json",
            "X-CC-Api-Key": self.api_key,
            "X-CC-Version": "2018-03-22"
        }

        response = requests.post(
            f"{self.base_url}/charges",
            headers=headers,
            json=charge_data
        )

        if response.status_code != 201:
            raise Exception(f"Failed to create charge: {response.text}")

        return response.json()["data"]

    def get_charge(self, charge_id: str) -> dict:
        """Retrieve charge information."""
        headers = {
            "X-CC-Api-Key": self.api_key,
            "X-CC-Version": "2018-03-22"
        }

        response = requests.get(
            f"{self.base_url}/charges/{charge_id}",
            headers=headers
        )

        if response.status_code != 200:
            raise Exception(f"Failed to get charge: {response.text}")

        return response.json()["data"]

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Verify Coinbase Commerce webhook signature."""
        if not self.webhook_secret:
            return False

        try:
            computed_signature = hmac.new(
                self.webhook_secret.encode(),
                payload,
                hashlib.sha256
            ).hexdigest()

            return hmac.compare_digest(computed_signature, signature)
        except Exception:
            return False

class LicenseManager:
    """Manages Synapse Language licenses."""

    def __init__(self):
        self.license_file = "licenses.json"

    def generate_license_key(self, product_type: str, customer_email: str) -> str:
        """Generate a unique license key."""
        # Create a deterministic but secure license key
        timestamp = str(int(datetime.utcnow().timestamp()))
        data = f"{product_type}:{customer_email}:{timestamp}:{uuid.uuid4()}"
        hash_obj = hashlib.sha256(data.encode())
        license_key = f"SYN-{hash_obj.hexdigest()[:16].upper()}"
        return license_key

    def create_license(self, charge_id: str, product_type: str,
                      customer_email: str, customer_name: str = None) -> str:
        """Create and store a new license."""

        if product_type not in Config.PRODUCTS:
            raise ValueError(f"Invalid product type: {product_type}")

        product = Config.PRODUCTS[product_type]
        license_key = self.generate_license_key(product_type, customer_email)

        # Calculate expiration date
        expires_at = datetime.utcnow() + timedelta(days=product["duration_days"])

        license_data = {
            "license_key": license_key,
            "charge_id": charge_id,
            "product_type": product_type,
            "product_name": product["name"],
            "customer_email": customer_email,
            "customer_name": customer_name,
            "price_paid_usd": product["price"],
            "issued_at": datetime.utcnow().isoformat(),
            "expires_at": expires_at.isoformat(),
            "active": True,
            "usage_count": 0
        }

        # Store license
        self._save_license(license_data)

        return license_key

    def _save_license(self, license_data: dict):
        """Save license to storage."""
        try:
            with open(self.license_file) as f:
                licenses = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            licenses = []

        licenses.append(license_data)

        with open(self.license_file, "w") as f:
            json.dump(licenses, f, indent=2)

    def validate_license(self, license_key: str) -> tuple[bool, str, dict]:
        """Validate a license key."""
        try:
            with open(self.license_file) as f:
                licenses = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return False, "License database not found", {}

        # Find license
        license_data = None
        for license_info in licenses:
            if license_info["license_key"] == license_key:
                license_data = license_info
                break

        if not license_data:
            return False, "Invalid license key", {}

        # Check if active
        if not license_data.get("active", False):
            return False, "License has been deactivated", license_data

        # Check expiration
        expires_at = datetime.fromisoformat(license_data["expires_at"])
        if datetime.utcnow() > expires_at:
            return False, "License has expired", license_data

        return True, "License is valid", license_data

# Initialize services
payment_service = SynapsePaymentService()
license_manager = LicenseManager()

# Routes
@app.route("/")
def index():
    """Payment page."""
    return render_template_string(PAYMENT_PAGE_HTML)

@app.route("/api/products", methods=["GET"])
def get_products():
    """Get available products for purchase."""
    return jsonify({
        "products": Config.PRODUCTS,
        "supported_cryptocurrencies": [
            "Bitcoin (BTC)", "Ethereum (ETH)", "Litecoin (LTC)",
            "Bitcoin Cash (BCH)", "USD Coin (USDC)", "DAI"
        ]
    })

@app.route("/api/create-charge", methods=["POST"])
def create_charge():
    """Create a new cryptocurrency charge."""
    try:
        data = request.get_json()

        # Validate input
        required_fields = ["product_type", "customer_email"]
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Create charge
        charge = payment_service.create_charge(
            product_type=data["product_type"],
            customer_email=data["customer_email"],
            customer_name=data.get("customer_name")
        )

        return jsonify({
            "success": True,
            "charge_id": charge["id"],
            "hosted_url": charge["hosted_url"],
            "expires_at": charge["expires_at"],
            "addresses": charge.get("addresses", {}),
            "pricing": charge.get("pricing", {})
        })

    except Exception as e:
        app.logger.error(f"Charge creation error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/webhooks/coinbase", methods=["POST"])
def coinbase_webhook():
    """Handle Coinbase Commerce webhooks."""
    try:
        # Verify signature
        signature = request.headers.get("X-CC-Webhook-Signature", "")
        if not payment_service.verify_webhook_signature(request.data, signature):
            app.logger.warning("Invalid webhook signature")
            return jsonify({"error": "Invalid signature"}), 401

        # Parse event
        event = request.get_json()
        event_type = event.get("type")
        event_data = event.get("data", {})

        app.logger.info(f"Received webhook: {event_type} for charge {event_data.get('id')}")

        # Handle different event types
        if event_type == "charge:confirmed":
            return handle_payment_confirmed(event_data)
        elif event_type == "charge:failed":
            return handle_payment_failed(event_data)
        elif event_type == "charge:pending":
            return handle_payment_pending(event_data)
        elif event_type == "charge:resolved":
            return handle_payment_resolved(event_data)

        return jsonify({"status": "received"})

    except Exception as e:
        app.logger.error(f"Webhook processing error: {str(e)}")
        return jsonify({"error": "Processing failed"}), 500

def handle_payment_confirmed(charge_data: dict):
    """Handle confirmed payment."""
    try:
        charge_id = charge_data["id"]
        metadata = charge_data.get("metadata", {})

        customer_email = metadata.get("customer_email")
        customer_name = metadata.get("customer_name")
        product_type = metadata.get("product_type")

        if not all([customer_email, product_type]):
            raise ValueError("Missing required metadata")

        # Create license
        license_key = license_manager.create_license(
            charge_id=charge_id,
            product_type=product_type,
            customer_email=customer_email,
            customer_name=customer_name
        )

        # Send license email (in production, use proper email service)
        send_license_email(customer_email, product_type, license_key)

        app.logger.info(f"License created for {customer_email}: {license_key}")

        return jsonify({"status": "processed", "license_key": license_key})

    except Exception as e:
        app.logger.error(f"Payment confirmation error: {str(e)}")
        return jsonify({"error": "Processing failed"}), 500

def handle_payment_failed(charge_data: dict):
    """Handle failed payment."""
    charge_id = charge_data["id"]
    app.logger.info(f"Payment failed for charge: {charge_id}")
    return jsonify({"status": "failed"})

def handle_payment_pending(charge_data: dict):
    """Handle pending payment."""
    charge_id = charge_data["id"]
    app.logger.info(f"Payment pending for charge: {charge_id}")
    return jsonify({"status": "pending"})

def handle_payment_resolved(charge_data: dict):
    """Handle resolved payment."""
    charge_id = charge_data["id"]
    app.logger.info(f"Payment resolved for charge: {charge_id}")
    return jsonify({"status": "resolved"})

def send_license_email(customer_email: str, product_type: str, license_key: str):
    """Send license key via email."""
    # In production, integrate with SendGrid, AWS SES, etc.
    product_name = Config.PRODUCTS[product_type]["name"]

    app.logger.info(f"License email sent to {customer_email}")
    app.logger.info(f"Product: {product_name}")
    app.logger.info(f"License Key: {license_key}")

    # TODO: Implement actual email sending
    # email_service.send_template_email(
    #     to=customer_email,
    #     template='license_delivery',
    #     data={
    #         'product_name': product_name,
    #         'license_key': license_key,
    #         'activation_url': f'https://synapse-lang.com/activate?key={license_key}'
    #     }
    # )

@app.route("/api/validate-license", methods=["POST"])
def validate_license():
    """Validate a license key."""
    try:
        data = request.get_json()
        license_key = data.get("license_key")

        if not license_key:
            return jsonify({"error": "License key required"}), 400

        is_valid, message, license_data = license_manager.validate_license(license_key)

        return jsonify({
            "valid": is_valid,
            "message": message,
            "license_data": license_data if is_valid else {}
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/charge/<charge_id>", methods=["GET"])
def get_charge_status(charge_id: str):
    """Get charge status."""
    try:
        charge = payment_service.get_charge(charge_id)
        return jsonify({"charge": charge})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Payment page HTML template
PAYMENT_PAGE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Synapse Language - Cryptocurrency Payment</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: white;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 50px 20px;
        }
        .header {
            text-align: center;
            margin-bottom: 50px;
        }
        .header h1 {
            font-size: 3rem;
            margin: 0;
            background: linear-gradient(45deg, #43E5FF, #7A5CFF);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .products {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 50px;
        }
        .product-card {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 30px;
            cursor: pointer;
            transition: all 0.3s ease;
            border: 2px solid transparent;
        }
        .product-card:hover {
            transform: translateY(-5px);
            border-color: #43E5FF;
        }
        .product-card.selected {
            border-color: #2ECC71;
            background: rgba(46, 204, 113, 0.2);
        }
        .product-price {
            font-size: 2rem;
            font-weight: bold;
            color: #43E5FF;
        }
        .crypto-info {
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }
        .payment-form {
            background: rgba(255, 255, 255, 0.1);
            padding: 30px;
            border-radius: 12px;
            display: none;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group input {
            width: 100%;
            padding: 15px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
        }
        .pay-button {
            background: #2ECC71;
            color: white;
            border: none;
            padding: 20px 40px;
            border-radius: 8px;
            font-size: 18px;
            font-weight: bold;
            cursor: pointer;
            width: 100%;
            margin-top: 20px;
        }
        .pay-button:hover {
            background: #27AE60;
        }
        .crypto-icons {
            display: flex;
            justify-content: center;
            gap: 15px;
            margin: 20px 0;
        }
        .crypto-icon {
            width: 50px;
            height: 50px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
        }
        .error {
            color: #ff6b6b;
            text-align: center;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚡ Synapse Language</h1>
            <p>Pay with cryptocurrency for instant access</p>
        </div>

        <div class="products" id="products">
            <!-- Products will be loaded dynamically -->
        </div>

        <div class="crypto-info">
            <h3>💰 Supported Cryptocurrencies</h3>
            <div class="crypto-icons">
                <div class="crypto-icon">₿</div>
                <div class="crypto-icon">Ξ</div>
                <div class="crypto-icon">Ł</div>
                <div class="crypto-icon">$</div>
            </div>
            <p>Bitcoin, Ethereum, Litecoin, Bitcoin Cash, USDC, and DAI accepted</p>
        </div>

        <div class="payment-form" id="paymentForm">
            <h3>Complete Your Purchase</h3>
            <form id="checkoutForm">
                <div class="form-group">
                    <input type="email" id="email" placeholder="Your email address" required>
                </div>
                <div class="form-group">
                    <input type="text" id="name" placeholder="Your full name" required>
                </div>
                <button type="submit" class="pay-button">
                    🚀 Pay with Cryptocurrency
                </button>
            </form>
            <div class="error" id="error"></div>
        </div>
    </div>

    <script>
        let selectedProduct = null;

        // Load products
        async function loadProducts() {
            try {
                const response = await fetch('/api/products');
                const data = await response.json();

                const productsContainer = document.getElementById('products');
                productsContainer.innerHTML = '';

                for (const [key, product] of Object.entries(data.products)) {
                    const card = document.createElement('div');
                    card.className = 'product-card';
                    card.innerHTML = `
                        <h3>${product.name}</h3>
                        <div class="product-price">$${product.price}</div>
                        <p>${product.description}</p>
                    `;

                    card.addEventListener('click', () => selectProduct(key, card));
                    productsContainer.appendChild(card);
                }
            } catch (error) {
                console.error('Failed to load products:', error);
            }
        }

        function selectProduct(productType, cardElement) {
            selectedProduct = productType;

            // Update UI
            document.querySelectorAll('.product-card').forEach(card => {
                card.classList.remove('selected');
            });
            cardElement.classList.add('selected');

            // Show payment form
            document.getElementById('paymentForm').style.display = 'block';
        }

        // Handle form submission
        document.getElementById('checkoutForm').addEventListener('submit', async (e) => {
            e.preventDefault();

            const email = document.getElementById('email').value;
            const name = document.getElementById('name').value;
            const errorDiv = document.getElementById('error');

            if (!selectedProduct) {
                errorDiv.textContent = 'Please select a product first';
                return;
            }

            if (!email || !name) {
                errorDiv.textContent = 'Please fill in all fields';
                return;
            }

            try {
                errorDiv.textContent = '';

                // Create charge
                const response = await fetch('/api/create-charge', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        product_type: selectedProduct,
                        customer_email: email,
                        customer_name: name
                    })
                });

                const data = await response.json();

                if (response.ok) {
                    // Redirect to Coinbase Commerce
                    window.location.href = data.hosted_url;
                } else {
                    errorDiv.textContent = data.error || 'Payment creation failed';
                }
            } catch (error) {
                errorDiv.textContent = 'Network error: ' + error.message;
            }
        });

        // Load products on page load
        loadProducts();
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
