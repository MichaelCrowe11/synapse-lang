#!/usr/bin/env python3
"""
Stripe Webhook Server for Synapse Platform

Handles incoming Stripe webhooks for payment processing.
"""

import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

from stripe_integration import PaymentConfig, StripePaymentProcessor


class StripeWebhookHandler(BaseHTTPRequestHandler):
    """HTTP request handler for Stripe webhooks."""

    def __init__(self, *args, processor=None, **kwargs):
        self.processor = processor or StripePaymentProcessor(PaymentConfig())
        super().__init__(*args, **kwargs)

    def do_POST(self):
        """Handle POST requests from Stripe."""
        if self.path != "/stripe/webhook":
            self.send_error(404, "Not Found")
            return

        # Read the request body
        content_length = int(self.headers.get("Content-Length", 0))
        payload = self.rfile.read(content_length).decode("utf-8")

        # Get Stripe signature
        signature = self.headers.get("Stripe-Signature", "")

        try:
            # Process webhook
            result = self.processor.handle_webhook(payload, signature)

            # Log the event
            event_data = json.loads(payload)
            print(f"Webhook received: {event_data.get('type')}")
            print(f"Result: {result}")

            # Send success response
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success"}).encode())

        except Exception as e:
            print(f"Webhook error: {str(e)}")
            self.send_error(400, str(e))

    def do_GET(self):
        """Handle GET requests for health checks."""
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "healthy",
                "service": "stripe-webhook-server"
            }).encode())
        else:
            self.send_error(404, "Not Found")

    def log_message(self, format, *args):
        """Custom log format."""
        print(f"[Webhook Server] {format % args}")

def run_webhook_server(port: int = 8000):
    """Run the webhook server."""
    processor = StripePaymentProcessor(PaymentConfig())

    # Create custom handler with processor
    def handler(*args, **kwargs):
        StripeWebhookHandler(*args, processor=processor, **kwargs)

    server_address = ("", port)
    httpd = HTTPServer(server_address, StripeWebhookHandler)

    print(f"Stripe Webhook Server running on port {port}")
    print(f"Webhook endpoint: http://localhost:{port}/stripe/webhook")
    print(f"Health check: http://localhost:{port}/health")
    print("Press Ctrl+C to stop...")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down webhook server...")
        httpd.shutdown()

if __name__ == "__main__":
    # Get port from environment or use default
    port = int(os.getenv("WEBHOOK_PORT", "8000"))
    run_webhook_server(port)
