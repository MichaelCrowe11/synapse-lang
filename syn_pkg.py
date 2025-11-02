#!/usr/bin/env python3
"""
syn-pkg: Package manager for Synapse language
Similar to pip for Python or npm for JavaScript
"""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tarfile
import urllib.error
import urllib.request
import zipfile
from datetime import datetime
from pathlib import Path


class SynapsePackageManager:
    """Package manager for Synapse language"""

    def __init__(self):
        self.home_dir = Path.home() / ".synapse"
        self.packages_dir = self.home_dir / "packages"
        self.cache_dir = self.home_dir / "cache"
        self.bin_dir = self.home_dir / "bin"
        self.registry_url = "https://registry.synapse-lang.org"  # Future registry

        # Create directories if they don't exist
        self.home_dir.mkdir(exist_ok=True)
        self.packages_dir.mkdir(exist_ok=True)
        self.cache_dir.mkdir(exist_ok=True)
        self.bin_dir.mkdir(exist_ok=True)

        # Load package database
        self.db_file = self.home_dir / "packages.json"
        self.packages_db = self.load_database()

        # Load registry cache
        self.registry_cache_file = self.cache_dir / "registry.json"
        self.registry_cache = self.load_registry_cache()

    def load_database(self) -> dict:
        """Load installed packages database"""
        if self.db_file.exists():
            with open(self.db_file) as f:
                return json.load(f)
        return {
            "installed": {},
            "dependencies": {},
            "scripts": {}
        }

    def save_database(self):
        """Save packages database"""
        with open(self.db_file, "w") as f:
            json.dump(self.packages_db, f, indent=2)

    def load_registry_cache(self) -> dict:
        """Load cached registry data"""
        if self.registry_cache_file.exists():
            with open(self.registry_cache_file) as f:
                cache = json.load(f)
                # Check if cache is recent (less than 1 hour old)
                cache_time = datetime.fromisoformat(cache.get("timestamp", "2000-01-01"))
                if (datetime.now() - cache_time).seconds < 3600:
                    return cache
        return {"packages": {}, "timestamp": datetime.now().isoformat()}

    def save_registry_cache(self):
        """Save registry cache"""
        self.registry_cache["timestamp"] = datetime.now().isoformat()
        with open(self.registry_cache_file, "w") as f:
            json.dump(self.registry_cache, f, indent=2)

    def install(self, package_spec: str, version: str | None = None,
                dev: bool = False, force: bool = False):
        """Install a Synapse package"""
        print(f"📦 Installing {package_spec}...")

        # Parse package specification
        if "@" in package_spec and not version:
            package_name, version = package_spec.split("@")
        else:
            package_name = package_spec

        # Check if already installed
        if not force and package_name in self.packages_db["installed"]:
            current_version = self.packages_db["installed"][package_name]["version"]
            print(f"✓ {package_name} is already installed (version {current_version})")
            if not force:
                print("  Use --force to reinstall")
                return

        # Determine installation source
        if os.path.exists(package_spec):
            # Local installation
            self.install_local(package_spec, dev=dev)
        elif package_spec.startswith("git+"):
            # Git installation
            self.install_from_git(package_spec[4:], version=version, dev=dev)
        elif package_spec.startswith("http://") or package_spec.startswith("https://"):
            # URL installation
            self.install_from_url(package_spec, dev=dev)
        else:
            # Registry installation (or create example)
            self.install_from_registry(package_name, version=version, dev=dev)

    def install_local(self, path: str, dev: bool = False):
        """Install package from local directory"""
        path = Path(path).absolute()

        # Read package.syn.json
        package_json_path = path / "package.syn.json"
        if not package_json_path.exists():
            # Try to create one if it doesn't exist
            print(f"⚠️  No package.syn.json found in {path}")
            self.init_package(path)
            if not package_json_path.exists():
                print(f"❌ Failed to initialize package in {path}")
                return

        with open(package_json_path) as f:
            package_info = json.load(f)

        name = package_info["name"]
        version = package_info.get("version", "0.0.1")

        print(f"📝 Installing {name} v{version} from {path}")

        if dev:
            # Development install (symlink)
            dest = self.packages_dir / name
            if dest.exists():
                if dest.is_symlink():
                    dest.unlink()
                else:
                    shutil.rmtree(dest)
            dest.symlink_to(path)
            print(f"🔗 Created development link: {dest} -> {path}")
        else:
            # Regular install (copy)
            dest = self.packages_dir / name
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(path, dest)
            print(f"📁 Copied to: {dest}")

        # Update database
        self.packages_db["installed"][name] = {
            "version": version,
            "path": str(dest),
            "dev": dev,
            "dependencies": package_info.get("dependencies", {}),
            "description": package_info.get("description", ""),
            "installed_time": datetime.now().isoformat()
        }

        # Install scripts if any
        if "scripts" in package_info:
            self.install_scripts(name, package_info["scripts"], dest)

        self.save_database()
        print(f"✅ Successfully installed {name} v{version}")

        # Install dependencies
        for dep, dep_version in package_info.get("dependencies", {}).items():
            if dep not in self.packages_db["installed"]:
                print(f"📦 Installing dependency: {dep} {dep_version}")
                self.install(dep, dep_version)

    def install_from_git(self, git_url: str, version: str | None = None,
                        dev: bool = False):
        """Install package from git repository"""
        print(f"🌐 Cloning from {git_url}...")

        # Create temporary directory
        temp_dir = self.cache_dir / f"temp_{hashlib.md5(git_url.encode()).hexdigest()}"
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

        # Clone repository
        try:
            cmd = ["git", "clone", git_url, str(temp_dir)]
            if version:
                cmd.extend(["-b", version])

            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"❌ Failed to clone repository: {result.stderr}")
                return

            # Install from cloned directory
            self.install_local(str(temp_dir), dev=dev)

        finally:
            # Cleanup
            if temp_dir.exists():
                shutil.rmtree(temp_dir)

    def install_from_url(self, url: str, dev: bool = False):
        """Install package from URL (tarball or zip)"""
        print(f"⬇️  Downloading from {url}...")

        # Download file
        filename = url.split("/")[-1]
        download_path = self.cache_dir / filename

        try:
            urllib.request.urlretrieve(url, download_path)
        except urllib.error.URLError as e:
            print(f"❌ Failed to download: {e}")
            return

        # Extract archive
        extract_dir = self.cache_dir / f"extract_{hashlib.md5(url.encode()).hexdigest()}"
        if extract_dir.exists():
            shutil.rmtree(extract_dir)
        extract_dir.mkdir()

        try:
            if filename.endswith(".tar.gz") or filename.endswith(".tgz"):
                with tarfile.open(download_path, "r:gz") as tar:
                    tar.extractall(extract_dir)
            elif filename.endswith(".zip"):
                with zipfile.ZipFile(download_path, "r") as zip_ref:
                    zip_ref.extractall(extract_dir)
            else:
                print(f"❌ Unsupported archive format: {filename}")
                return

            # Find package directory (might be nested)
            package_dirs = list(extract_dir.glob("*/package.syn.json"))
            if package_dirs:
                package_dir = package_dirs[0].parent
                self.install_local(str(package_dir), dev=dev)
            else:
                print("❌ No package.syn.json found in archive")

        finally:
            # Cleanup
            if extract_dir.exists():
                shutil.rmtree(extract_dir)
            download_path.unlink()

    def install_from_registry(self, package_name: str, version: str | None = None,
                             dev: bool = False):
        """Install package from registry"""
        # For now, create an example package since registry doesn't exist yet
        print(f"📦 Package '{package_name}' not found in registry")
        print("📝 Creating example package for demonstration...")

        self.create_example_package(package_name)
        example_dir = Path(f"./{package_name}")
        if example_dir.exists():
            self.install_local(str(example_dir), dev=dev)

    def uninstall(self, package_name: str):
        """Uninstall a Synapse package"""
        if package_name not in self.packages_db["installed"]:
            print(f"❌ Package {package_name} is not installed")
            return

        print(f"🗑️  Uninstalling {package_name}...")

        # Remove package directory
        package_info = self.packages_db["installed"][package_name]
        package_path = Path(package_info["path"])
        if package_path.exists():
            if package_path.is_symlink():
                package_path.unlink()
            else:
                shutil.rmtree(package_path)

        # Remove installed scripts
        if package_name in self.packages_db.get("scripts", {}):
            for script_name in self.packages_db["scripts"][package_name]:
                script_path = self.bin_dir / script_name
                if script_path.exists():
                    script_path.unlink()

        # Update database
        del self.packages_db["installed"][package_name]
        if "scripts" in self.packages_db and package_name in self.packages_db["scripts"]:
            del self.packages_db["scripts"][package_name]

        self.save_database()
        print(f"✅ Successfully uninstalled {package_name}")

    def list_installed(self, verbose: bool = False):
        """List all installed packages"""
        if not self.packages_db["installed"]:
            print("📦 No packages installed")
            return

        print("📦 Installed packages:")
        print("=" * 60)

        for name, info in sorted(self.packages_db["installed"].items()):
            dev_marker = " [dev]" if info.get("dev") else ""
            print(f"  {name} v{info['version']}{dev_marker}")

            if verbose:
                print(f"    Path: {info['path']}")
                print(f"    Installed: {info.get('installed_time', 'Unknown')}")
                if info.get("description"):
                    print(f"    Description: {info['description']}")
                if info.get("dependencies"):
                    print("    Dependencies:")
                    for dep, version in info["dependencies"].items():
                        print(f"      - {dep} {version}")
                print()

    def search(self, query: str):
        """Search for packages"""
        print(f"🔍 Searching for '{query}'...")

        # Example packages for demonstration
        example_packages = {
            "synapse-stats": {
                "description": "Statistical computing library for Synapse",
                "version": "1.0.0",
                "author": "Synapse Community"
            },
            "synapse-ml": {
                "description": "Machine learning toolkit for Synapse",
                "version": "0.5.0",
                "author": "Synapse AI Team"
            },
            "synapse-plot": {
                "description": "Data visualization library for Synapse",
                "version": "2.1.0",
                "author": "Synapse Viz Team"
            },
            "synapse-bio": {
                "description": "Bioinformatics tools for Synapse",
                "version": "0.3.0",
                "author": "BioSynapse"
            },
            "synapse-physics": {
                "description": "Physics simulation library for Synapse",
                "version": "1.2.0",
                "author": "Quantum Synapse"
            },
            "synapse-quantum": {
                "description": "Quantum computing extensions for Synapse",
                "version": "0.1.0",
                "author": "Q-Synapse Team"
            }
        }

        # Filter results
        results = {}
        for name, info in example_packages.items():
            if query.lower() in name.lower() or query.lower() in info["description"].lower():
                results[name] = info

        if results:
            print(f"📋 Found {len(results)} packages:")
            print("=" * 60)
            for name, info in results.items():
                print(f"  📦 {name} v{info['version']}")
                print(f"     {info['description']}")
                print(f"     Author: {info['author']}")
                print()
        else:
            print("❌ No packages found")

    def create_example_package(self, name: str):
        """Create an example package structure"""
        print(f"🏗️  Creating example package structure for {name}...")

        package_dir = Path(f"./{name}")
        package_dir.mkdir(exist_ok=True)

        # Create package.syn.json
        package_json = {
            "name": name,
            "version": "0.1.0",
            "description": f"Example Synapse package: {name}",
            "main": "main.syn",
            "scripts": {
                f"{name}": "main.syn"
            },
            "dependencies": {},
            "devDependencies": {},
            "author": "Your Name",
            "license": "MIT",
            "repository": {
                "type": "git",
                "url": f"https://github.com/yourusername/{name}"
            },
            "keywords": ["synapse", "example", name]
        }

        with open(package_dir / "package.syn.json", "w") as f:
            json.dump(package_json, f, indent=2)

        # Create main.syn
        main_content = f"""
// {name} - Main module
// Example Synapse package

// Export main functionality
export function hello() {{
    print("Hello from {name}!")
    return "Success"
}}

// Version information
export function version() {{
    return "0.1.0"
}}

// Example scientific function
export function calculate(data) {{
    uncertain mean = calculate_mean(data)
    uncertain std = calculate_std(data)

    return {{
        "mean": mean,
        "std": std
    }}
}}

function calculate_mean(data) {{
    sum = 0
    for value in data {{
        sum = sum + value
    }}
    return sum / len(data)
}}

function calculate_std(data) {{
    mean = calculate_mean(data)
    sum_sq = 0

    for value in data {{
        diff = value - mean
        sum_sq = sum_sq + diff * diff
    }}

    return sqrt(sum_sq / len(data))
}}
"""

        with open(package_dir / "main.syn", "w") as f:
            f.write(main_content)

        # Create README.md
        readme_content = f"""
# {name}

Example Synapse package demonstrating package structure and features.

## Installation

```bash
syn-pkg install ./{name}
```

## Usage

```synapse
import {name}

// Basic usage
{name}.hello()

// Get version
version = {name}.version()

// Scientific calculations
data = [1, 2, 3, 4, 5]
results = {name}.calculate(data)
print("Mean:", results.mean)
print("Std:", results.std)
```

## API Reference

### `hello()`
Prints a greeting message.

### `version()`
Returns the package version.

### `calculate(data)`
Performs statistical calculations on data.
- **Parameters**: `data` - Array of numeric values
- **Returns**: Object with `mean` and `std` properties

## License

MIT
"""

        with open(package_dir / "README.md", "w") as f:
            f.write(readme_content)

        # Create test file
        test_content = f"""
// Tests for {name}

import {name}

test "hello function works" {{
    result = {name}.hello()
    assert result == "Success"
}}

test "version returns correct version" {{
    version = {name}.version()
    assert version == "0.1.0"
}}

test "calculate function works" {{
    data = [1, 2, 3, 4, 5]
    results = {name}.calculate(data)

    assert results.mean == 3.0
    assert results.std > 1.0
}}
"""

        test_dir = package_dir / "tests"
        test_dir.mkdir(exist_ok=True)
        with open(test_dir / "test_main.syn", "w") as f:
            f.write(test_content)

        print(f"✅ Created example package in ./{name}/")

    def init_package(self, path: Path | None = None):
        """Initialize a new Synapse package in the current or specified directory"""
        if path is None:
            path = Path.cwd()
        else:
            path = Path(path)

        project_name = path.name

        print(f"🚀 Initializing Synapse package: {project_name}")

        # Create package.syn.json
        package_json = {
            "name": project_name,
            "version": "0.1.0",
            "description": "",
            "main": "main.syn",
            "scripts": {
                "start": "synapse main.syn",
                "test": "synapse test/*.syn"
            },
            "dependencies": {},
            "devDependencies": {},
            "author": "",
            "license": "MIT"
        }

        package_json_path = path / "package.syn.json"
        if package_json_path.exists():
            print("⚠️  package.syn.json already exists")
        else:
            with open(package_json_path, "w") as f:
                json.dump(package_json, f, indent=2)
            print("✅ Created package.syn.json")

        # Create main.syn if it doesn't exist
        main_path = path / "main.syn"
        if not main_path.exists():
            with open(main_path, "w") as f:
                f.write(f"// {project_name} - Main entry point\n\n")
            print("✅ Created main.syn")

        # Create .gitignore
        gitignore_path = path / ".gitignore"
        if not gitignore_path.exists():
            with open(gitignore_path, "w") as f:
                f.write("node_modules/\n*.pyc\n__pycache__/\n.synapse_cache/\n*.log\n")
            print("✅ Created .gitignore")

        print(f"🎉 Synapse package initialized: {project_name}")

    def run_script(self, script_name: str):
        """Run a package script"""
        # Find package with this script
        for package_name, scripts in self.packages_db.get("scripts", {}).items():
            if script_name in scripts:
                script_path = scripts[script_name]
                print(f"🚀 Running {script_name} from {package_name}...")
                os.system(f"synapse {script_path}")
                return

        print(f"❌ Script '{script_name}' not found")

    def install_scripts(self, package_name: str, scripts: dict[str, str],
                       package_path: Path):
        """Install package scripts"""
        if "scripts" not in self.packages_db:
            self.packages_db["scripts"] = {}

        self.packages_db["scripts"][package_name] = {}

        for script_name, script_cmd in scripts.items():
            # Create wrapper script
            script_content = f"""#!/usr/bin/env python3
import os
import sys
os.system("synapse {package_path}/{script_cmd}")
"""
            script_path = self.bin_dir / script_name
            with open(script_path, "w") as f:
                f.write(script_content)

            # Make executable
            script_path.chmod(0o755)
            self.packages_db["scripts"][package_name][script_name] = str(script_path)
            print(f"  📜 Installed script: {script_name}")

    def update(self, package_name: str | None = None):
        """Update packages"""
        if package_name:
            # Update specific package
            if package_name not in self.packages_db["installed"]:
                print(f"❌ Package {package_name} is not installed")
                return

            print(f"🔄 Updating {package_name}...")
            self.packages_db["installed"][package_name]
            self.install(package_name, force=True)
        else:
            # Update all packages
            print("🔄 Updating all packages...")
            for package_name in list(self.packages_db["installed"].keys()):
                self.update(package_name)


def main():
    parser = argparse.ArgumentParser(
        description="Synapse Package Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  syn-pkg install synapse-stats        # Install from registry
  syn-pkg install ./my-package         # Install from local directory
  syn-pkg install git+https://...      # Install from git
  syn-pkg install package@1.2.3        # Install specific version
  syn-pkg search quantum                # Search for packages
  syn-pkg list                          # List installed packages
  syn-pkg uninstall package-name       # Uninstall package
  syn-pkg init                          # Initialize new package
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Install command
    install_parser = subparsers.add_parser("install", help="Install a package")
    install_parser.add_argument("package", help="Package name, path, or URL")
    install_parser.add_argument("--version", help="Package version")
    install_parser.add_argument("--dev", action="store_true",
                               help="Development installation (symlink)")
    install_parser.add_argument("--force", action="store_true",
                               help="Force reinstall")

    # Uninstall command
    uninstall_parser = subparsers.add_parser("uninstall", help="Uninstall a package")
    uninstall_parser.add_argument("package", help="Package name")

    # List command
    list_parser = subparsers.add_parser("list", help="List installed packages")
    list_parser.add_argument("-v", "--verbose", action="store_true",
                            help="Show detailed information")

    # Search command
    search_parser = subparsers.add_parser("search", help="Search for packages")
    search_parser.add_argument("query", help="Search query")

    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize a new package")
    init_parser.add_argument("--path", help="Path to initialize (default: current)")

    # Update command
    update_parser = subparsers.add_parser("update", help="Update packages")
    update_parser.add_argument("package", nargs="?", help="Package to update (all if omitted)")

    # Run command
    run_parser = subparsers.add_parser("run", help="Run a package script")
    run_parser.add_argument("script", help="Script name")

    args = parser.parse_args()

    # Create package manager instance
    pm = SynapsePackageManager()

    # Execute command
    if args.command == "install":
        pm.install(args.package, version=args.version, dev=args.dev,
                  force=args.force)
    elif args.command == "uninstall":
        pm.uninstall(args.package)
    elif args.command == "list":
        pm.list_installed(verbose=args.verbose)
    elif args.command == "search":
        pm.search(args.query)
    elif args.command == "init":
        pm.init_package(Path(args.path) if args.path else None)
    elif args.command == "update":
        pm.update(args.package)
    elif args.command == "run":
        pm.run_script(args.script)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
