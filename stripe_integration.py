"""
Stripe Payment Integration for Synapse-Lang.com
Handles subscriptions, payments, and billing
"""

from flask import Blueprint, request, jsonify, session, redirect, url_for
import stripe
import os
import json
from datetime import datetime
import sqlite3

# Stripe configuration
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_your_secret_key_here')
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY', 'pk_test_your_publishable_key_here')

# Create Blueprint
stripe_bp = Blueprint('stripe', __name__)

# Price IDs (create these in Stripe Dashboard)
PRICE_IDS = {
    'pro_monthly': 'price_1234567890',  # Replace with actual Stripe price ID
    'pro_yearly': 'price_1234567891',   # Replace with actual Stripe price ID
    'enterprise_monthly': 'price_1234567892',  # Replace with actual Stripe price ID
    'enterprise_yearly': 'price_1234567893'    # Replace with actual Stripe price ID
}

class StripeManager:
    """Handles all Stripe operations"""
    
    def __init__(self):
        self.webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET', 'whsec_your_webhook_secret')
    
    def create_customer(self, email, name=None, metadata=None):
        """Create a new Stripe customer"""
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata=metadata or {}
            )
            return customer
        except stripe.error.StripeError as e:
            print(f"Stripe error creating customer: {e}")
            return None
    
    def create_checkout_session(self, price_id, customer_email, success_url, cancel_url, metadata=None):
        """Create a Stripe Checkout session"""
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                customer_email=customer_email,
                success_url=success_url,
                cancel_url=cancel_url,
                metadata=metadata or {},
                allow_promotion_codes=True,
                billing_address_collection='required',
                customer_creation='always'
            )
            return session
        except stripe.error.StripeError as e:
            print(f"Stripe error creating checkout session: {e}")
            return None
    
    def create_billing_portal_session(self, customer_id, return_url):
        """Create a billing portal session for customer management"""
        try:
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url
            )
            return session
        except stripe.error.StripeError as e:
            print(f"Stripe error creating billing portal session: {e}")
            return None
    
    def get_subscription(self, subscription_id):
        """Get subscription details"""
        try:
            return stripe.Subscription.retrieve(subscription_id)
        except stripe.error.StripeError as e:
            print(f"Stripe error retrieving subscription: {e}")
            return None
    
    def cancel_subscription(self, subscription_id):
        """Cancel a subscription"""
        try:
            return stripe.Subscription.delete(subscription_id)
        except stripe.error.StripeError as e:
            print(f"Stripe error cancelling subscription: {e}")
            return None
    
    def get_usage_record(self, subscription_item_id, usage_quantity):
        """Create usage record for metered billing"""
        try:
            return stripe.UsageRecord.create(
                subscription_item=subscription_item_id,
                quantity=usage_quantity,
                timestamp=int(datetime.now().timestamp())
            )
        except stripe.error.StripeError as e:
            print(f"Stripe error creating usage record: {e}")
            return None

# Initialize Stripe manager
stripe_manager = StripeManager()

@stripe_bp.route('/api/stripe/config')
def get_stripe_config():
    """Get Stripe publishable key"""
    return jsonify({
        'publishable_key': STRIPE_PUBLISHABLE_KEY
    })

@stripe_bp.route('/api/stripe/create-checkout-session', methods=['POST'])
def create_checkout_session():
    """Create Stripe Checkout session"""
    try:
        data = request.json
        plan = data.get('plan')
        user_email = data.get('email', 'user@example.com')  # Should come from authenticated user
        
        # Map plan to price ID
        price_mapping = {
            'pro': PRICE_IDS['pro_monthly'],
            'pro_yearly': PRICE_IDS['pro_yearly'],
            'enterprise': PRICE_IDS['enterprise_monthly'],
            'enterprise_yearly': PRICE_IDS['enterprise_yearly']
        }
        
        price_id = price_mapping.get(plan)
        if not price_id:
            return jsonify({'error': 'Invalid plan'}), 400
        
        # Create checkout session
        session = stripe_manager.create_checkout_session(
            price_id=price_id,
            customer_email=user_email,
            success_url=request.host_url + 'success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.host_url + 'pricing',
            metadata={
                'plan': plan,
                'platform': 'synapse-lang.com'
            }
        )
        
        if session:
            return jsonify({
                'sessionId': session.id,
                'url': session.url
            })
        else:
            return jsonify({'error': 'Failed to create checkout session'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@stripe_bp.route('/api/stripe/create-portal-session', methods=['POST'])
def create_portal_session():
    """Create customer portal session"""
    try:
        data = request.json
        customer_id = data.get('customer_id')
        
        if not customer_id:
            return jsonify({'error': 'Customer ID required'}), 400
        
        session = stripe_manager.create_billing_portal_session(
            customer_id=customer_id,
            return_url=request.host_url + 'account'
        )
        
        if session:
            return jsonify({'url': session.url})
        else:
            return jsonify({'error': 'Failed to create portal session'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@stripe_bp.route('/api/stripe/subscription/<subscription_id>')
def get_subscription_details(subscription_id):
    """Get subscription details"""
    try:
        subscription = stripe_manager.get_subscription(subscription_id)
        if subscription:
            return jsonify({
                'id': subscription.id,
                'status': subscription.status,
                'current_period_start': subscription.current_period_start,
                'current_period_end': subscription.current_period_end,
                'plan': subscription.items.data[0].price.nickname,
                'amount': subscription.items.data[0].price.unit_amount / 100,
                'currency': subscription.items.data[0].price.currency,
                'interval': subscription.items.data[0].price.recurring.interval
            })
        else:
            return jsonify({'error': 'Subscription not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@stripe_bp.route('/api/stripe/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhooks"""
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, stripe_manager.webhook_secret
        )
    except ValueError:
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError:
        return jsonify({'error': 'Invalid signature'}), 400
    
    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        handle_checkout_session_completed(session)
    
    elif event['type'] == 'customer.subscription.created':
        subscription = event['data']['object']
        handle_subscription_created(subscription)
    
    elif event['type'] == 'customer.subscription.updated':
        subscription = event['data']['object']
        handle_subscription_updated(subscription)
    
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        handle_subscription_deleted(subscription)
    
    elif event['type'] == 'invoice.payment_succeeded':
        invoice = event['data']['object']
        handle_payment_succeeded(invoice)
    
    elif event['type'] == 'invoice.payment_failed':
        invoice = event['data']['object']
        handle_payment_failed(invoice)
    
    return jsonify({'status': 'success'})

def handle_checkout_session_completed(session):
    """Handle successful checkout"""
    try:
        customer_id = session['customer']
        subscription_id = session['subscription']
        plan = session['metadata'].get('plan', 'unknown')
        
        # Update user subscription in database
        conn = sqlite3.connect('synapse_lang.db')
        c = conn.cursor()
        
        # Update user plan
        c.execute('''UPDATE users SET 
                     plan = ?, 
                     stripe_customer_id = ?, 
                     stripe_subscription_id = ?,
                     subscription_status = 'active',
                     updated_at = ?
                     WHERE email = ?''',
                  (plan, customer_id, subscription_id, datetime.now(), session['customer_email']))
        
        # Log the event
        c.execute('''INSERT INTO subscription_events 
                     (customer_id, event_type, subscription_id, plan, timestamp)
                     VALUES (?, ?, ?, ?, ?)''',
                  (customer_id, 'checkout_completed', subscription_id, plan, datetime.now()))
        
        conn.commit()
        conn.close()
        
        print(f"Subscription created for customer {customer_id}, plan: {plan}")
        
    except Exception as e:
        print(f"Error handling checkout completion: {e}")

def handle_subscription_created(subscription):
    """Handle subscription creation"""
    try:
        customer_id = subscription['customer']
        subscription_id = subscription['id']
        status = subscription['status']
        
        # Update database
        conn = sqlite3.connect('synapse_lang.db')
        c = conn.cursor()
        
        c.execute('''UPDATE users SET 
                     subscription_status = ?,
                     updated_at = ?
                     WHERE stripe_customer_id = ?''',
                  (status, datetime.now(), customer_id))
        
        conn.commit()
        conn.close()
        
        print(f"Subscription {subscription_id} created for customer {customer_id}")
        
    except Exception as e:
        print(f"Error handling subscription creation: {e}")

def handle_subscription_updated(subscription):
    """Handle subscription updates"""
    try:
        customer_id = subscription['customer']
        subscription_id = subscription['id']
        status = subscription['status']
        
        # Update database
        conn = sqlite3.connect('synapse_lang.db')
        c = conn.cursor()
        
        c.execute('''UPDATE users SET 
                     subscription_status = ?,
                     updated_at = ?
                     WHERE stripe_customer_id = ?''',
                  (status, datetime.now(), customer_id))
        
        conn.commit()
        conn.close()
        
        print(f"Subscription {subscription_id} updated for customer {customer_id}")
        
    except Exception as e:
        print(f"Error handling subscription update: {e}")

def handle_subscription_deleted(subscription):
    """Handle subscription cancellation"""
    try:
        customer_id = subscription['customer']
        subscription_id = subscription['id']
        
        # Update database
        conn = sqlite3.connect('synapse_lang.db')
        c = conn.cursor()
        
        c.execute('''UPDATE users SET 
                     subscription_status = 'cancelled',
                     plan = 'free',
                     updated_at = ?
                     WHERE stripe_customer_id = ?''',
                  (datetime.now(), customer_id))
        
        conn.commit()
        conn.close()
        
        print(f"Subscription {subscription_id} cancelled for customer {customer_id}")
        
    except Exception as e:
        print(f"Error handling subscription deletion: {e}")

def handle_payment_succeeded(invoice):
    """Handle successful payment"""
    try:
        customer_id = invoice['customer']
        subscription_id = invoice['subscription']
        amount_paid = invoice['amount_paid'] / 100  # Convert from cents
        
        # Log successful payment
        conn = sqlite3.connect('synapse_lang.db')
        c = conn.cursor()
        
        c.execute('''INSERT INTO payment_history 
                     (customer_id, subscription_id, amount, currency, status, timestamp)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (customer_id, subscription_id, amount_paid, invoice['currency'], 
                   'succeeded', datetime.now()))
        
        conn.commit()
        conn.close()
        
        print(f"Payment succeeded: ${amount_paid} for customer {customer_id}")
        
    except Exception as e:
        print(f"Error handling successful payment: {e}")

def handle_payment_failed(invoice):
    """Handle failed payment"""
    try:
        customer_id = invoice['customer']
        subscription_id = invoice['subscription']
        amount_due = invoice['amount_due'] / 100
        
        # Log failed payment
        conn = sqlite3.connect('synapse_lang.db')
        c = conn.cursor()
        
        c.execute('''INSERT INTO payment_history 
                     (customer_id, subscription_id, amount, currency, status, timestamp)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (customer_id, subscription_id, amount_due, invoice['currency'], 
                   'failed', datetime.now()))
        
        # Update subscription status
        c.execute('''UPDATE users SET 
                     subscription_status = 'past_due',
                     updated_at = ?
                     WHERE stripe_customer_id = ?''',
                  (datetime.now(), customer_id))
        
        conn.commit()
        conn.close()
        
        print(f"Payment failed: ${amount_due} for customer {customer_id}")
        
    except Exception as e:
        print(f"Error handling failed payment: {e}")

# Usage tracking functions
def track_code_execution(user_id, language, lines_of_code=1):
    """Track code execution for usage-based billing"""
    try:
        conn = sqlite3.connect('synapse_lang.db')
        c = conn.cursor()
        
        # Insert usage record
        c.execute('''INSERT INTO usage_tracking 
                     (user_id, event_type, quantity, language, timestamp)
                     VALUES (?, ?, ?, ?, ?)''',
                  (user_id, 'code_execution', lines_of_code, language, datetime.now()))
        
        # Check if user has metered billing
        c.execute('''SELECT stripe_subscription_id, plan FROM users WHERE id = ?''', (user_id,))
        user = c.fetchone()
        
        if user and user[1] in ['enterprise']:  # Enterprise plans might have usage-based billing
            # Report usage to Stripe (if needed)
            # This would require setting up metered billing in Stripe
            pass
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        print(f"Error tracking usage: {e}")

def get_user_usage_stats(user_id, period_start=None):
    """Get usage statistics for a user"""
    try:
        conn = sqlite3.connect('synapse_lang.db')
        c = conn.cursor()
        
        if period_start:
            c.execute('''SELECT event_type, SUM(quantity) as total, COUNT(*) as count
                         FROM usage_tracking 
                         WHERE user_id = ? AND timestamp >= ?
                         GROUP BY event_type''',
                      (user_id, period_start))
        else:
            # Get all-time stats
            c.execute('''SELECT event_type, SUM(quantity) as total, COUNT(*) as count
                         FROM usage_tracking 
                         WHERE user_id = ?
                         GROUP BY event_type''',
                      (user_id,))
        
        stats = c.fetchall()
        conn.close()
        
        return {
            'executions': next((s[1] for s in stats if s[0] == 'code_execution'), 0),
            'deployments': next((s[1] for s in stats if s[0] == 'deployment'), 0),
            'api_calls': next((s[1] for s in stats if s[0] == 'api_call'), 0),
        }
        
    except Exception as e:
        print(f"Error getting usage stats: {e}")
        return {}

# Initialize subscription tables
def init_subscription_tables():
    """Initialize subscription-related database tables"""
    conn = sqlite3.connect('synapse_lang.db')
    c = conn.cursor()
    
    # Subscription events table
    c.execute('''CREATE TABLE IF NOT EXISTS subscription_events
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  customer_id TEXT,
                  event_type TEXT,
                  subscription_id TEXT,
                  plan TEXT,
                  timestamp TIMESTAMP)''')
    
    # Payment history table
    c.execute('''CREATE TABLE IF NOT EXISTS payment_history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  customer_id TEXT,
                  subscription_id TEXT,
                  amount REAL,
                  currency TEXT,
                  status TEXT,
                  timestamp TIMESTAMP)''')
    
    # Usage tracking table
    c.execute('''CREATE TABLE IF NOT EXISTS usage_tracking
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id TEXT,
                  event_type TEXT,
                  quantity INTEGER,
                  language TEXT,
                  timestamp TIMESTAMP)''')
    
    # Add Stripe fields to users table
    c.execute('''ALTER TABLE users ADD COLUMN stripe_customer_id TEXT''')
    c.execute('''ALTER TABLE users ADD COLUMN stripe_subscription_id TEXT''')
    c.execute('''ALTER TABLE users ADD COLUMN subscription_status TEXT DEFAULT 'free' ''')
    c.execute('''ALTER TABLE users ADD COLUMN updated_at TIMESTAMP''')
    
    conn.commit()
    conn.close()

# Export the blueprint
__all__ = ['stripe_bp', 'track_code_execution', 'get_user_usage_stats', 'init_subscription_tables']