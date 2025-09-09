#!/usr/bin/env python
"""
Synapse Language - Interactive PyPI Upload Script
"""

import os
import sys
import subprocess
from pathlib import Path
import getpass

def print_header():
    print("=" * 50)
    print("🚀 Synapse Language - PyPI Upload Tool")
    print("=" * 50)
    print()

def check_dist_files():
    """Check if distribution files exist."""
    dist_dir = Path("dist")
    if not dist_dir.exists():
        print("❌ Error: dist/ directory not found!")
        print("Run 'python -m build' first to create distribution files.")
        return False
    
    files = list(dist_dir.glob("synapse_lang-1.0.2*"))
    if not files:
        print("❌ Error: No distribution files found for version 1.0.2!")
        print("Run 'python -m build' first to create distribution files.")
        return False
    
    print("✅ Found distribution files:")
    for f in files:
        size = f.stat().st_size / 1024
        print(f"   - {f.name} ({size:.1f} KB)")
    print()
    return True

def get_token():
    """Get PyPI token from user."""
    print("📝 PyPI Authentication")
    print("-" * 30)
    print("You need a PyPI API token to upload.")
    print()
    print("To get a token:")
    print("1. Go to https://pypi.org/manage/account/token/")
    print("2. Create a new API token")
    print("3. Copy the token (starts with 'pypi-')")
    print()
    
    token = getpass.getpass("Enter your PyPI token (hidden): ")
    if not token.startswith("pypi-"):
        print("⚠️  Warning: Token should start with 'pypi-'")
        confirm = input("Continue anyway? (y/n): ")
        if confirm.lower() != 'y':
            return None
    
    return token

def upload_to_pypi(repository="pypi", token=None):
    """Upload to PyPI using twine."""
    if repository == "testpypi":
        print("\n📤 Uploading to Test PyPI...")
        cmd = ["python", "-m", "twine", "upload", "--repository", "testpypi", "dist/*"]
    else:
        print("\n📤 Uploading to Production PyPI...")
        cmd = ["python", "-m", "twine", "upload", "dist/*"]
    
    if token:
        cmd.extend(["-u", "__token__", "-p", token])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Upload successful!")
            return True
        else:
            print("❌ Upload failed!")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print_header()
    
    # Check distribution files
    if not check_dist_files():
        return 1
    
    # Choose repository
    print("🎯 Choose Upload Target")
    print("-" * 30)
    print("1. Test PyPI (recommended for first upload)")
    print("2. Production PyPI")
    print("3. Cancel")
    print()
    
    choice = input("Enter your choice (1-3): ").strip()
    
    if choice == "3":
        print("Upload cancelled.")
        return 0
    elif choice == "1":
        repository = "testpypi"
        print("\n✅ You selected: Test PyPI")
    elif choice == "2":
        repository = "pypi"
        print("\n✅ You selected: Production PyPI")
        print("⚠️  Warning: This will make the package publicly available!")
        confirm = input("Are you sure? (yes/no): ")
        if confirm.lower() != "yes":
            print("Upload cancelled.")
            return 0
    else:
        print("Invalid choice. Upload cancelled.")
        return 1
    
    # Get token
    print()
    token = get_token()
    if not token:
        print("No token provided. Upload cancelled.")
        return 1
    
    # Upload
    if upload_to_pypi(repository, token):
        print()
        print("=" * 50)
        print("🎉 Success! Your package has been uploaded.")
        print("=" * 50)
        
        if repository == "testpypi":
            print("\nTo test installation:")
            print("  pip install -i https://test.pypi.org/simple/ synapse-lang")
            print("\nOnce verified, run this script again to upload to production.")
        else:
            print("\nTo install:")
            print("  pip install synapse-lang")
            print("\nView your package at:")
            print("  https://pypi.org/project/synapse-lang/")
        
        return 0
    else:
        print("\n❌ Upload failed. Please check your token and try again.")
        print("If you continue to have issues:")
        print("1. Verify your PyPI account is active")
        print("2. Check that your token has the correct permissions")
        print("3. Try creating a new token")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nUpload cancelled by user.")
        sys.exit(1)