#!/usr/bin/env python3
"""
Email service for Synapse Language payment notifications
Handles license delivery and payment confirmations via SendGrid
"""

import json
import logging
import os
from datetime import datetime

import sendgrid
from sendgrid.helpers.mail import Content, Email, Mail, To


class EmailService:
    """Handles email notifications for Synapse Language payments."""

    def __init__(self):
        self.api_key = os.getenv("SENDGRID_API_KEY")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@synapse-lang.com")

        if not self.api_key:
            raise ValueError("SENDGRID_API_KEY environment variable is required")

        self.client = sendgrid.SendGridAPIClient(api_key=self.api_key)

        # Email templates
        self.templates = {
            "license_delivery": {
                "subject": "🎉 Your Synapse Language License is Ready!",
                "template_id": "d-license-delivery-template-id"  # Replace with actual SendGrid template ID
            },
            "payment_confirmation": {
                "subject": "💰 Payment Confirmed - Synapse Language",
                "template_id": "d-payment-confirmation-template-id"
            },
            "payment_failed": {
                "subject": "❌ Payment Failed - Synapse Language",
                "template_id": "d-payment-failed-template-id"
            }
        }

    def send_license_email(self, customer_email: str, license_data: dict) -> bool:
        """Send license delivery email to customer."""
        try:
            # Prepare email data
            template_data = {
                "customer_name": license_data.get("customer_name", "Synapse User"),
                "product_name": license_data["product_name"],
                "license_key": license_data["license_key"],
                "price_paid": f"${license_data['price_paid_usd']}",
                "expires_at": license_data["expires_at"],
                "activation_url": f'https://synapse-lang.com/activate?key={license_data["license_key"]}',
                "support_url": "https://synapse-lang.com/support",
                "documentation_url": "https://docs.synapse-lang.com"
            }

            # Create email content (fallback HTML for when template is not available)
            html_content = self._generate_license_html(template_data)

            # Send email
            success = self._send_email(
                to_email=customer_email,
                template_type="license_delivery",
                template_data=template_data,
                fallback_html=html_content
            )

            # Log email attempt
            self._log_email_attempt(
                recipient=customer_email,
                template_type="license_delivery",
                license_key=license_data["license_key"],
                success=success
            )

            return success

        except Exception as e:
            logging.error(f"Failed to send license email to {customer_email}: {str(e)}")
            return False

    def send_payment_confirmation(self, customer_email: str, payment_data: dict) -> bool:
        """Send payment confirmation email."""
        try:
            template_data = {
                "customer_name": payment_data.get("customer_name", "Synapse User"),
                "product_name": payment_data["product_name"],
                "amount_paid": f"${payment_data['amount_usd']}",
                "currency_paid": payment_data.get("currency_paid", "USD"),
                "transaction_id": payment_data["charge_id"],
                "payment_date": datetime.utcnow().strftime("%B %d, %Y at %I:%M %p UTC"),
                "receipt_url": f'https://synapse-lang.com/receipt?id={payment_data["charge_id"]}'
            }

            html_content = self._generate_payment_confirmation_html(template_data)

            success = self._send_email(
                to_email=customer_email,
                template_type="payment_confirmation",
                template_data=template_data,
                fallback_html=html_content
            )

            self._log_email_attempt(
                recipient=customer_email,
                template_type="payment_confirmation",
                charge_id=payment_data["charge_id"],
                success=success
            )

            return success

        except Exception as e:
            logging.error(f"Failed to send payment confirmation to {customer_email}: {str(e)}")
            return False

    def send_payment_failed_email(self, customer_email: str, payment_data: dict) -> bool:
        """Send payment failure notification."""
        try:
            template_data = {
                "customer_name": payment_data.get("customer_name", "Synapse User"),
                "product_name": payment_data["product_name"],
                "failure_reason": payment_data.get("failure_reason", "Payment could not be processed"),
                "retry_url": f'https://pay.synapse-lang.com?retry={payment_data["charge_id"]}',
                "support_url": "https://synapse-lang.com/support"
            }

            html_content = self._generate_payment_failed_html(template_data)

            success = self._send_email(
                to_email=customer_email,
                template_type="payment_failed",
                template_data=template_data,
                fallback_html=html_content
            )

            self._log_email_attempt(
                recipient=customer_email,
                template_type="payment_failed",
                charge_id=payment_data["charge_id"],
                success=success
            )

            return success

        except Exception as e:
            logging.error(f"Failed to send payment failed email to {customer_email}: {str(e)}")
            return False

    def _send_email(self, to_email: str, template_type: str,
                   template_data: dict, fallback_html: str) -> bool:
        """Send email using SendGrid."""
        try:
            template_config = self.templates[template_type]

            # Create email message
            from_email_obj = Email(self.from_email, "Synapse Language Team")
            to_email_obj = To(to_email)

            # Try using SendGrid template first, fallback to HTML content
            try:
                message = Mail(
                    from_email=from_email_obj,
                    to_emails=to_email_obj,
                    subject=template_config["subject"]
                )

                # Add template data
                message.dynamic_template_data = template_data
                message.template_id = template_config.get("template_id")

            except:
                # Fallback to HTML content if template is not available
                content = Content("text/html", fallback_html)
                message = Mail(
                    from_email=from_email_obj,
                    to_emails=to_email_obj,
                    subject=template_config["subject"],
                    html_content=content
                )

            # Send email
            response = self.client.send(message)

            # Check if email was sent successfully
            return response.status_code in [200, 202]

        except Exception as e:
            logging.error(f"SendGrid API error: {str(e)}")
            return False

    def _generate_license_html(self, data: dict) -> str:
        """Generate HTML content for license delivery email."""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 8px; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 8px; margin: 20px 0; }}
                .license-box {{ background: #e8f5e8; border: 2px solid #4CAF50; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .button {{ display: inline-block; background: #4CAF50; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; }}
                .footer {{ text-align: center; color: #666; margin-top: 30px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>⚡ Synapse Language</h1>
                    <h2>Your License is Ready!</h2>
                </div>

                <div class="content">
                    <p>Hi {data['customer_name']},</p>

                    <p>Thank you for purchasing <strong>{data['product_name']}</strong>! Your cryptocurrency payment has been confirmed and your license is now active.</p>

                    <div class="license-box">
                        <h3>🔑 Your License Key</h3>
                        <p style="font-family: monospace; font-size: 18px; font-weight: bold; color: #2E7D32;">
                            {data['license_key']}
                        </p>
                        <p><strong>Expires:</strong> {data['expires_at']}</p>
                    </div>

                    <h3>🚀 Quick Start</h3>
                    <ol>
                        <li>Install Synapse Language: <code>pip install synapse-lang</code></li>
                        <li>Activate your license: <code>synapse activate {data['license_key']}</code></li>
                        <li>Start coding with quantum-enhanced features!</li>
                    </ol>

                    <p style="text-align: center; margin: 30px 0;">
                        <a href="{data['activation_url']}" class="button">Activate License Online</a>
                    </p>

                    <h3>📚 Resources</h3>
                    <ul>
                        <li><a href="{data['documentation_url']}">Documentation</a></li>
                        <li><a href="{data['support_url']}">Support Center</a></li>
                        <li><a href="https://github.com/synapse-lang/examples">Code Examples</a></li>
                    </ul>
                </div>

                <div class="footer">
                    <p>Paid: {data['price_paid']} via cryptocurrency</p>
                    <p>Questions? Contact us at <a href="mailto:support@synapse-lang.com">support@synapse-lang.com</a></p>
                    <p><small>Synapse Language - Quantum-Enhanced Scientific Computing</small></p>
                </div>
            </div>
        </body>
        </html>
        """

    def _generate_payment_confirmation_html(self, data: dict) -> str:
        """Generate HTML content for payment confirmation email."""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #2ECC71 0%, #27AE60 100%); color: white; padding: 30px; text-align: center; border-radius: 8px; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 8px; margin: 20px 0; }}
                .receipt-box {{ background: #e8f5e8; border-left: 4px solid #4CAF50; padding: 20px; margin: 20px 0; }}
                .footer {{ text-align: center; color: #666; margin-top: 30px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✅ Payment Confirmed</h1>
                    <h2>Synapse Language</h2>
                </div>

                <div class="content">
                    <p>Hi {data['customer_name']},</p>

                    <p>Great news! Your cryptocurrency payment has been successfully confirmed.</p>

                    <div class="receipt-box">
                        <h3>📄 Payment Receipt</h3>
                        <p><strong>Product:</strong> {data['product_name']}</p>
                        <p><strong>Amount:</strong> {data['amount_paid']} ({data['currency_paid']})</p>
                        <p><strong>Transaction ID:</strong> {data['transaction_id']}</p>
                        <p><strong>Date:</strong> {data['payment_date']}</p>
                    </div>

                    <p>Your license will be delivered shortly in a separate email. The license activation process is automatic and should complete within a few minutes.</p>

                    <p style="text-align: center; margin: 30px 0;">
                        <a href="{data['receipt_url']}" style="display: inline-block; background: #2ECC71; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">View Full Receipt</a>
                    </p>
                </div>

                <div class="footer">
                    <p>Thank you for choosing Synapse Language!</p>
                    <p>Questions? Contact us at <a href="mailto:support@synapse-lang.com">support@synapse-lang.com</a></p>
                </div>
            </div>
        </body>
        </html>
        """

    def _generate_payment_failed_html(self, data: dict) -> str:
        """Generate HTML content for payment failure email."""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #E74C3C 0%, #C0392B 100%); color: white; padding: 30px; text-align: center; border-radius: 8px; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 8px; margin: 20px 0; }}
                .error-box {{ background: #ffeaea; border-left: 4px solid #E74C3C; padding: 20px; margin: 20px 0; }}
                .button {{ display: inline-block; background: #3498DB; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; }}
                .footer {{ text-align: center; color: #666; margin-top: 30px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>❌ Payment Issue</h1>
                    <h2>Synapse Language</h2>
                </div>

                <div class="content">
                    <p>Hi {data['customer_name']},</p>

                    <p>We encountered an issue processing your payment for <strong>{data['product_name']}</strong>.</p>

                    <div class="error-box">
                        <h3>🔍 What happened?</h3>
                        <p>{data['failure_reason']}</p>
                    </div>

                    <h3>💡 Next Steps</h3>
                    <ol>
                        <li>Check your wallet balance and transaction status</li>
                        <li>Ensure you have sufficient cryptocurrency for the transaction</li>
                        <li>Try the payment again using the link below</li>
                        <li>Contact our support team if the issue persists</li>
                    </ol>

                    <p style="text-align: center; margin: 30px 0;">
                        <a href="{data['retry_url']}" class="button">Retry Payment</a>
                    </p>
                </div>

                <div class="footer">
                    <p>Need help? Our support team is here to assist you.</p>
                    <p>Contact us at <a href="mailto:support@synapse-lang.com">support@synapse-lang.com</a></p>
                    <p>Or visit our <a href="{data['support_url']}">Support Center</a></p>
                </div>
            </div>
        </body>
        </html>
        """

    def _log_email_attempt(self, recipient: str, template_type: str,
                          license_key: str = None, charge_id: str = None, success: bool = True):
        """Log email attempt for debugging and monitoring."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "recipient": recipient,
            "template_type": template_type,
            "success": success,
            "license_key": license_key,
            "charge_id": charge_id
        }

        # In production, save to database
        # For now, log to file
        try:
            os.makedirs("logs", exist_ok=True)
            with open("logs/email_log.jsonl", "a") as f:
                f.write(json.dumps(log_data) + "\n")
        except Exception as e:
            logging.error(f"Failed to log email attempt: {str(e)}")

# Singleton instance
email_service = EmailService()
