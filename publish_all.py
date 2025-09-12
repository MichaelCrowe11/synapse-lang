#!/usr/bin/env python3
"""
Synapse Language - Universal Publishing Script
Publishes to PyPI, VS Code Marketplace, npm, and other platforms
"""

import os
import sys
import json
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Optional
import argparse


class SynapsePublisher:
    """Handles publishing to multiple platforms."""
    
    def __init__(self, dry_run: bool = False, verbose: bool = False):
        self.dry_run = dry_run
        self.verbose = verbose
        self.root_dir = Path(__file__).parent
        self.version = self.get_version()
        
    def get_version(self) -> str:
        """Get current version from __init__.py."""
        init_file = self.root_dir / "synapse_lang" / "__init__.py"
        with open(init_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith("__version__"):
                    return line.split('"')[1]
        raise ValueError("Version not found")
    
    def run_command(self, cmd: List[str], cwd: Optional[Path] = None) -> int:
        """Run a command with optional dry-run mode."""
        if self.dry_run:
            print(f"[DRY RUN] Would execute: {' '.join(cmd)}")
            return 0
        
        if self.verbose:
            print(f"[EXEC] {' '.join(cmd)}")
        
        result = subprocess.run(cmd, cwd=cwd or self.root_dir, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"[ERROR] Command failed: {' '.join(cmd)}")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
        
        return result.returncode
    
    def clean_build_dirs(self):
        """Clean previous build directories."""
        print("\n[1/8] Cleaning build directories...")
        
        dirs_to_clean = ["build", "dist", "*.egg-info", "__pycache__"]
        for pattern in dirs_to_clean:
            for path in self.root_dir.glob(pattern):
                if self.dry_run:
                    print(f"[DRY RUN] Would remove: {path}")
                else:
                    if path.is_dir():
                        shutil.rmtree(path)
                    else:
                        path.unlink()
                    if self.verbose:
                        print(f"Removed: {path}")
    
    def run_tests(self) -> bool:
        """Run test suite before publishing."""
        print("\n[2/8] Running tests...")
        
        # Run pytest
        result = self.run_command([sys.executable, "-m", "pytest", "tests/", "-v"])
        if result != 0:
            print("[ERROR] Tests failed. Fix issues before publishing.")
            return False
        
        print("[SUCCESS] All tests passed!")
        return True
    
    def build_python_package(self) -> bool:
        """Build Python package for PyPI."""
        print("\n[3/8] Building Python package...")
        
        # Build source distribution and wheel
        result = self.run_command([sys.executable, "-m", "build"])
        if result != 0:
            print("[ERROR] Failed to build Python package")
            return False
        
        print(f"[SUCCESS] Built Python package version {self.version}")
        return True
    
    def publish_to_pypi(self, test: bool = False) -> bool:
        """Publish to PyPI or TestPyPI."""
        target = "TestPyPI" if test else "PyPI"
        print(f"\n[4/8] Publishing to {target}...")
        
        if test:
            # Upload to TestPyPI
            cmd = [
                sys.executable, "-m", "twine", "upload",
                "--repository", "testpypi",
                "dist/*"
            ]
        else:
            # Upload to PyPI
            cmd = [sys.executable, "-m", "twine", "upload", "dist/*"]
        
        result = self.run_command(cmd)
        if result != 0:
            print(f"[ERROR] Failed to upload to {target}")
            return False
        
        print(f"[SUCCESS] Published to {target}!")
        print(f"Install with: pip install {'--index-url https://test.pypi.org/simple/ ' if test else ''}synapse-lang=={self.version}")
        return True
    
    def build_vscode_extension(self) -> bool:
        """Build VS Code extension."""
        print("\n[5/8] Building VS Code extension...")
        
        vscode_dir = self.root_dir / "vscode-extension"
        if not vscode_dir.exists():
            print("[WARNING] VS Code extension directory not found")
            return False
        
        # Update version in package.json
        package_json = vscode_dir / "package.json"
        if package_json.exists():
            with open(package_json, 'r') as f:
                data = json.load(f)
            
            data['version'] = self.version
            
            if not self.dry_run:
                with open(package_json, 'w') as f:
                    json.dump(data, f, indent=2)
            
            print(f"Updated VS Code extension version to {self.version}")
        
        # Install dependencies
        result = self.run_command(["npm", "install"], cwd=vscode_dir)
        if result != 0:
            print("[ERROR] Failed to install VS Code extension dependencies")
            return False
        
        # Build extension
        result = self.run_command(["vsce", "package"], cwd=vscode_dir)
        if result != 0:
            print("[ERROR] Failed to build VS Code extension")
            print("Make sure vsce is installed: npm install -g vsce")
            return False
        
        print("[SUCCESS] Built VS Code extension!")
        return True
    
    def publish_to_vscode_marketplace(self) -> bool:
        """Publish to VS Code Marketplace."""
        print("\n[6/8] Publishing to VS Code Marketplace...")
        
        vscode_dir = self.root_dir / "vscode-extension"
        
        # Publish extension
        result = self.run_command(["vsce", "publish"], cwd=vscode_dir)
        if result != 0:
            print("[ERROR] Failed to publish to VS Code Marketplace")
            print("Make sure you're logged in: vsce login <publisher>")
            return False
        
        print("[SUCCESS] Published to VS Code Marketplace!")
        print(f"Install with: code --install-extension synapse-lang.synapse-lang")
        return True
    
    def publish_to_npm(self) -> bool:
        """Publish to npm registry."""
        print("\n[7/8] Publishing to npm...")
        
        # Check if package.json exists in root
        package_json = self.root_dir / "package.json"
        if not package_json.exists():
            # Create package.json for npm
            npm_package = {
                "name": "@synapse-lang/core",
                "version": self.version,
                "description": "Synapse Programming Language - Core Runtime",
                "main": "index.js",
                "scripts": {
                    "test": "echo \"Error: no test specified\" && exit 1"
                },
                "keywords": ["synapse", "programming-language", "scientific-computing"],
                "author": "Michael Benjamin Crowe",
                "license": "Proprietary",
                "repository": {
                    "type": "git",
                    "url": "https://github.com/MichaelCrowe11/synapse-lang.git"
                }
            }
            
            if not self.dry_run:
                with open(package_json, 'w') as f:
                    json.dump(npm_package, f, indent=2)
        
        # Publish to npm
        result = self.run_command(["npm", "publish", "--access=public"])
        if result != 0:
            print("[ERROR] Failed to publish to npm")
            print("Make sure you're logged in: npm login")
            return False
        
        print("[SUCCESS] Published to npm!")
        print(f"Install with: npm install @synapse-lang/core@{self.version}")
        return True
    
    def create_github_release(self) -> bool:
        """Create GitHub release with assets."""
        print("\n[8/8] Creating GitHub release...")
        
        # Create release using GitHub CLI
        cmd = [
            "gh", "release", "create",
            f"v{self.version}",
            "--title", f"Synapse Language v{self.version}",
            "--notes-file", "CHANGELOG.md",
            "dist/*"  # Upload built packages
        ]
        
        result = self.run_command(cmd)
        if result != 0:
            print("[ERROR] Failed to create GitHub release")
            print("Make sure GitHub CLI is installed and authenticated")
            return False
        
        print(f"[SUCCESS] Created GitHub release v{self.version}!")
        return True
    
    def publish_all(self, platforms: List[str], test_pypi: bool = False):
        """Publish to all specified platforms."""
        print(f"\n{'='*60}")
        print(f"Synapse Language Publisher v{self.version}")
        print(f"{'='*60}")
        
        if self.dry_run:
            print("[MODE] DRY RUN - No actual changes will be made")
        
        # Clean build directories
        self.clean_build_dirs()
        
        # Run tests
        if "test" in platforms:
            if not self.run_tests():
                print("\n[ABORT] Tests failed. Fix issues before publishing.")
                return
        
        # Build Python package
        if any(p in platforms for p in ["pypi", "all"]):
            if not self.build_python_package():
                print("\n[ABORT] Failed to build Python package.")
                return
            
            # Publish to PyPI
            if not self.publish_to_pypi(test=test_pypi):
                print("\n[WARNING] Failed to publish to PyPI")
        
        # VS Code Marketplace
        if any(p in platforms for p in ["vscode", "all"]):
            if self.build_vscode_extension():
                self.publish_to_vscode_marketplace()
            else:
                print("\n[WARNING] Skipping VS Code Marketplace")
        
        # npm registry
        if any(p in platforms for p in ["npm", "all"]):
            self.publish_to_npm()
        
        # GitHub release
        if any(p in platforms for p in ["github", "all"]):
            self.create_github_release()
        
        print(f"\n{'='*60}")
        print(f"Publishing complete!")
        print(f"{'='*60}")
        print(f"\nSynapse Language v{self.version} has been published to:")
        
        if "pypi" in platforms or "all" in platforms:
            print(f"  [OK] PyPI: pip install synapse-lang=={self.version}")
        if "vscode" in platforms or "all" in platforms:
            print(f"  [OK] VS Code: Search for 'Synapse Language' in Extensions")
        if "npm" in platforms or "all" in platforms:
            print(f"  [OK] npm: npm install @synapse-lang/core@{self.version}")
        if "github" in platforms or "all" in platforms:
            print(f"  [OK] GitHub: https://github.com/MichaelCrowe11/synapse-lang/releases/tag/v{self.version}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Publish Synapse Language to multiple platforms")
    parser.add_argument(
        "platforms",
        nargs="+",
        choices=["all", "pypi", "vscode", "npm", "github", "test"],
        help="Platforms to publish to (can specify multiple)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform a dry run without actually publishing"
    )
    parser.add_argument(
        "--test-pypi",
        action="store_true",
        help="Upload to TestPyPI instead of PyPI"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip running tests before publishing"
    )
    
    args = parser.parse_args()
    
    # Remove 'test' from platforms if skip-tests is set
    platforms = args.platforms
    if args.skip_tests and "test" in platforms:
        platforms.remove("test")
    elif not args.skip_tests and "test" not in platforms:
        platforms.insert(0, "test")
    
    publisher = SynapsePublisher(dry_run=args.dry_run, verbose=args.verbose)
    publisher.publish_all(platforms, test_pypi=args.test_pypi)


if __name__ == "__main__":
    main()