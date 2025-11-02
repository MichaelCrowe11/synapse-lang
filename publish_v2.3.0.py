#!/usr/bin/env python3
"""
Automated PyPI Publishing Script for Synapse v2.3.0
Ready to execute with your PyPI token
"""

import getpass
import os
import subprocess
import sys
from pathlib import Path


def print_banner():
    """Display banner"""
    print("=" * 60)
    print("🚀 SYNAPSE LANGUAGE v2.3.0 - PyPI PUBLISHER")
    print("=" * 60)
    print()


def check_package():
    """Verify package exists"""
    package_path = Path("dist/synapse-lang-2.3.0.tar.gz")

    if not package_path.exists():
        print("❌ ERROR: Package not found at dist/synapse-lang-2.3.0.tar.gz")
        print("Please run: python setup.py sdist")
        return False

    size_kb = package_path.stat().st_size / 1024
    print(f"✅ Package found: {package_path.name} ({size_kb:.1f} KB)")
    print()
    return True


def check_twine():
    """Check if twine is installed"""
    try:
        subprocess.run(["twine", "--version"], capture_output=True, check=True)
        print("✅ Twine is installed")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Twine not found. Installing...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "twine"], check=True)
            print("✅ Twine installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install twine")
            return False


def get_token():
    """Get PyPI token from user or environment"""
    # Check environment variable first
    token = os.environ.get("PYPI_TOKEN")

    if token:
        print("✅ Found PyPI token in environment variable")
        return token

    print("📝 PyPI Authentication Required")
    print("-" * 40)
    print("To get a token:")
    print("1. Go to: https://pypi.org/manage/account/token/")
    print("2. Create a new API token")
    print("3. Copy the token (starts with 'pypi-')")
    print()

    token = getpass.getpass("Enter your PyPI token (hidden): ").strip()

    if not token:
        print("❌ No token provided")
        return None

    if not token.startswith("pypi-"):
        print("⚠️  Warning: Token should start with 'pypi-'")
        confirm = input("Continue anyway? (y/n): ")
        if confirm.lower() != "y":
            return None

    return token


def publish_to_pypi(token, test_mode=False):
    """Upload package to PyPI"""
    if test_mode:
        print("\n📤 Uploading to Test PyPI...")
        cmd = [
            sys.executable, "-m", "twine", "upload",
            "--repository", "testpypi",
            "--username", "__token__",
            "--password", token,
            "dist/synapse-lang-2.3.0.tar.gz"
        ]
    else:
        print("\n📤 Uploading to Production PyPI...")
        cmd = [
            sys.executable, "-m", "twine", "upload",
            "--username", "__token__",
            "--password", token,
            "dist/synapse-lang-2.3.0.tar.gz"
        ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Upload successful!")
            return True
        else:
            print("❌ Upload failed!")
            if "403" in result.stderr:
                print("Authentication error - check your token")
            elif "400" in result.stderr:
                print("Package validation error")
            elif "already exists" in result.stderr.lower():
                print("Version 2.3.0 already exists on PyPI")
            else:
                print(f"Error: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Error during upload: {e}")
        return False


def main():
    """Main execution"""
    print_banner()

    # Check prerequisites
    if not check_package():
        return 1

    if not check_twine():
        return 1

    print()
    print("📋 PACKAGE DETAILS")
    print("-" * 40)
    print("Name:     synapse-lang")
    print("Version:  2.3.0")
    print("Size:     348 KB")
    print("Features: 8 major enhancements")
    print()

    # Choose target
    print("🎯 SELECT UPLOAD TARGET")
    print("-" * 40)
    print("1. Test PyPI (recommended for first attempt)")
    print("2. Production PyPI (live release)")
    print("3. Cancel")
    print()

    choice = input("Your choice (1-3): ").strip()

    if choice == "3":
        print("\n❌ Upload cancelled")
        return 0

    test_mode = (choice == "1")

    if choice == "2":
        print("\n⚠️  PRODUCTION RELEASE WARNING")
        print("This will make v2.3.0 publicly available on PyPI")
        confirm = input("Are you absolutely sure? (type 'yes' to confirm): ")
        if confirm != "yes":
            print("\n❌ Upload cancelled")
            return 0

    # Get token
    print()
    token = get_token()
    if not token:
        print("\n❌ No token provided. Upload cancelled.")
        return 1

    # Publish
    if publish_to_pypi(token, test_mode):
        print()
        print("=" * 60)
        print("🎉 SUCCESS! Synapse v2.3.0 has been uploaded!")
        print("=" * 60)

        if test_mode:
            print("\n📦 Test Installation:")
            print("pip install --index-url https://test.pypi.org/simple/ synapse-lang==2.3.0")
            print("\nOnce verified, run this script again for production release.")
        else:
            print("\n📦 Installation:")
            print("pip install synapse-lang")
            print("\n🌐 View Package:")
            print("https://pypi.org/project/synapse-lang/")
            print("\n📊 Statistics:")
            print("https://pypistats.org/packages/synapse-lang")
            print("\n🎯 Next Steps:")
            print("1. Test installation in a fresh environment")
            print("2. Create GitHub release tag v2.3.0")
            print("3. Announce on social media")
            print("4. Update documentation website")

        print()
        return 0
    else:
        print("\n❌ Upload failed. Please check your token and try again.")
        print("\nTroubleshooting:")
        print("1. Verify your PyPI account is active")
        print("2. Check token permissions")
        print("3. Ensure 'synapse-lang' package name is available")
        print("4. Try Test PyPI first")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n❌ Upload cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
