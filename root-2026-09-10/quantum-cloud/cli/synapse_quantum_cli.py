"""
Synapse Quantum CLI (synapse-cli)
AWS CLI equivalent for quantum computing

# Configure quantum credentials
synapse configure

# List quantum instances
synapse sq compute describe-instances

# Submit quantum job
synapse sq compute run-job --circuit bell_state.qasm --shots 1000

# Monitor quantum jobs
synapse sq compute describe-jobs --status running

# Get job results
synapse sq compute get-job-result --job-id sq-job-abc123
"""

import asyncio
import json
import os
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any

import click
import yaml

# Import our quantum services
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from synapse_quantum_services.core.compute_service import (
    QuantumBackendProvider,
    QuantumInstanceType,
    QuantumJobStatus,
    SynapseQuantumCompute,
)


class SynapseQuantumConfig:
    """Configuration management for Synapse Quantum CLI"""

    def __init__(self):
        self.config_dir = Path.home() / ".synapse"
        self.config_file = self.config_dir / "config"
        self.credentials_file = self.config_dir / "credentials"

    def load_config(self) -> dict[str, Any]:
        """Load CLI configuration"""
        if not self.config_file.exists():
            return self._get_default_config()

        try:
            with open(self.config_file) as f:
                return json.load(f)
        except Exception:
            return self._get_default_config()

    def save_config(self, config: dict[str, Any]):
        """Save CLI configuration"""
        self.config_dir.mkdir(exist_ok=True)
        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=2)

    def load_credentials(self) -> dict[str, Any]:
        """Load quantum credentials"""
        if not self.credentials_file.exists():
            return {}

        try:
            with open(self.credentials_file) as f:
                return json.load(f)
        except Exception:
            return {}

    def save_credentials(self, credentials: dict[str, Any]):
        """Save quantum credentials"""
        self.config_dir.mkdir(exist_ok=True)
        with open(self.credentials_file, "w") as f:
            json.dump(credentials, f, indent=2)
        # Secure the credentials file
        os.chmod(self.credentials_file, 0o600)

    def _get_default_config(self) -> dict[str, Any]:
        return {
            "region": "us-quantum-1",
            "output": "json",
            "quantum_backend_preference": ["auto"],
            "default_instance_type": "sq.small.8q",
            "max_cost_per_job": 100.00
        }

# Global configuration instance
config_manager = SynapseQuantumConfig()

@click.group()
@click.option("--region", help="Quantum region to use")
@click.option("--output", type=click.Choice(["json", "yaml", "table"]), help="Output format")
@click.pass_context
def cli(ctx, region, output):
    """Synapse Quantum CLI - AWS CLI for quantum computing"""
    ctx.ensure_object(dict)

    # Load configuration
    config = config_manager.load_config()
    credentials = config_manager.load_credentials()

    # Override with command line options
    if region:
        config["region"] = region
    if output:
        config["output"] = output

    ctx.obj["config"] = config
    ctx.obj["credentials"] = credentials

@cli.command()
def configure():
    """Configure Synapse Quantum CLI credentials and settings"""
    click.echo("Synapse Quantum CLI Configuration")
    click.echo("=" * 35)

    # Get current config
    config = config_manager.load_config()
    credentials = config_manager.load_credentials()

    # Quantum access credentials
    access_key = click.prompt(
        "Synapse Quantum Access Key ID",
        default=credentials.get("quantum_access_key_id", ""),
        show_default=bool(credentials.get("quantum_access_key_id"))
    )

    secret_key = click.prompt(
        "Synapse Quantum Secret Access Key",
        default=credentials.get("quantum_secret_access_key", ""),
        hide_input=True,
        show_default=bool(credentials.get("quantum_secret_access_key"))
    )

    # Configuration settings
    region = click.prompt(
        "Default quantum region",
        default=config.get("region", "us-quantum-1")
    )

    output_format = click.prompt(
        "Default output format",
        type=click.Choice(["json", "yaml", "table"]),
        default=config.get("output", "json")
    )

    backend_preference = click.prompt(
        "Default quantum backend preference (comma-separated)",
        default=",".join(config.get("quantum_backend_preference", ["auto"]))
    )

    instance_type = click.prompt(
        "Default quantum instance type",
        type=click.Choice([t.value for t in QuantumInstanceType]),
        default=config.get("default_instance_type", "sq.small.8q")
    )

    max_cost = click.prompt(
        "Maximum cost per job ($)",
        type=float,
        default=config.get("max_cost_per_job", 100.00)
    )

    # Save credentials
    credentials.update({
        "quantum_access_key_id": access_key,
        "quantum_secret_access_key": secret_key
    })
    config_manager.save_credentials(credentials)

    # Save configuration
    config.update({
        "region": region,
        "output": output_format,
        "quantum_backend_preference": backend_preference.split(","),
        "default_instance_type": instance_type,
        "max_cost_per_job": max_cost
    })
    config_manager.save_config(config)

    click.echo("\nConfiguration saved successfully!")
    click.echo(f"Configuration file: {config_manager.config_file}")
    click.echo(f"Credentials file: {config_manager.credentials_file}")

# Quantum Compute service commands
@cli.group(name="sq")
def quantum_services():
    """Synapse Quantum services"""
    pass

@quantum_services.group(name="compute")
def compute():
    """Quantum compute service (SQ-Compute)"""
    pass

@compute.command("describe-instances")
@click.option("--instance-types", help="Filter by instance types (comma-separated)")
@click.option("--output", type=click.Choice(["json", "yaml", "table"]), help="Output format")
@click.pass_context
def describe_instances(ctx, instance_types, output):
    """List available quantum instance types (like AWS EC2 describe-instances)"""

    async def _describe_instances():
        sq_compute = SynapseQuantumCompute()
        instances = await sq_compute.describe_quantum_instances()

        # Filter by instance types if specified
        if instance_types:
            filter_types = [t.strip() for t in instance_types.split(",")]
            instances = [i for i in instances if i["InstanceType"] in filter_types]

        return instances

    instances = asyncio.run(_describe_instances())

    output_format = output or ctx.obj["config"]["output"]
    _display_output(instances, output_format)

@compute.command("describe-backends")
@click.option("--providers", help="Filter by providers (comma-separated)")
@click.option("--output", type=click.Choice(["json", "yaml", "table"]), help="Output format")
@click.pass_context
def describe_backends(ctx, providers, output):
    """List available quantum backends (like AWS EC2 describe-regions)"""

    async def _describe_backends():
        sq_compute = SynapseQuantumCompute()
        backends = await sq_compute.describe_quantum_backends()

        # Filter by providers if specified
        if providers:
            filter_providers = [p.strip() for p in providers.split(",")]
            backends = [b for b in backends if b["Provider"] in filter_providers]

        return backends

    backends = asyncio.run(_describe_backends())

    output_format = output or ctx.obj["config"]["output"]
    _display_output(backends, output_format)

@compute.command("run-job")
@click.option("--circuit", required=True, help="Quantum circuit file or code")
@click.option("--language", default="synapse", help="Circuit language (synapse, qiskit, cirq, qasm)")
@click.option("--instance-type", help="Quantum instance type")
@click.option("--shots", default=1000, help="Number of shots")
@click.option("--backend-preference", help="Backend preference (comma-separated)")
@click.option("--optimization-level", default=1, help="Circuit optimization level (0-3)")
@click.option("--cost-limit", type=float, help="Maximum cost limit")
@click.option("--tags", help="Job tags (key=value,key=value)")
@click.option("--output", type=click.Choice(["json", "yaml", "table"]), help="Output format")
@click.pass_context
def run_job(ctx, circuit, language, instance_type, shots, backend_preference,
           optimization_level, cost_limit, tags, output):
    """Submit a quantum job for execution (like AWS Batch submit-job)"""

    config = ctx.obj["config"]

    # Read circuit code
    if os.path.isfile(circuit):
        with open(circuit) as f:
            circuit_code = f.read()
    else:
        circuit_code = circuit

    # Parse parameters
    instance_type = instance_type or config["default_instance_type"]
    backend_prefs = backend_preference.split(",") if backend_preference else config["quantum_backend_preference"]
    cost_limit = cost_limit or config["max_cost_per_job"]

    # Parse tags
    job_tags = {}
    if tags:
        for tag in tags.split(","):
            if "=" in tag:
                key, value = tag.split("=", 1)
                job_tags[key.strip()] = value.strip()

    # Convert backend preferences to enum
    backend_enums = []
    for pref in backend_prefs:
        try:
            backend_enums.append(QuantumBackendProvider(pref.strip()))
        except ValueError:
            click.echo(f"Warning: Unknown backend '{pref}', using auto")
            backend_enums.append(QuantumBackendProvider.AUTO)

    async def _run_job():
        sq_compute = SynapseQuantumCompute()

        job = await sq_compute.run_quantum_job(
            circuit_code=circuit_code,
            language=language,
            instance_type=QuantumInstanceType(instance_type),
            shots=shots,
            backend_preference=backend_enums,
            optimization_level=optimization_level,
            tags=job_tags,
            cost_limit=Decimal(str(cost_limit)) if cost_limit else None
        )

        return {
            "JobId": job.job_id,
            "Status": job.status.value,
            "InstanceType": job.instance_type.value,
            "Shots": job.shots,
            "EstimatedCost": float(job.estimated_cost) if job.estimated_cost else None,
            "CreatedAt": job.created_at.isoformat(),
            "Tags": job.tags
        }

    try:
        result = asyncio.run(_run_job())
        output_format = output or config["output"]
        _display_output(result, output_format)

        if output_format == "table":
            click.echo(f"\nJob submitted successfully: {result['JobId']}")
            click.echo(f"Monitor with: synapse sq compute describe-jobs --job-ids {result['JobId']}")

    except Exception as e:
        click.echo(f"Error submitting job: {e}", err=True)
        sys.exit(1)

@compute.command("describe-jobs")
@click.option("--job-ids", help="Job IDs to describe (comma-separated)")
@click.option("--status", type=click.Choice([s.value for s in QuantumJobStatus]), help="Filter by job status")
@click.option("--max-results", default=50, help="Maximum number of results")
@click.option("--output", type=click.Choice(["json", "yaml", "table"]), help="Output format")
@click.pass_context
def describe_jobs(ctx, job_ids, status, max_results, output):
    """Describe quantum jobs (like AWS Batch describe-jobs)"""

    async def _describe_jobs():
        sq_compute = SynapseQuantumCompute()

        if job_ids:
            # Get specific jobs
            jobs = []
            for job_id in job_ids.split(","):
                try:
                    job_status = await sq_compute.get_job_status(job_id.strip())
                    jobs.append(job_status)
                except Exception as e:
                    click.echo(f"Warning: Could not get status for job {job_id}: {e}", err=True)
        else:
            # List all jobs (simplified - would implement pagination in real system)
            all_jobs = []
            for job_id, job in sq_compute.job_queue.items():
                if not status or job.status.value == status:
                    job_status = await sq_compute.get_job_status(job_id)
                    all_jobs.append(job_status)

            # Limit results
            jobs = all_jobs[:max_results]

        return jobs

    jobs = asyncio.run(_describe_jobs())

    output_format = output or ctx.obj["config"]["output"]
    _display_output(jobs, output_format)

@compute.command("get-job-result")
@click.option("--job-id", required=True, help="Job ID to get results for")
@click.option("--output", type=click.Choice(["json", "yaml", "table"]), help="Output format")
@click.pass_context
def get_job_result(ctx, job_id, output):
    """Get quantum job results"""

    async def _get_result():
        sq_compute = SynapseQuantumCompute()
        return await sq_compute.get_job_status(job_id)

    try:
        result = asyncio.run(_get_result())

        if result["Status"] != "completed":
            click.echo(f"Job {job_id} is not completed yet. Status: {result['Status']}")
            if result["Status"] == "failed":
                click.echo(f"Error: {result.get('ErrorMessage', 'Unknown error')}")
            return

        output_format = output or ctx.obj["config"]["output"]
        _display_output(result, output_format)

    except Exception as e:
        click.echo(f"Error getting job result: {e}", err=True)
        sys.exit(1)

@compute.command("cancel-job")
@click.option("--job-id", required=True, help="Job ID to cancel")
@click.pass_context
def cancel_job(ctx, job_id):
    """Cancel a quantum job (like AWS Batch cancel-job)"""

    async def _cancel_job():
        sq_compute = SynapseQuantumCompute()
        return await sq_compute.cancel_job(job_id)

    try:
        cancelled = asyncio.run(_cancel_job())

        if cancelled:
            click.echo(f"Job {job_id} cancelled successfully")
        else:
            click.echo(f"Job {job_id} could not be cancelled (may be completed or already cancelled)")

    except Exception as e:
        click.echo(f"Error cancelling job: {e}", err=True)
        sys.exit(1)

# Cost and billing commands
@quantum_services.group(name="pricing")
def pricing():
    """Quantum pricing and cost estimation"""
    pass

@pricing.command("estimate-cost")
@click.option("--instance-type", required=True, help="Quantum instance type")
@click.option("--shots", default=1000, help="Number of shots")
@click.option("--circuit-complexity", default=1, help="Circuit complexity factor")
@click.option("--output", type=click.Choice(["json", "yaml", "table"]), help="Output format")
@click.pass_context
def estimate_cost(ctx, instance_type, shots, circuit_complexity, output):
    """Estimate cost for quantum job (like AWS Pricing Calculator)"""

    from synapse_quantum_services.core.compute_service import QuantumPricingCalculator

    calculator = QuantumPricingCalculator()

    try:
        cost = calculator.estimate_cost(
            instance_type=QuantumInstanceType(instance_type),
            shots=shots,
            circuit_complexity=circuit_complexity
        )

        result = {
            "InstanceType": instance_type,
            "Shots": shots,
            "CircuitComplexity": circuit_complexity,
            "EstimatedCost": float(cost),
            "Currency": "USD"
        }

        output_format = output or ctx.obj["config"]["output"]
        _display_output(result, output_format)

    except Exception as e:
        click.echo(f"Error estimating cost: {e}", err=True)
        sys.exit(1)

# Utility functions
def _display_output(data: Any, format_type: str):
    """Display output in specified format"""

    if format_type == "json":
        click.echo(json.dumps(data, indent=2, default=str))
    elif format_type == "yaml":
        click.echo(yaml.dump(data, default_flow_style=False))
    elif format_type == "table":
        _display_table(data)
    else:
        click.echo(json.dumps(data, indent=2, default=str))

def _display_table(data: Any):
    """Display data in table format"""

    if isinstance(data, list) and data:
        # Display as table
        if isinstance(data[0], dict):
            headers = list(data[0].keys())

            # Print headers
            header_line = " | ".join(f"{h:<15}" for h in headers)
            click.echo(header_line)
            click.echo("-" * len(header_line))

            # Print rows
            for item in data:
                row_line = " | ".join(f"{str(item.get(h, '')):<15}" for h in headers)
                click.echo(row_line)
        else:
            for item in data:
                click.echo(item)
    elif isinstance(data, dict):
        # Display key-value pairs
        for key, value in data.items():
            click.echo(f"{key:<20}: {value}")
    else:
        click.echo(str(data))

# Version command
@cli.command()
def version():
    """Show Synapse Quantum CLI version"""
    click.echo("Synapse Quantum CLI v2.2.0")
    click.echo("The AWS CLI for quantum computing")

# Help examples
@cli.command()
def examples():
    """Show usage examples"""
    examples_text = """
Synapse Quantum CLI Examples
============================

# Configure CLI
synapse configure

# List quantum instance types
synapse sq compute describe-instances

# List quantum backends
synapse sq compute describe-backends

# Submit a quantum job
synapse sq compute run-job \
  --circuit "circuit.h(0); circuit.cx(0,1)" \
  --language synapse \
  --instance-type sq.small.8q \
  --shots 1000 \
  --tags project=demo,team=research

# Submit job from file
synapse sq compute run-job \
  --circuit bell_state.qasm \
  --language qasm \
  --instance-type sq.medium.20q \
  --shots 5000

# Monitor job status
synapse sq compute describe-jobs --status running

# Get specific job results
synapse sq compute get-job-result --job-id sq-job-abc123

# Cancel a job
synapse sq compute cancel-job --job-id sq-job-abc123

# Estimate cost
synapse sq pricing estimate-cost \
  --instance-type sq.large.50q \
  --shots 10000 \
  --circuit-complexity 5

# Output in different formats
synapse sq compute describe-instances --output table
synapse sq compute describe-instances --output yaml
synapse sq compute describe-instances --output json

For more information, see: https://docs.synapse-lang.org/cli
"""
    click.echo(examples_text)

if __name__ == "__main__":
    cli()
