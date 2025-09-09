#!/usr/bin/env python3
"""
Synapse Language - Publication Script
Automates the process of publishing to PyPI
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import argparse

def run_command(cmd, check=True):
    """Run a shell command and return the result"""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)
    return result

def clean_build():
    """Clean previous build artifacts"""
    print("Cleaning build artifacts...")
    dirs_to_remove = ['build', 'dist', '*.egg-info', '__pycache__']
    for pattern in dirs_to_remove:
        for path in Path('.').glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
                print(f"  Removed {path}")

def run_tests():
    """Run test suite"""
    print("\nRunning tests...")
    result = run_command("python -m pytest tests/ -v", check=False)
    if result.returncode != 0:
        response = input("Tests failed. Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)

def check_version():
    """Check and update version"""
    version_file = Path("synapse_lang/__version__.py")
    current_version = "1.0.0"
    
    if version_file.exists():
        with open(version_file) as f:
            for line in f:
                if "__version__" in line:
                    current_version = line.split("=")[1].strip().strip('"')
                    break
    
    print(f"\nCurrent version: {current_version}")
    new_version = input("Enter new version (or press Enter to keep current): ").strip()
    
    if new_version and new_version != current_version:
        # Update version file
        with open(version_file, 'w') as f:
            f.write(f'"""Version information for Synapse Language"""\n\n')
            f.write(f'__version__ = "{new_version}"\n')
            version_parts = new_version.split('.')
            f.write(f'__version_info__ = ({", ".join(version_parts)})\n')
            f.write(f'__release_date__ = "{Path.cwd().name}"\n')
        
        # Update pyproject.toml
        pyproject = Path("pyproject.toml")
        if pyproject.exists():
            content = pyproject.read_text()
            content = content.replace(f'version = "{current_version}"', f'version = "{new_version}"')
            pyproject.write_text(content)
        
        print(f"Version updated to {new_version}")
        return new_version
    
    return current_version

def build_package():
    """Build the package"""
    print("\nBuilding package...")
    run_command("python -m build")
    
    # Check the build
    run_command("python -m twine check dist/*")
    
    # List built files
    print("\nBuilt files:")
    for file in Path("dist").glob("*"):
        print(f"  {file.name}")

def publish_to_test_pypi():
    """Publish to Test PyPI"""
    response = input("\nPublish to Test PyPI? (y/N): ")
    if response.lower() == 'y':
        print("Publishing to Test PyPI...")
        run_command("python -m twine upload --repository testpypi dist/*")
        print("\nPackage uploaded to Test PyPI!")
        print("Install with: pip install --index-url https://test.pypi.org/simple/ synapse-lang")

def publish_to_pypi():
    """Publish to PyPI"""
    response = input("\nPublish to PyPI? (y/N): ")
    if response.lower() == 'y':
        print("Publishing to PyPI...")
        run_command("python -m twine upload dist/*")
        print("\nPackage uploaded to PyPI!")
        print("Install with: pip install synapse-lang")

def create_git_tag(version):
    """Create and push git tag"""
    response = input(f"\nCreate git tag v{version}? (y/N): ")
    if response.lower() == 'y':
        run_command(f"git tag -a v{version} -m 'Release version {version}'")
        run_command(f"git push origin v{version}")
        print(f"Git tag v{version} created and pushed")

def main():
    parser = argparse.ArgumentParser(description="Publish Synapse Language to PyPI")
    parser.add_argument("--skip-tests", action="store_true", help="Skip running tests")
    parser.add_argument("--skip-clean", action="store_true", help="Skip cleaning build artifacts")
    parser.add_argument("--test-only", action="store_true", help="Only publish to Test PyPI")
    parser.add_argument("--no-tag", action="store_true", help="Don't create git tag")
    args = parser.parse_args()
    
    print("=" * 60)
    print("Synapse Language - Publication Script")
    print("=" * 60)
    
    # Check requirements
    requirements = ["build", "twine", "pytest"]
    for req in requirements:
        result = run_command(f"python -m pip show {req}", check=False)
        if result.returncode != 0:
            print(f"Installing {req}...")
            run_command(f"python -m pip install {req}")
    
    # Clean build artifacts
    if not args.skip_clean:
        clean_build()
    
    # Run tests
    if not args.skip_tests:
        run_tests()
    
    # Check version
    version = check_version()
    
    # Build package
    build_package()
    
    # Publish to Test PyPI
    publish_to_test_pypi()
    
    # Publish to PyPI (if not test-only)
    if not args.test_only:
        publish_to_pypi()
    
    # Create git tag
    if not args.no_tag:
        create_git_tag(version)
    
    print("\n" + "=" * 60)
    print("Publication complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()