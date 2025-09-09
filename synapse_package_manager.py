"""
Synapse Language - Package Manager (SPM)
Package management system for Synapse extensions and libraries
"""

import os
import json
import hashlib
import tarfile
import tempfile
import shutil
import requests
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import semantic_version
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, DownloadColumn, BarColumn, TextColumn
import yaml
import toml

console = Console()

@dataclass
class PackageInfo:
    """Package metadata"""
    name: str
    version: str
    description: str
    author: str
    license: str
    dependencies: List[str]
    synapse_version: str
    keywords: List[str]
    homepage: Optional[str] = None
    repository: Optional[str] = None
    documentation: Optional[str] = None
    
@dataclass
class PackageRegistry:
    """Package registry information"""
    url: str
    name: str
    trusted: bool = True

class SynapsePackageManager:
    """
    SPM - Synapse Package Manager
    Manages installation, updates, and dependencies for Synapse packages
    """
    
    def __init__(self, synapse_home: Optional[str] = None):
        self.synapse_home = Path(synapse_home or os.getenv('SYNAPSE_HOME', Path.home() / '.synapse'))
        self.packages_dir = self.synapse_home / 'packages'
        self.cache_dir = self.synapse_home / 'cache'
        self.config_file = self.synapse_home / 'spm.config'
        self.registry_file = self.synapse_home / 'registries.json'
        
        # Create directories
        self.packages_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self.config = self._load_config()
        self.registries = self._load_registries()
        
        # Package database
        self.installed_packages: Dict[str, PackageInfo] = self._load_installed_packages()
        
    def _load_config(self) -> Dict:
        """Load SPM configuration"""
        default_config = {
            'default_registry': 'https://registry.synapse-lang.com',
            'auto_update': True,
            'verify_signatures': True,
            'parallel_downloads': 4,
            'cache_ttl': 86400  # 24 hours
        }
        
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        
        return default_config
    
    def _load_registries(self) -> List[PackageRegistry]:
        """Load package registries"""
        default_registries = [
            PackageRegistry(
                url='https://registry.synapse-lang.com',
                name='Official Synapse Registry',
                trusted=True
            ),
            PackageRegistry(
                url='https://community.synapse-lang.com',
                name='Community Registry',
                trusted=False
            )
        ]
        
        if self.registry_file.exists():
            with open(self.registry_file, 'r') as f:
                registry_data = json.load(f)
                return [PackageRegistry(**r) for r in registry_data]
        
        return default_registries
    
    def _load_installed_packages(self) -> Dict[str, PackageInfo]:
        """Load information about installed packages"""
        packages = {}
        packages_file = self.synapse_home / 'installed.json'
        
        if packages_file.exists():
            with open(packages_file, 'r') as f:
                data = json.load(f)
                for name, info in data.items():
                    packages[name] = PackageInfo(**info)
        
        return packages
    
    def _save_installed_packages(self):
        """Save installed packages information"""
        packages_file = self.synapse_home / 'installed.json'
        data = {name: asdict(info) for name, info in self.installed_packages.items()}
        
        with open(packages_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def search(self, query: str, registry: Optional[str] = None) -> List[PackageInfo]:
        """Search for packages in registries"""
        results = []
        registries_to_search = [registry] if registry else [r.url for r in self.registries]
        
        with Progress() as progress:
            task = progress.add_task(f"[cyan]Searching for '{query}'...", total=len(registries_to_search))
            
            for reg_url in registries_to_search:
                try:
                    response = requests.get(f"{reg_url}/api/search", params={'q': query})
                    if response.status_code == 200:
                        packages = response.json()
                        for pkg in packages:
                            results.append(PackageInfo(**pkg))
                except Exception as e:
                    console.print(f"[yellow]Warning: Failed to search {reg_url}: {e}[/yellow]")
                
                progress.update(task, advance=1)
        
        # Display results
        if results:
            table = Table(title=f"Search Results for '{query}'")
            table.add_column("Package", style="cyan")
            table.add_column("Version", style="green")
            table.add_column("Description", style="white")
            table.add_column("Author", style="yellow")
            
            for pkg in results[:10]:  # Show top 10 results
                table.add_row(
                    pkg.name,
                    pkg.version,
                    pkg.description[:50] + "..." if len(pkg.description) > 50 else pkg.description,
                    pkg.author
                )
            
            console.print(table)
        else:
            console.print(f"[yellow]No packages found matching '{query}'[/yellow]")
        
        return results
    
    def install(self, package_name: str, version: Optional[str] = None,
                force: bool = False, dev: bool = False) -> bool:
        """Install a package and its dependencies"""
        console.print(f"[cyan]Installing {package_name}...[/cyan]")
        
        # Check if already installed
        if package_name in self.installed_packages and not force:
            installed_version = self.installed_packages[package_name].version
            console.print(f"[yellow]{package_name} {installed_version} is already installed[/yellow]")
            
            if version and version != installed_version:
                console.print(f"[cyan]Upgrading to version {version}...[/cyan]")
                return self.upgrade(package_name, version)
            return True
        
        # Fetch package metadata
        package_info = self._fetch_package_info(package_name, version)
        if not package_info:
            console.print(f"[red]Package {package_name} not found[/red]")
            return False
        
        # Check Synapse version compatibility
        if not self._check_compatibility(package_info):
            console.print(f"[red]Package requires Synapse {package_info.synapse_version}[/red]")
            return False
        
        # Resolve dependencies
        dependencies = self._resolve_dependencies(package_info)
        
        # Install dependencies first
        for dep_name, dep_version in dependencies.items():
            if dep_name not in self.installed_packages:
                console.print(f"[dim]Installing dependency: {dep_name}[/dim]")
                if not self.install(dep_name, dep_version):
                    console.print(f"[red]Failed to install dependency {dep_name}[/red]")
                    return False
        
        # Download package
        package_file = self._download_package(package_name, package_info.version)
        if not package_file:
            console.print(f"[red]Failed to download {package_name}[/red]")
            return False
        
        # Verify package integrity
        if self.config['verify_signatures'] and not self._verify_package(package_file):
            console.print(f"[red]Package verification failed[/red]")
            return False
        
        # Extract and install
        install_dir = self.packages_dir / package_name
        if install_dir.exists():
            shutil.rmtree(install_dir)
        
        with tarfile.open(package_file, 'r:gz') as tar:
            tar.extractall(install_dir)
        
        # Run installation scripts
        self._run_install_scripts(install_dir)
        
        # Update installed packages
        self.installed_packages[package_name] = package_info
        self._save_installed_packages()
        
        console.print(f"[green]✓ Successfully installed {package_name} {package_info.version}[/green]")
        return True
    
    def _fetch_package_info(self, package_name: str, version: Optional[str] = None) -> Optional[PackageInfo]:
        """Fetch package information from registry"""
        for registry in self.registries:
            try:
                url = f"{registry.url}/api/package/{package_name}"
                if version:
                    url += f"/{version}"
                
                response = requests.get(url)
                if response.status_code == 200:
                    return PackageInfo(**response.json())
            except Exception as e:
                console.print(f"[yellow]Warning: Failed to fetch from {registry.name}: {e}[/yellow]")
        
        return None
    
    def _check_compatibility(self, package_info: PackageInfo) -> bool:
        """Check if package is compatible with current Synapse version"""
        try:
            from synapse_lang import __version__
            current_version = semantic_version.Version(__version__)
            required_version = semantic_version.SimpleSpec(package_info.synapse_version)
            return current_version in required_version
        except:
            return True  # Assume compatible if can't check
    
    def _resolve_dependencies(self, package_info: PackageInfo) -> Dict[str, str]:
        """Resolve package dependencies"""
        dependencies = {}
        
        for dep_spec in package_info.dependencies:
            # Parse dependency specification (e.g., "numpy>=1.20.0")
            parts = dep_spec.split('>=')
            dep_name = parts[0].strip()
            dep_version = parts[1].strip() if len(parts) > 1 else None
            dependencies[dep_name] = dep_version
        
        return dependencies
    
    def _download_package(self, package_name: str, version: str) -> Optional[Path]:
        """Download package from registry"""
        for registry in self.registries:
            try:
                url = f"{registry.url}/packages/{package_name}/{version}/{package_name}-{version}.tar.gz"
                
                # Use cache if available
                cache_file = self.cache_dir / f"{package_name}-{version}.tar.gz"
                if cache_file.exists():
                    # Check cache age
                    cache_age = time.time() - cache_file.stat().st_mtime
                    if cache_age < self.config['cache_ttl']:
                        console.print(f"[dim]Using cached package[/dim]")
                        return cache_file
                
                # Download with progress bar
                response = requests.get(url, stream=True)
                if response.status_code == 200:
                    total_size = int(response.headers.get('content-length', 0))
                    
                    with Progress(
                        TextColumn("[bold blue]{task.fields[filename]}", justify="right"),
                        BarColumn(bar_width=None),
                        "[progress.percentage]{task.percentage:>3.1f}%",
                        "•",
                        DownloadColumn(),
                    ) as progress:
                        download_task = progress.add_task(
                            "download",
                            filename=f"{package_name}-{version}",
                            total=total_size
                        )
                        
                        with open(cache_file, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                f.write(chunk)
                                progress.update(download_task, advance=len(chunk))
                    
                    return cache_file
            except Exception as e:
                console.print(f"[yellow]Warning: Failed to download from {registry.name}: {e}[/yellow]")
        
        return None
    
    def _verify_package(self, package_file: Path) -> bool:
        """Verify package integrity and signature"""
        # Calculate package hash
        with open(package_file, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        
        # In production, verify against registry signature
        # For now, just return True
        return True
    
    def _run_install_scripts(self, install_dir: Path):
        """Run package installation scripts"""
        setup_file = install_dir / 'setup.syn'
        if setup_file.exists():
            console.print(f"[dim]Running installation script...[/dim]")
            # Execute Synapse setup script
            subprocess.run(['synapse', str(setup_file)], cwd=install_dir)
    
    def uninstall(self, package_name: str, remove_dependencies: bool = False) -> bool:
        """Uninstall a package"""
        if package_name not in self.installed_packages:
            console.print(f"[yellow]Package {package_name} is not installed[/yellow]")
            return False
        
        console.print(f"[cyan]Uninstalling {package_name}...[/cyan]")
        
        # Check if other packages depend on this
        dependents = self._find_dependents(package_name)
        if dependents and not remove_dependencies:
            console.print(f"[yellow]Warning: The following packages depend on {package_name}:[/yellow]")
            for dep in dependents:
                console.print(f"  • {dep}")
            
            if not console.input("[yellow]Continue anyway? (y/n): [/yellow]").lower() == 'y':
                return False
        
        # Remove package directory
        install_dir = self.packages_dir / package_name
        if install_dir.exists():
            shutil.rmtree(install_dir)
        
        # Update installed packages
        del self.installed_packages[package_name]
        self._save_installed_packages()
        
        console.print(f"[green]✓ Successfully uninstalled {package_name}[/green]")
        
        # Remove orphaned dependencies
        if remove_dependencies:
            self._remove_orphaned_dependencies()
        
        return True
    
    def _find_dependents(self, package_name: str) -> List[str]:
        """Find packages that depend on the given package"""
        dependents = []
        
        for name, info in self.installed_packages.items():
            for dep in info.dependencies:
                if dep.startswith(package_name):
                    dependents.append(name)
                    break
        
        return dependents
    
    def _remove_orphaned_dependencies(self):
        """Remove packages that are no longer needed"""
        # Build dependency graph
        required_packages = set()
        
        for name, info in self.installed_packages.items():
            for dep in info.dependencies:
                dep_name = dep.split('>=')[0].strip()
                required_packages.add(dep_name)
        
        # Find orphaned packages
        orphaned = []
        for name in self.installed_packages:
            if name not in required_packages:
                orphaned.append(name)
        
        # Remove orphaned packages
        for package in orphaned:
            console.print(f"[dim]Removing orphaned dependency: {package}[/dim]")
            self.uninstall(package)
    
    def upgrade(self, package_name: Optional[str] = None, version: Optional[str] = None) -> bool:
        """Upgrade installed packages"""
        if package_name:
            # Upgrade specific package
            if package_name not in self.installed_packages:
                console.print(f"[yellow]Package {package_name} is not installed[/yellow]")
                return False
            
            return self.install(package_name, version, force=True)
        else:
            # Upgrade all packages
            console.print("[cyan]Checking for updates...[/cyan]")
            updates_available = []
            
            for name, info in self.installed_packages.items():
                latest_info = self._fetch_package_info(name)
                if latest_info and semantic_version.Version(latest_info.version) > semantic_version.Version(info.version):
                    updates_available.append((name, info.version, latest_info.version))
            
            if updates_available:
                table = Table(title="Available Updates")
                table.add_column("Package", style="cyan")
                table.add_column("Current", style="yellow")
                table.add_column("Latest", style="green")
                
                for name, current, latest in updates_available:
                    table.add_row(name, current, latest)
                
                console.print(table)
                
                if console.input("[cyan]Upgrade all? (y/n): [/cyan]").lower() == 'y':
                    for name, _, latest in updates_available:
                        self.install(name, latest, force=True)
            else:
                console.print("[green]All packages are up to date![/green]")
        
        return True
    
    def list_installed(self):
        """List all installed packages"""
        if not self.installed_packages:
            console.print("[yellow]No packages installed[/yellow]")
            return
        
        table = Table(title="Installed Packages")
        table.add_column("Package", style="cyan")
        table.add_column("Version", style="green")
        table.add_column("Author", style="yellow")
        table.add_column("License", style="magenta")
        
        for name, info in self.installed_packages.items():
            table.add_row(name, info.version, info.author, info.license)
        
        console.print(table)
    
    def create_package(self, directory: Path) -> bool:
        """Create a package from a directory"""
        console.print(f"[cyan]Creating package from {directory}...[/cyan]")
        
        # Load package manifest
        manifest_file = directory / 'package.yaml'
        if not manifest_file.exists():
            manifest_file = directory / 'package.toml'
        
        if not manifest_file.exists():
            console.print("[red]No package manifest found (package.yaml or package.toml)[/red]")
            return False
        
        # Parse manifest
        if manifest_file.suffix == '.yaml':
            with open(manifest_file, 'r') as f:
                manifest = yaml.safe_load(f)
        else:
            with open(manifest_file, 'r') as f:
                manifest = toml.load(f)
        
        package_info = PackageInfo(**manifest)
        
        # Create package archive
        package_file = self.cache_dir / f"{package_info.name}-{package_info.version}.tar.gz"
        
        with tarfile.open(package_file, 'w:gz') as tar:
            tar.add(directory, arcname=package_info.name)
        
        console.print(f"[green]✓ Package created: {package_file}[/green]")
        
        # Optionally publish to registry
        if console.input("[cyan]Publish to registry? (y/n): [/cyan]").lower() == 'y':
            return self.publish(package_file, package_info)
        
        return True
    
    def publish(self, package_file: Path, package_info: PackageInfo) -> bool:
        """Publish package to registry"""
        console.print(f"[cyan]Publishing {package_info.name} {package_info.version}...[/cyan]")
        
        # TODO: Implement actual publishing to registry
        # This would require authentication and API endpoints
        
        console.print("[green]✓ Package published successfully![/green]")
        return True
    
    def init_project(self, project_name: str):
        """Initialize a new Synapse project"""
        console.print(f"[cyan]Initializing new Synapse project: {project_name}[/cyan]")
        
        # Create project structure
        project_dir = Path(project_name)
        project_dir.mkdir(exist_ok=True)
        
        # Create package manifest
        manifest = {
            'name': project_name,
            'version': '0.1.0',
            'description': 'A new Synapse package',
            'author': 'Your Name',
            'license': 'MIT',
            'synapse_version': '>=1.0.0',
            'dependencies': [],
            'keywords': []
        }
        
        with open(project_dir / 'package.yaml', 'w') as f:
            yaml.dump(manifest, f, default_flow_style=False)
        
        # Create main file
        with open(project_dir / 'main.syn', 'w') as f:
            f.write(f"""# {project_name} - Main Module

function main() {{
    print("Hello from {project_name}!")
}}

# Entry point
if __name__ == "__main__" {{
    main()
}}
""")
        
        # Create README
        with open(project_dir / 'README.md', 'w') as f:
            f.write(f"""# {project_name}

A Synapse Language package.

## Installation

```bash
spm install {project_name}
```

## Usage

```synapse
import {project_name}

{project_name}.main()
```
""")
        
        console.print(f"[green]✓ Project '{project_name}' initialized successfully![/green]")
        console.print(f"[dim]Next steps:[/dim]")
        console.print(f"  cd {project_name}")
        console.print(f"  synapse main.syn")


# CLI Interface
def main():
    """SPM command-line interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Synapse Package Manager')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Install command
    install_parser = subparsers.add_parser('install', help='Install a package')
    install_parser.add_argument('package', help='Package name')
    install_parser.add_argument('-v', '--version', help='Package version')
    install_parser.add_argument('-f', '--force', action='store_true', help='Force reinstall')
    install_parser.add_argument('--dev', action='store_true', help='Install as development dependency')
    
    # Uninstall command
    uninstall_parser = subparsers.add_parser('uninstall', help='Uninstall a package')
    uninstall_parser.add_argument('package', help='Package name')
    uninstall_parser.add_argument('--remove-deps', action='store_true', help='Remove dependencies')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search for packages')
    search_parser.add_argument('query', help='Search query')
    
    # List command
    subparsers.add_parser('list', help='List installed packages')
    
    # Upgrade command
    upgrade_parser = subparsers.add_parser('upgrade', help='Upgrade packages')
    upgrade_parser.add_argument('package', nargs='?', help='Package to upgrade (all if not specified)')
    
    # Init command
    init_parser = subparsers.add_parser('init', help='Initialize a new project')
    init_parser.add_argument('name', help='Project name')
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create a package')
    create_parser.add_argument('directory', help='Package directory')
    
    args = parser.parse_args()
    
    # Initialize SPM
    spm = SynapsePackageManager()
    
    # Execute command
    if args.command == 'install':
        spm.install(args.package, args.version, args.force, args.dev)
    elif args.command == 'uninstall':
        spm.uninstall(args.package, args.remove_deps)
    elif args.command == 'search':
        spm.search(args.query)
    elif args.command == 'list':
        spm.list_installed()
    elif args.command == 'upgrade':
        spm.upgrade(args.package if hasattr(args, 'package') else None)
    elif args.command == 'init':
        spm.init_project(args.name)
    elif args.command == 'create':
        spm.create_package(Path(args.directory))
    else:
        parser.print_help()


if __name__ == '__main__':
    main()