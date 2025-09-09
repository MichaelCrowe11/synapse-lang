#!/usr/bin/env python3
"""
Synapse Language - License Key Generator
For internal use only - generates license keys for customers
"""

import hashlib
import json
import time
from datetime import datetime, timedelta
import argparse
import secrets
import base64

class LicenseGenerator:
    """Generate license keys for Synapse Language"""
    
    # Secret key for signing (in production, use proper key management)
    SECRET_KEY = "SYNAPSE-2024-SECRET-KEY-REPLACE-IN-PRODUCTION"
    
    LICENSE_TYPES = {
        "evaluation": 30,  # 30 days
        "personal": 365,  # 1 year
        "professional": 365,  # 1 year
        "enterprise": 365,  # 1 year
        "academic": 365,  # 1 year
    }
    
    def __init__(self):
        self.generated_licenses = []
    
    def generate_key(self, license_type: str, email: str, 
                     machine_id: Optional[str] = None,
                     days: Optional[int] = None) -> Dict:
        """Generate a license key"""
        
        if license_type not in self.LICENSE_TYPES:
            raise ValueError(f"Invalid license type: {license_type}")
        
        # Calculate expiration
        days = days or self.LICENSE_TYPES[license_type]
        expires = datetime.now() + timedelta(days=days)
        expires_timestamp = int(expires.timestamp())
        
        # Generate license components
        license_id = secrets.token_hex(8)
        machine = machine_id or "ANY"
        
        # Create license key
        key_parts = [
            license_type.upper()[:4],
            str(expires_timestamp)[-8:],
            license_id[:8],
            machine[:8] if machine != "ANY" else "ANY00000",
        ]
        
        # Generate signature
        signature_data = f"{license_type}{expires_timestamp}{license_id}{machine}{self.SECRET_KEY}"
        signature = hashlib.sha256(signature_data.encode()).hexdigest()[:8].upper()
        key_parts.append(signature)
        
        license_key = "-".join(key_parts)
        
        # Store license info
        license_info = {
            "key": license_key,
            "type": license_type,
            "email": email,
            "machine_id": machine_id,
            "expires": expires.isoformat(),
            "created": datetime.now().isoformat(),
            "license_id": license_id,
        }
        
        self.generated_licenses.append(license_info)
        
        return license_info
    
    def generate_batch(self, license_type: str, count: int) -> List[Dict]:
        """Generate multiple license keys"""
        licenses = []
        for i in range(count):
            email = f"customer{i+1}@example.com"
            license_info = self.generate_key(license_type, email)
            licenses.append(license_info)
        return licenses
    
    def save_licenses(self, filename: str = "licenses.json"):
        """Save generated licenses to file"""
        with open(filename, 'w') as f:
            json.dump(self.generated_licenses, f, indent=2)
        print(f"Saved {len(self.generated_licenses)} licenses to {filename}")
    
    def format_license_email(self, license_info: Dict) -> str:
        """Format license information for customer email"""
        return f"""
Dear Customer,

Thank you for purchasing Synapse Language {license_info['type'].title()} Edition!

Your License Information:
========================
License Key: {license_info['key']}
Type: {license_info['type'].title()}
Expires: {license_info['expires'][:10]}
Email: {license_info['email']}

Installation Instructions:
========================
1. Install Synapse Language:
   pip install synapse-lang

2. Activate your license:
   synapse --activate-license {license_info['key']}

3. Verify activation:
   synapse --license-info

Features Included:
==================
{self._get_features_text(license_info['type'])}

Support:
========
Email: support@synapse-lang.com
Documentation: https://synapse-lang.com/docs

Thank you for choosing Synapse Language!

Best regards,
The Synapse Team
"""
    
    def _get_features_text(self, license_type: str) -> str:
        """Get features text for license type"""
        features = {
            "evaluation": """
- 30-day trial period
- Limited to 2 CPU cores
- Basic features only
- Community support
""",
            "personal": """
- 1 year license
- Up to 8 CPU cores
- Personal use only
- Email support
- JIT compilation
""",
            "professional": """
- 1 year license
- Up to 16 CPU cores
- Commercial use allowed
- Priority support
- JIT compilation
- GPU acceleration
""",
            "enterprise": """
- 1 year license
- Unlimited CPU cores
- Commercial use allowed
- Priority support with SLA
- All features unlocked
- GPU acceleration
- Quantum computing modules
- Custom feature development
""",
            "academic": """
- 1 year license
- Educational use only
- All features unlocked
- GPU acceleration
- Quantum computing modules
- Email support
"""
        }
        return features.get(license_type, "Standard features")

def main():
    parser = argparse.ArgumentParser(description="Generate Synapse Language license keys")
    parser.add_argument("--type", choices=["evaluation", "personal", "professional", "enterprise", "academic"],
                       required=True, help="License type")
    parser.add_argument("--email", required=True, help="Customer email")
    parser.add_argument("--machine", help="Machine ID (optional, for node-locked licenses)")
    parser.add_argument("--days", type=int, help="Override default duration in days")
    parser.add_argument("--batch", type=int, help="Generate multiple licenses")
    parser.add_argument("--save", action="store_true", help="Save licenses to file")
    parser.add_argument("--format-email", action="store_true", help="Format as customer email")
    
    args = parser.parse_args()
    
    generator = LicenseGenerator()
    
    if args.batch:
        licenses = generator.generate_batch(args.type, args.batch)
        for license_info in licenses:
            print(f"Generated: {license_info['key']}")
    else:
        license_info = generator.generate_key(
            args.type, 
            args.email,
            args.machine,
            args.days
        )
        
        if args.format_email:
            print(generator.format_license_email(license_info))
        else:
            print(f"Generated License Key: {license_info['key']}")
            print(f"Type: {license_info['type']}")
            print(f"Email: {license_info['email']}")
            print(f"Expires: {license_info['expires'][:10]}")
    
    if args.save:
        generator.save_licenses()

if __name__ == "__main__":
    main()