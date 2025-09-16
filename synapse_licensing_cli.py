#!/usr/bin/env python3
"""
Synapse-Lang License Management CLI
"""

import argparse
import sys

from synapse_licensing import LicenseManager, LicenseType, get_license_manager


def main():
    parser = argparse.ArgumentParser(
        description="Synapse-Lang License Management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  synapse-license status              # Show current license status
  synapse-license activate KEY EMAIL  # Activate a license
  synapse-license generate --type enterprise  # Generate test license
  synapse-license features            # List available features
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Status command
    subparsers.add_parser("status", help="Show license status")

    # Activate command
    activate_parser = subparsers.add_parser("activate", help="Activate license")
    activate_parser.add_argument("key", help="License key")
    activate_parser.add_argument("email", help="Email address")

    # Generate command (for testing)
    generate_parser = subparsers.add_parser("generate", help="Generate test license")
    generate_parser.add_argument(
        "--type",
        choices=["community", "professional", "enterprise", "academic", "trial"],
        default="trial",
        help="License type"
    )
    generate_parser.add_argument("--seed", help="Seed for reproducible key")

    # Features command
    subparsers.add_parser("features", help="List features")

    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate license key")
    validate_parser.add_argument("key", help="License key to validate")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    lm = get_license_manager()

    if args.command == "status":
        show_status(lm)

    elif args.command == "activate":
        activate_license(lm, args.key, args.email)

    elif args.command == "generate":
        generate_license(lm, args.type, args.seed)

    elif args.command == "features":
        show_features(lm)

    elif args.command == "validate":
        validate_key(lm, args.key)

    return 0

def show_status(lm: LicenseManager):
    """Show current license status"""
    info = lm.get_license_info()

    print("="*60)
    print("SYNAPSE-LANG LICENSE STATUS")
    print("="*60)
    print(f"License Type:    {info['type'].upper()}")
    print(f"Owner:           {info['owner']}")
    print(f"Organization:    {info['organization'] or 'N/A'}")
    print(f"Email:           {info['email']}")
    print(f"Issued:          {info['issued']}")
    print(f"Expires:         {info['expires']}")
    print(f"Max Cores:       {info['max_cores']}")
    print(f"Max Qubits:      {info['max_qubits']}")
    print("-"*60)
    print("Active Features:")
    for feature in info["features"]:
        print(f"  ✓ {feature}")
    print("="*60)

def activate_license(lm: LicenseManager, key: str, email: str):
    """Activate a license key"""
    try:
        if lm.activate_license(key, email):
            print("✅ License activated successfully!")
            print(f"License Key: {key}")
            print(f"Email: {email}")
            show_status(lm)
        else:
            print("❌ Failed to activate license")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

def generate_license(lm: LicenseManager, license_type: str, seed: str = None):
    """Generate a test license key"""
    type_enum = LicenseType(license_type)
    key = lm.generate_license_key(type_enum, seed)

    print("="*60)
    print("GENERATED LICENSE KEY")
    print("="*60)
    print(f"Type:     {license_type.upper()}")
    print(f"Key:      {key}")
    print("-"*60)
    print("Features included:")
    for feature in lm.FEATURE_SETS[type_enum]:
        print(f"  ✓ {feature.value}")
    print("-"*60)
    print(f"To activate: synapse-license activate {key} your@email.com")
    print("="*60)

def show_features(lm: LicenseManager):
    """Show features by license type"""
    print("="*60)
    print("SYNAPSE-LANG FEATURES BY LICENSE TYPE")
    print("="*60)

    for license_type in LicenseType:
        features = lm.FEATURE_SETS[license_type]
        print(f"\n{license_type.value.upper()} Edition:")
        print("-"*40)
        for feature in features:
            print(f"  ✓ {feature.value}")

    print("\n" + "="*60)

def validate_key(lm: LicenseManager, key: str):
    """Validate a license key"""
    if lm.validate_license_key(key):
        print(f"✅ License key format is valid: {key}")

        # Determine type
        license_type = lm._determine_license_type(key)
        print(f"License Type: {license_type.value.upper()}")
    else:
        print(f"❌ Invalid license key format: {key}")
        print("Expected format: XXXX-XXXX-XXXX-XXXX-XXXX")
        sys.exit(1)

if __name__ == "__main__":
    sys.exit(main())
