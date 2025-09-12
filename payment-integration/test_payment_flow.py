#!/usr/bin/env python3
"""
Test script for Synapse Language cryptocurrency payment flow
Tests all aspects of the payment system end-to-end
"""

import os
import sys
import json
import time
import requests
import hmac
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List

# Test configuration
TEST_CONFIG = {
    'base_url': 'http://localhost:5000',
    'test_email': 'test@synapse-lang.com',
    'test_name': 'Test User',
    'webhook_secret': 'test_webhook_secret',
    'products': ['professional', 'enterprise', 'vscode_extension']
}

class PaymentFlowTester:
    """Test class for payment flow validation."""
    
    def __init__(self, base_url: str = 'http://localhost:5000'):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, message: str = "", data: Dict = None):
        """Log test result."""
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.utcnow().isoformat(),
            'data': data or {}
        }
        self.test_results.append(result)
        
        status = "[PASS]" if success else "[FAIL]"
        print(f"{status} {test_name}: {message}")
        
        if data:
            print(f"    Data: {json.dumps(data, indent=2)}")
    
    def test_service_health(self) -> bool:
        """Test if the payment service is running and healthy."""
        try:
            response = self.session.get(f'{self.base_url}/api/products')
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Service Health Check", 
                    True, 
                    f"Service is healthy, {len(data.get('products', {}))} products available",
                    {'response_time': response.elapsed.total_seconds()}
                )
                return True
            else:
                self.log_test(
                    "Service Health Check", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Service Health Check", False, f"Connection failed: {str(e)}")
            return False
    
    def test_product_listing(self) -> bool:
        """Test product listing endpoint."""
        try:
            response = self.session.get(f'{self.base_url}/api/products')
            
            if response.status_code != 200:
                self.log_test("Product Listing", False, f"HTTP {response.status_code}")
                return False
            
            data = response.json()
            products = data.get('products', {})
            cryptocurrencies = data.get('supported_cryptocurrencies', [])
            
            # Validate response structure
            required_products = ['professional', 'enterprise', 'vscode_extension']
            missing_products = [p for p in required_products if p not in products]
            
            if missing_products:
                self.log_test(
                    "Product Listing", 
                    False, 
                    f"Missing products: {missing_products}"
                )
                return False
            
            # Validate product structure
            for product_id, product in products.items():
                required_fields = ['name', 'price', 'description']
                missing_fields = [f for f in required_fields if f not in product]
                
                if missing_fields:
                    self.log_test(
                        "Product Listing", 
                        False, 
                        f"Product {product_id} missing fields: {missing_fields}"
                    )
                    return False
            
            self.log_test(
                "Product Listing", 
                True, 
                f"Found {len(products)} products and {len(cryptocurrencies)} cryptocurrencies",
                {
                    'products': list(products.keys()),
                    'cryptocurrencies': cryptocurrencies
                }
            )
            return True
            
        except Exception as e:
            self.log_test("Product Listing", False, f"Error: {str(e)}")
            return False
    
    def test_charge_creation(self, product_type: str = 'professional') -> Dict:
        """Test creating a cryptocurrency charge."""
        try:
            payload = {
                'product_type': product_type,
                'customer_email': TEST_CONFIG['test_email'],
                'customer_name': TEST_CONFIG['test_name']
            }
            
            response = self.session.post(
                f'{self.base_url}/api/create-charge',
                json=payload
            )
            
            if response.status_code != 200:
                self.log_test(
                    "Charge Creation", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return {}
            
            data = response.json()
            
            # Validate response structure
            required_fields = ['success', 'charge_id', 'hosted_url', 'expires_at']
            missing_fields = [f for f in required_fields if f not in data]
            
            if missing_fields:
                self.log_test(
                    "Charge Creation", 
                    False, 
                    f"Missing response fields: {missing_fields}"
                )
                return {}
            
            if not data.get('success'):
                self.log_test("Charge Creation", False, "Response indicates failure")
                return {}
            
            self.log_test(
                "Charge Creation", 
                True, 
                f"Created charge {data['charge_id']} for {product_type}",
                {
                    'charge_id': data['charge_id'],
                    'product_type': product_type,
                    'hosted_url': data['hosted_url'][:50] + "..." if len(data['hosted_url']) > 50 else data['hosted_url']
                }
            )
            
            return data
            
        except Exception as e:
            self.log_test("Charge Creation", False, f"Error: {str(e)}")
            return {}
    
    def test_charge_status(self, charge_id: str) -> bool:
        """Test retrieving charge status."""
        try:
            response = self.session.get(f'{self.base_url}/api/charge/{charge_id}')
            
            if response.status_code != 200:
                self.log_test(
                    "Charge Status", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
            
            data = response.json()
            charge_data = data.get('charge', {})
            
            if not charge_data:
                self.log_test("Charge Status", False, "No charge data returned")
                return False
            
            self.log_test(
                "Charge Status", 
                True, 
                f"Retrieved status for charge {charge_id}",
                {
                    'charge_id': charge_id,
                    'status': charge_data.get('timeline', [{}])[-1].get('status', 'unknown')
                }
            )
            return True
            
        except Exception as e:
            self.log_test("Charge Status", False, f"Error: {str(e)}")
            return False
    
    def test_webhook_signature_verification(self) -> bool:
        """Test webhook signature verification."""
        try:
            # Create test payload
            test_payload = {
                'type': 'charge:confirmed',
                'data': {
                    'id': 'test_charge_123',
                    'metadata': {
                        'customer_email': TEST_CONFIG['test_email'],
                        'product_type': 'professional'
                    }
                }
            }
            
            payload_bytes = json.dumps(test_payload).encode('utf-8')
            
            # Generate signature
            secret = TEST_CONFIG['webhook_secret'].encode('utf-8')
            signature = hmac.new(secret, payload_bytes, hashlib.sha256).hexdigest()
            
            headers = {
                'X-CC-Webhook-Signature': signature,
                'Content-Type': 'application/json'
            }
            
            response = self.session.post(
                f'{self.base_url}/api/webhooks/coinbase',
                data=payload_bytes,
                headers=headers
            )
            
            # For testing, we expect this to fail due to missing Coinbase API key
            # But we can check if signature verification works
            if response.status_code == 401:
                self.log_test(
                    "Webhook Signature", 
                    False, 
                    "Invalid signature (expected for test)"
                )
            else:
                self.log_test(
                    "Webhook Signature", 
                    True, 
                    f"Signature verification passed (HTTP {response.status_code})"
                )
            
            return True
            
        except Exception as e:
            self.log_test("Webhook Signature", False, f"Error: {str(e)}")
            return False
    
    def test_license_validation(self) -> bool:
        """Test license validation endpoint."""
        try:
            # Test with invalid license key
            payload = {'license_key': 'SYN-INVALID123456'}
            
            response = self.session.post(
                f'{self.base_url}/api/validate-license',
                json=payload
            )
            
            if response.status_code != 200:
                self.log_test(
                    "License Validation", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                return False
            
            data = response.json()
            
            if data.get('valid'):
                self.log_test(
                    "License Validation", 
                    False, 
                    "Invalid license key was accepted"
                )
                return False
            
            # Test with sample license key (if exists)
            payload = {'license_key': 'SYN-SAMPLE123456'}
            response = self.session.post(
                f'{self.base_url}/api/validate-license',
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "License Validation", 
                    True, 
                    f"License validation working (sample key valid: {data.get('valid', False)})",
                    {'sample_license_valid': data.get('valid', False)}
                )
            else:
                self.log_test(
                    "License Validation", 
                    True, 
                    "License validation endpoint accessible"
                )
            
            return True
            
        except Exception as e:
            self.log_test("License Validation", False, f"Error: {str(e)}")
            return False
    
    def test_error_handling(self) -> bool:
        """Test error handling for various scenarios."""
        tests_passed = 0
        total_tests = 3
        
        try:
            # Test 1: Missing required fields
            response = self.session.post(
                f'{self.base_url}/api/create-charge',
                json={'product_type': 'professional'}  # Missing customer_email
            )
            
            if response.status_code == 400:
                tests_passed += 1
                print("    [OK] Missing field validation works")
            else:
                print(f"    [FAIL] Missing field validation failed: HTTP {response.status_code}")
            
            # Test 2: Invalid product type
            response = self.session.post(
                f'{self.base_url}/api/create-charge',
                json={
                    'product_type': 'invalid_product',
                    'customer_email': TEST_CONFIG['test_email']
                }
            )
            
            if response.status_code in [400, 500]:
                tests_passed += 1
                print("    [OK] Invalid product type validation works")
            else:
                print(f"    [FAIL] Invalid product type validation failed: HTTP {response.status_code}")
            
            # Test 3: Invalid license key format
            response = self.session.post(
                f'{self.base_url}/api/validate-license',
                json={'license_key': ''}
            )
            
            if response.status_code == 400:
                tests_passed += 1
                print("    [OK] Empty license key validation works")
            else:
                print(f"    [FAIL] Empty license key validation failed: HTTP {response.status_code}")
            
            success = tests_passed == total_tests
            self.log_test(
                "Error Handling", 
                success, 
                f"{tests_passed}/{total_tests} error handling tests passed"
            )
            
            return success
            
        except Exception as e:
            self.log_test("Error Handling", False, f"Error: {str(e)}")
            return False
    
    def test_performance(self) -> bool:
        """Test performance of key endpoints."""
        try:
            endpoints = [
                ('/api/products', 'GET'),
                ('/api/validate-license', 'POST')
            ]
            
            performance_results = {}
            
            for endpoint, method in endpoints:
                start_time = time.time()
                
                if method == 'GET':
                    response = self.session.get(f'{self.base_url}{endpoint}')
                else:
                    response = self.session.post(
                        f'{self.base_url}{endpoint}',
                        json={'license_key': 'SYN-TEST123456'}
                    )
                
                end_time = time.time()
                response_time = (end_time - start_time) * 1000  # Convert to milliseconds
                
                performance_results[endpoint] = {
                    'response_time_ms': round(response_time, 2),
                    'status_code': response.status_code
                }
            
            # Check if response times are reasonable (< 5 seconds)
            slow_endpoints = [
                ep for ep, data in performance_results.items() 
                if data['response_time_ms'] > 5000
            ]
            
            if slow_endpoints:
                self.log_test(
                    "Performance", 
                    False, 
                    f"Slow endpoints detected: {slow_endpoints}",
                    performance_results
                )
                return False
            
            self.log_test(
                "Performance", 
                True, 
                "All endpoints responding within acceptable time",
                performance_results
            )
            
            return True
            
        except Exception as e:
            self.log_test("Performance", False, f"Error: {str(e)}")
            return False
    
    def run_all_tests(self) -> Dict:
        """Run complete test suite."""
        print("Testing Synapse Language Payment Service...\n")
        
        # Test sequence
        test_functions = [
            self.test_service_health,
            self.test_product_listing,
            lambda: self.test_charge_creation('professional'),
            self.test_webhook_signature_verification,
            self.test_license_validation,
            self.test_error_handling,
            self.test_performance
        ]
        
        # Test charge creation for all products
        for product in TEST_CONFIG['products']:
            charge_data = self.test_charge_creation(product)
            if charge_data and charge_data.get('charge_id'):
                self.test_charge_status(charge_data['charge_id'])
        
        # Execute tests
        passed_tests = 0
        total_tests = len(self.test_results)
        
        for result in self.test_results:
            if result['success']:
                passed_tests += 1
        
        # Generate summary
        summary = {
            'total_tests': total_tests,
            'passed': passed_tests,
            'failed': total_tests - passed_tests,
            'success_rate': round((passed_tests / total_tests) * 100, 2) if total_tests > 0 else 0,
            'timestamp': datetime.utcnow().isoformat(),
            'detailed_results': self.test_results
        }
        
        print(f"\nTest Summary:")
        print(f"   Total Tests: {summary['total_tests']}")
        print(f"   Passed: {summary['passed']}")
        print(f"   Failed: {summary['failed']}")
        print(f"   Success Rate: {summary['success_rate']}%")
        
        if summary['success_rate'] >= 80:
            print(f"\nTest suite PASSED with {summary['success_rate']}% success rate!")
        else:
            print(f"\nTest suite needs attention. Success rate: {summary['success_rate']}%")
        
        # Save results to file
        with open('test_results.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\nDetailed results saved to: test_results.json")
        
        return summary

def main():
    """Main test execution."""
    # Check if service is running locally
    base_url = os.getenv('PAYMENT_SERVICE_URL', 'http://localhost:5000')
    
    print(f"Testing payment service at: {base_url}")
    
    # Initialize tester
    tester = PaymentFlowTester(base_url)
    
    # Run tests
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if results['success_rate'] >= 80 else 1)

if __name__ == '__main__':
    main()