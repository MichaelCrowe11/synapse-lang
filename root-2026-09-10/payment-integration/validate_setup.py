#!/usr/bin/env python3
"""
Validate Coinbase Commerce setup for Synapse Language payments
Tests live API connection and webhook configuration
"""

import json
import os
import sys
from datetime import datetime

import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class CoinbaseSetupValidator:
    """Validate Coinbase Commerce integration setup."""

    def __init__(self):
        self.api_key = os.getenv("COINBASE_COMMERCE_API_KEY")
        self.webhook_secret = os.getenv("COINBASE_COMMERCE_WEBHOOK_SECRET")
        self.oauth_client_id = os.getenv("COINBASE_OAUTH_CLIENT_ID")
        self.oauth_client_secret = os.getenv("COINBASE_OAUTH_CLIENT_SECRET")

        self.base_url = "https://api.commerce.coinbase.com"
        self.results = []

    def log_result(self, test_name: str, status: str, message: str, details: dict = None):
        """Log validation result."""
        result = {
            "test": test_name,
            "status": status,
            "message": message,
            "details": details or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        self.results.append(result)

        status_icon = {
            "PASS": "[PASS]",
            "FAIL": "[FAIL]",
            "WARN": "[WARN]",
            "INFO": "[INFO]"
        }.get(status, "[?]")

        print(f"{status_icon} {test_name}: {message}")
        if details and status in ["FAIL", "WARN"]:
            for key, value in details.items():
                print(f"    {key}: {value}")

    def test_environment_variables(self):
        """Test if required environment variables are set."""
        required_vars = {
            "COINBASE_COMMERCE_API_KEY": self.api_key,
            "COINBASE_COMMERCE_WEBHOOK_SECRET": self.webhook_secret,
            "COINBASE_OAUTH_CLIENT_ID": self.oauth_client_id,
            "COINBASE_OAUTH_CLIENT_SECRET": self.oauth_client_secret
        }

        missing_vars = []
        for var_name, var_value in required_vars.items():
            if not var_value:
                missing_vars.append(var_name)

        if missing_vars:
            self.log_result(
                "Environment Variables",
                "FAIL",
                f"Missing required variables: {', '.join(missing_vars)}",
                {"missing_count": len(missing_vars)}
            )
            return False

        # Validate format
        if not self.api_key.startswith(("ddae9bb3", "live_", "test_")):
            self.log_result(
                "Environment Variables",
                "WARN",
                "API key format may be incorrect",
                {"api_key_prefix": self.api_key[:8] + "..."}
            )

        self.log_result(
            "Environment Variables",
            "PASS",
            "All required environment variables are set",
            {
                "api_key_set": bool(self.api_key),
                "webhook_secret_set": bool(self.webhook_secret),
                "oauth_client_set": bool(self.oauth_client_id)
            }
        )
        return True

    def test_api_connection(self):
        """Test connection to Coinbase Commerce API."""
        if not self.api_key:
            self.log_result(
                "API Connection",
                "FAIL",
                "Cannot test - API key not set"
            )
            return False

        headers = {
            "Content-Type": "application/json",
            "X-CC-Api-Key": self.api_key,
            "X-CC-Version": "2018-03-22"
        }

        try:
            response = requests.get(
                f"{self.base_url}/charges",
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                self.log_result(
                    "API Connection",
                    "PASS",
                    "Successfully connected to Coinbase Commerce API",
                    {
                        "response_time": f"{response.elapsed.total_seconds():.2f}s",
                        "charges_found": len(data.get("data", []))
                    }
                )
                return True
            elif response.status_code == 401:
                self.log_result(
                    "API Connection",
                    "FAIL",
                    "Authentication failed - check API key",
                    {"status_code": response.status_code}
                )
                return False
            else:
                self.log_result(
                    "API Connection",
                    "FAIL",
                    f"API request failed with status {response.status_code}",
                    {
                        "status_code": response.status_code,
                        "response": response.text[:200]
                    }
                )
                return False

        except requests.exceptions.RequestException as e:
            self.log_result(
                "API Connection",
                "FAIL",
                f"Network error: {str(e)}",
                {"error_type": type(e).__name__}
            )
            return False

    def test_charge_creation(self):
        """Test creating a test charge."""
        if not self.api_key:
            self.log_result(
                "Charge Creation",
                "FAIL",
                "Cannot test - API key not set"
            )
            return False

        headers = {
            "Content-Type": "application/json",
            "X-CC-Api-Key": self.api_key,
            "X-CC-Version": "2018-03-22"
        }

        test_charge_data = {
            "name": "Synapse Language Test Charge",
            "description": "Test charge for setup validation",
            "local_price": {
                "amount": "1.00",
                "currency": "USD"
            },
            "pricing_type": "fixed_price",
            "metadata": {
                "test": "true",
                "setup_validation": "true"
            }
        }

        try:
            response = requests.post(
                f"{self.base_url}/charges",
                headers=headers,
                json=test_charge_data,
                timeout=15
            )

            if response.status_code == 201:
                charge_data = response.json()["data"]
                self.log_result(
                    "Charge Creation",
                    "PASS",
                    "Test charge created successfully",
                    {
                        "charge_id": charge_data["id"],
                        "hosted_url": charge_data["hosted_url"][:50] + "...",
                        "expires_at": charge_data["expires_at"]
                    }
                )

                # Clean up test charge (cancel it)
                self.cancel_test_charge(charge_data["id"])
                return True
            else:
                self.log_result(
                    "Charge Creation",
                    "FAIL",
                    f"Failed to create test charge: {response.status_code}",
                    {"response": response.text[:200]}
                )
                return False

        except requests.exceptions.RequestException as e:
            self.log_result(
                "Charge Creation",
                "FAIL",
                f"Error creating charge: {str(e)}",
                {"error_type": type(e).__name__}
            )
            return False

    def cancel_test_charge(self, charge_id: str):
        """Cancel the test charge to clean up."""
        headers = {
            "Content-Type": "application/json",
            "X-CC-Api-Key": self.api_key,
            "X-CC-Version": "2018-03-22"
        }

        try:
            response = requests.post(
                f"{self.base_url}/charges/{charge_id}/cancel",
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                self.log_result(
                    "Test Cleanup",
                    "INFO",
                    "Test charge cancelled successfully"
                )
            else:
                self.log_result(
                    "Test Cleanup",
                    "WARN",
                    f"Could not cancel test charge: {response.status_code}"
                )

        except Exception as e:
            self.log_result(
                "Test Cleanup",
                "WARN",
                f"Error cancelling test charge: {str(e)}"
            )

    def test_webhook_configuration(self):
        """Check webhook endpoint configuration."""
        webhook_url = "https://pay.synapse-lang.com/api/webhooks/coinbase"

        try:
            # Test if webhook endpoint is accessible
            response = requests.get(webhook_url, timeout=10)

            if response.status_code == 405:  # Method Not Allowed is expected for GET
                self.log_result(
                    "Webhook Endpoint",
                    "PASS",
                    "Webhook endpoint is accessible",
                    {"webhook_url": webhook_url}
                )
            elif response.status_code == 404:
                self.log_result(
                    "Webhook Endpoint",
                    "FAIL",
                    "Webhook endpoint not found - check deployment",
                    {"webhook_url": webhook_url}
                )
                return False
            else:
                self.log_result(
                    "Webhook Endpoint",
                    "WARN",
                    f"Unexpected response from webhook endpoint: {response.status_code}",
                    {"webhook_url": webhook_url}
                )

        except requests.exceptions.RequestException as e:
            self.log_result(
                "Webhook Endpoint",
                "FAIL",
                f"Cannot reach webhook endpoint: {str(e)}",
                {"webhook_url": webhook_url}
            )
            return False

        # Provide webhook setup instructions
        self.log_result(
            "Webhook Setup",
            "INFO",
            "Configure webhook in Coinbase Commerce dashboard",
            {
                "webhook_url": webhook_url,
                "events": ["charge:confirmed", "charge:failed", "charge:pending"],
                "secret": self.webhook_secret[:8] + "..." if self.webhook_secret else "NOT_SET"
            }
        )

        return True

    def test_oauth_setup(self):
        """Test OAuth client configuration."""
        if not self.oauth_client_id or not self.oauth_client_secret:
            self.log_result(
                "OAuth Setup",
                "WARN",
                "OAuth credentials not configured (optional feature)"
            )
            return True

        # Validate OAuth client ID format
        if len(self.oauth_client_id) != 36:  # Standard UUID length
            self.log_result(
                "OAuth Setup",
                "WARN",
                "OAuth client ID format may be incorrect",
                {"client_id_length": len(self.oauth_client_id)}
            )
        else:
            self.log_result(
                "OAuth Setup",
                "PASS",
                "OAuth credentials configured",
                {"client_id": self.oauth_client_id[:8] + "..."}
            )

        return True

    def generate_report(self):
        """Generate validation report."""
        passed = len([r for r in self.results if r["status"] == "PASS"])
        failed = len([r for r in self.results if r["status"] == "FAIL"])
        warnings = len([r for r in self.results if r["status"] == "WARN"])

        print("\n" + "="*50)
        print("COINBASE COMMERCE SETUP VALIDATION REPORT")
        print("="*50)
        print(f"Total Tests: {len(self.results)}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Warnings: {warnings}")
        print(f"Success Rate: {(passed / len(self.results)) * 100:.1f}%" if self.results else "0%")

        if failed == 0:
            print("\nSETUP VALIDATION PASSED! Your Coinbase Commerce integration is ready.")
            print("You can now accept cryptocurrency payments for Synapse Language!")
        else:
            print(f"\nSetup needs attention. {failed} critical issues found.")
            print("Please resolve the failed tests before going live.")

        # Save detailed report
        report_data = {
            "validation_timestamp": datetime.utcnow().isoformat(),
            "summary": {
                "total_tests": len(self.results),
                "passed": passed,
                "failed": failed,
                "warnings": warnings,
                "success_rate": (passed / len(self.results)) * 100 if self.results else 0
            },
            "detailed_results": self.results
        }

        with open("coinbase_setup_validation.json", "w") as f:
            json.dump(report_data, f, indent=2)

        print("\nDetailed report saved to: coinbase_setup_validation.json")

        return failed == 0

    def run_validation(self):
        """Run complete validation suite."""
        print("Validating Coinbase Commerce Setup for Synapse Language")
        print("=" * 60)

        # Run all validation tests
        self.test_environment_variables()
        self.test_api_connection()
        self.test_charge_creation()
        self.test_webhook_configuration()
        self.test_oauth_setup()

        # Generate report
        return self.generate_report()

def main():
    """Main validation execution."""
    validator = CoinbaseSetupValidator()
    success = validator.run_validation()

    if success:
        print("\nNext steps:")
        print("1. Deploy your payment service: ./deploy.sh")
        print("2. Test end-to-end payment flow")
        print("3. Configure webhooks in Coinbase Commerce dashboard")
        print("4. Go live and start accepting crypto payments!")
    else:
        print("\nNext steps:")
        print("1. Fix the failed validation tests")
        print("2. Re-run validation: python validate_setup.py")
        print("3. Contact support if you need assistance")

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
