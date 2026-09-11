"""
Synapse Quantum Developer Console API
AWS Management Console equivalent for quantum computing
"""

import asyncio
import json
import os

# Import our quantum services
import sys
from datetime import datetime, timedelta
from typing import Any

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from synapse_quantum_services.core.compute_service import (
    QuantumBackendProvider,
    QuantumInstanceType,
    SynapseQuantumCompute,
)
from synapse_quantum_services.core.quantum_autoscaling import QuantumAutoScaler
from synapse_quantum_services.marketplace.quantum_marketplace import (
    MarketplaceCategory,
    QuantumMarketplace,
)

app = FastAPI(
    title="Synapse Quantum Console API",
    description="AWS Management Console for quantum computing",
    version="1.0.0"
)

# CORS middleware for web console
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
quantum_compute = SynapseQuantumCompute()
quantum_marketplace = QuantumMarketplace()
quantum_autoscaler = QuantumAutoScaler()

# WebSocket connections for real-time updates
active_connections: list[WebSocket] = []

# Models for API requests
class DashboardFilters(BaseModel):
    time_range: str = "24h"  # "1h", "24h", "7d", "30d"
    region: str | None = None
    service: str | None = None

class JobSubmissionRequest(BaseModel):
    circuit_code: str
    language: str = "synapse"
    instance_type: str = "sq.small.8q"
    shots: int = 1000
    backend_preference: list[str] = ["auto"]
    tags: dict[str, str] = {}

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    await quantum_autoscaler.start_monitoring()
    print("Quantum Console API started")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await quantum_autoscaler.stop_monitoring()

# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            # Send periodic updates
            data = await get_dashboard_data("1h")
            await websocket.send_text(json.dumps(data, default=str))
            await asyncio.sleep(10)  # Update every 10 seconds
    except WebSocketDisconnect:
        active_connections.remove(websocket)

# Dashboard APIs
@app.get("/api/dashboard/overview")
async def get_dashboard_overview():
    """Get main dashboard overview data"""

    return await get_dashboard_data("24h")

async def get_dashboard_data(time_range: str) -> dict[str, Any]:
    """Get comprehensive dashboard data"""

    # Get quantum compute metrics
    compute_metrics = await get_compute_metrics(time_range)

    # Get marketplace metrics
    marketplace_metrics = await get_marketplace_metrics()

    # Get cost metrics
    cost_metrics = await get_cost_metrics(time_range)

    # Get scaling metrics
    scaling_metrics = await get_scaling_metrics()

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "time_range": time_range,
        "compute": compute_metrics,
        "marketplace": marketplace_metrics,
        "costs": cost_metrics,
        "scaling": scaling_metrics,
        "alerts": await get_active_alerts()
    }

async def get_compute_metrics(time_range: str) -> dict[str, Any]:
    """Get quantum compute service metrics"""

    # Simulate metrics (in real system, would query actual data)
    import random

    return {
        "active_jobs": random.randint(15, 50),
        "queued_jobs": random.randint(5, 25),
        "completed_jobs_24h": random.randint(200, 500),
        "failed_jobs_24h": random.randint(5, 20),
        "average_wait_time": random.uniform(30, 120),
        "quantum_utilization": random.uniform(60, 95),
        "error_rate": random.uniform(2, 8),
        "throughput_per_hour": random.uniform(50, 150),
        "backends_status": {
            "ibm_quantum": "healthy",
            "google_quantum": "healthy",
            "aws_braket": "degraded",
            "quantinuum": "healthy"
        },
        "instance_utilization": {
            "sq.nano.2q": {"active": 2, "capacity": 10, "utilization": 20},
            "sq.small.8q": {"active": 8, "capacity": 15, "utilization": 53},
            "sq.medium.20q": {"active": 12, "capacity": 20, "utilization": 60},
            "sq.large.50q": {"active": 3, "capacity": 5, "utilization": 60},
            "sq.xlarge.100q": {"active": 1, "capacity": 2, "utilization": 50}
        }
    }

async def get_marketplace_metrics() -> dict[str, Any]:
    """Get quantum marketplace metrics"""

    # Get real marketplace data
    featured_items = await quantum_marketplace.get_featured_items()
    categories = await quantum_marketplace.get_categories()

    return {
        "total_items": len(quantum_marketplace.items),
        "featured_items": featured_items[:3],  # Top 3 featured
        "categories": categories,
        "recent_downloads": 1250,  # Simulate
        "new_items_this_week": 8,  # Simulate
        "top_categories": [
            {"name": "Algorithms", "count": 45, "growth": "+12%"},
            {"name": "Tools", "count": 23, "growth": "+8%"},
            {"name": "Datasets", "count": 18, "growth": "+15%"}
        ]
    }

async def get_cost_metrics(time_range: str) -> dict[str, Any]:
    """Get cost and billing metrics"""

    import random

    base_cost = random.uniform(500, 2000)

    return {
        "current_month_spend": base_cost,
        "projected_month_spend": base_cost * 1.2,
        "budget_remaining": max(0, 3000 - base_cost),
        "cost_by_service": {
            "quantum_compute": base_cost * 0.6,
            "marketplace_purchases": base_cost * 0.2,
            "storage": base_cost * 0.1,
            "data_transfer": base_cost * 0.1
        },
        "cost_by_instance_type": {
            "sq.small.8q": base_cost * 0.4,
            "sq.medium.20q": base_cost * 0.3,
            "sq.large.50q": base_cost * 0.2,
            "sq.xlarge.100q": base_cost * 0.1
        },
        "daily_spend_trend": [
            {"date": "2024-01-10", "amount": base_cost * 0.8},
            {"date": "2024-01-11", "amount": base_cost * 0.9},
            {"date": "2024-01-12", "amount": base_cost * 1.1},
            {"date": "2024-01-13", "amount": base_cost * 1.0},
            {"date": "2024-01-14", "amount": base_cost * 1.2}
        ]
    }

async def get_scaling_metrics() -> dict[str, Any]:
    """Get auto-scaling metrics"""

    targets = await quantum_autoscaler.get_scaling_targets()
    policies = await quantum_autoscaler.get_scaling_policies()
    history = await quantum_autoscaler.get_scaling_history(hours=24)

    return {
        "scaling_targets": targets,
        "active_policies": len([p for p in policies if p["enabled"]]),
        "scaling_actions_24h": len(history),
        "recent_actions": history[-5:] if history else []
    }

async def get_active_alerts() -> list[dict[str, Any]]:
    """Get active system alerts"""

    import random

    alerts = []

    # Simulate some alerts
    if random.random() < 0.3:  # 30% chance of high queue alert
        alerts.append({
            "id": "alert-queue-high",
            "severity": "warning",
            "title": "High Queue Depth",
            "message": "Quantum job queue depth is above threshold (25 jobs)",
            "timestamp": (datetime.utcnow() - timedelta(minutes=15)).isoformat(),
            "service": "quantum_compute"
        })

    if random.random() < 0.2:  # 20% chance of backend alert
        alerts.append({
            "id": "alert-backend-degraded",
            "severity": "warning",
            "title": "Backend Performance Degraded",
            "message": "AWS Braket backend showing increased error rates",
            "timestamp": (datetime.utcnow() - timedelta(minutes=30)).isoformat(),
            "service": "quantum_backends"
        })

    if random.random() < 0.1:  # 10% chance of cost alert
        alerts.append({
            "id": "alert-cost-threshold",
            "severity": "info",
            "title": "Cost Threshold Reached",
            "message": "Monthly spend has reached 80% of budget",
            "timestamp": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
            "service": "billing"
        })

    return alerts

# Quantum Compute Service APIs
@app.get("/api/compute/instances")
async def list_quantum_instances():
    """List available quantum instance types"""
    return await quantum_compute.describe_quantum_instances()

@app.get("/api/compute/backends")
async def list_quantum_backends():
    """List available quantum backends"""
    return await quantum_compute.describe_quantum_backends()

@app.post("/api/compute/jobs")
async def submit_quantum_job(request: JobSubmissionRequest):
    """Submit a new quantum job"""

    try:
        # Convert backend preferences
        backend_enums = []
        for pref in request.backend_preference:
            try:
                backend_enums.append(QuantumBackendProvider(pref))
            except ValueError:
                backend_enums.append(QuantumBackendProvider.AUTO)

        job = await quantum_compute.run_quantum_job(
            circuit_code=request.circuit_code,
            language=request.language,
            instance_type=QuantumInstanceType(request.instance_type),
            shots=request.shots,
            backend_preference=backend_enums,
            tags=request.tags
        )

        return {
            "job_id": job.job_id,
            "status": job.status.value,
            "estimated_cost": float(job.estimated_cost) if job.estimated_cost else None,
            "created_at": job.created_at.isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/compute/jobs")
async def list_quantum_jobs(status: str | None = None, limit: int = 50):
    """List quantum jobs"""

    jobs = []
    for job_id, job in quantum_compute.job_queue.items():
        if not status or job.status.value == status:
            job_data = await quantum_compute.get_job_status(job_id)
            jobs.append(job_data)

    return {"jobs": jobs[:limit]}

@app.get("/api/compute/jobs/{job_id}")
async def get_quantum_job(job_id: str):
    """Get quantum job details"""

    try:
        return await quantum_compute.get_job_status(job_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.delete("/api/compute/jobs/{job_id}")
async def cancel_quantum_job(job_id: str):
    """Cancel a quantum job"""

    try:
        success = await quantum_compute.cancel_job(job_id)
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

# Marketplace APIs
@app.get("/api/marketplace/search")
async def search_marketplace(
    query: str | None = None,
    category: str | None = None,
    tags: str | None = None,
    min_rating: float | None = None,
    sort_by: str = "relevance",
    limit: int = 20,
    offset: int = 0
):
    """Search quantum marketplace"""

    # Convert parameters
    tag_list = tags.split(",") if tags else None
    category_enum = MarketplaceCategory(category) if category else None

    return await quantum_marketplace.search_marketplace(
        query=query,
        category=category_enum,
        tags=tag_list,
        min_rating=min_rating,
        sort_by=sort_by,
        limit=limit,
        offset=offset
    )

@app.get("/api/marketplace/items/{item_id}")
async def get_marketplace_item(item_id: str):
    """Get marketplace item details"""

    try:
        return await quantum_marketplace.get_item_details(item_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/api/marketplace/featured")
async def get_featured_items():
    """Get featured marketplace items"""
    return await quantum_marketplace.get_featured_items()

@app.get("/api/marketplace/trending")
async def get_trending_items():
    """Get trending marketplace items"""
    return await quantum_marketplace.get_trending_items()

@app.get("/api/marketplace/categories")
async def get_marketplace_categories():
    """Get marketplace categories"""
    return await quantum_marketplace.get_categories()

@app.post("/api/marketplace/purchase/{item_id}")
async def purchase_marketplace_item(item_id: str, user_id: str = "current_user"):
    """Purchase a marketplace item"""

    try:
        return await quantum_marketplace.purchase_item(item_id, user_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Auto-scaling APIs
@app.get("/api/autoscaling/policies")
async def get_scaling_policies():
    """Get auto-scaling policies"""
    return await quantum_autoscaler.get_scaling_policies()

@app.get("/api/autoscaling/targets")
async def get_scaling_targets():
    """Get scaling targets"""
    return await quantum_autoscaler.get_scaling_targets()

@app.get("/api/autoscaling/history")
async def get_scaling_history(hours: int = 24):
    """Get scaling action history"""
    return await quantum_autoscaler.get_scaling_history(hours)

# Cost and billing APIs
@app.get("/api/billing/current")
async def get_current_billing():
    """Get current billing information"""
    return await get_cost_metrics("current_month")

@app.get("/api/billing/estimate")
async def estimate_cost(
    instance_type: str,
    shots: int = 1000,
    circuit_complexity: int = 1
):
    """Estimate cost for quantum job"""

    from synapse_quantum_services.core.compute_service import QuantumPricingCalculator

    calculator = QuantumPricingCalculator()

    try:
        cost = calculator.estimate_cost(
            instance_type=QuantumInstanceType(instance_type),
            shots=shots,
            circuit_complexity=circuit_complexity
        )

        return {
            "instance_type": instance_type,
            "shots": shots,
            "circuit_complexity": circuit_complexity,
            "estimated_cost": float(cost),
            "currency": "USD"
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# System status APIs
@app.get("/api/status/health")
async def get_system_health():
    """Get overall system health"""

    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "quantum_compute": "healthy",
            "marketplace": "healthy",
            "autoscaling": "healthy",
            "billing": "healthy"
        },
        "regions": {
            "us-quantum-1": "healthy",
            "eu-quantum-1": "healthy",
            "asia-quantum-1": "degraded"
        }
    }

@app.get("/api/status/metrics")
async def get_system_metrics():
    """Get system-wide metrics"""

    import random

    return {
        "requests_per_second": random.uniform(10, 100),
        "average_response_time": random.uniform(50, 200),
        "error_rate": random.uniform(0.1, 2.0),
        "active_users": random.randint(50, 500),
        "total_jobs_today": random.randint(1000, 5000),
        "quantum_backends_online": 15,
        "quantum_backends_total": 18
    }

# User management APIs (simplified)
@app.get("/api/user/profile")
async def get_user_profile(user_id: str = "current_user"):
    """Get user profile"""

    # Simulate user profile
    return {
        "user_id": user_id,
        "username": "quantum_researcher",
        "email": "researcher@example.com",
        "organization": "MIT Quantum Lab",
        "subscription_tier": "professional",
        "quantum_credits": 5000,
        "jobs_run_this_month": 150,
        "marketplace_purchases": 8,
        "member_since": "2023-06-15"
    }

@app.get("/api/user/purchases")
async def get_user_purchases(user_id: str = "current_user"):
    """Get user's marketplace purchases"""
    return await quantum_marketplace.get_user_purchases(user_id)

# Static file serving for web console
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def get_console_home():
    """Serve the main console page"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Synapse Quantum Console</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; background: #f5f5f5; }
            .header { background: #232f3e; color: white; padding: 1rem 2rem; display: flex; align-items: center; }
            .logo { font-size: 1.5rem; font-weight: bold; }
            .nav { margin-left: 2rem; }
            .nav a { color: #adb5bd; text-decoration: none; margin-right: 2rem; }
            .nav a:hover { color: white; }
            .container { max-width: 1200px; margin: 2rem auto; padding: 0 2rem; }
            .card { background: white; border-radius: 8px; padding: 2rem; margin-bottom: 2rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; }
            .metric { text-align: center; }
            .metric-value { font-size: 2rem; font-weight: bold; color: #0066cc; }
            .metric-label { color: #666; margin-top: 0.5rem; }
            .status-healthy { color: #28a745; }
            .status-warning { color: #ffc107; }
            .status-error { color: #dc3545; }
        </style>
    </head>
    <body>
        <div class="header">
            <div class="logo">⚛️ Synapse Quantum Console</div>
            <nav class="nav">
                <a href="#dashboard">Dashboard</a>
                <a href="#compute">Quantum Compute</a>
                <a href="#marketplace">Marketplace</a>
                <a href="#autoscaling">Auto Scaling</a>
                <a href="#billing">Billing</a>
            </nav>
        </div>

        <div class="container">
            <div class="card">
                <h2>🚀 Welcome to Synapse Quantum Cloud</h2>
                <p>The AWS of quantum computing - making quantum accessible to everyone.</p>

                <div class="metrics">
                    <div class="metric">
                        <div class="metric-value" id="active-jobs">-</div>
                        <div class="metric-label">Active Jobs</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value" id="quantum-utilization">-</div>
                        <div class="metric-label">Quantum Utilization</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value" id="monthly-spend">-</div>
                        <div class="metric-label">Monthly Spend</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value status-healthy" id="system-status">Healthy</div>
                        <div class="metric-label">System Status</div>
                    </div>
                </div>
            </div>

            <div class="card">
                <h3>🎯 Quick Actions</h3>
                <p>
                    <button onclick="submitSampleJob()">Submit Sample Quantum Job</button>
                    <button onclick="openMarketplace()">Browse Marketplace</button>
                    <button onclick="viewCosts()">View Cost Analysis</button>
                    <button onclick="openDocumentation()">View Documentation</button>
                </p>
            </div>

            <div class="card">
                <h3>📊 Real-Time Dashboard</h3>
                <div id="dashboard-data">
                    <p>Loading dashboard data...</p>
                </div>
            </div>
        </div>

        <script>
            // WebSocket connection for real-time updates
            const ws = new WebSocket('ws://localhost:8000/ws');

            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                updateDashboard(data);
            };

            function updateDashboard(data) {
                document.getElementById('active-jobs').textContent = data.compute.active_jobs;
                document.getElementById('quantum-utilization').textContent = data.compute.quantum_utilization.toFixed(1) + '%';
                document.getElementById('monthly-spend').textContent = '$' + data.costs.current_month_spend.toFixed(0);

                // Update dashboard data section
                const dashboardDiv = document.getElementById('dashboard-data');
                dashboardDiv.innerHTML = `
                    <h4>Live Metrics</h4>
                    <p><strong>Queue Depth:</strong> ${data.compute.queued_jobs} jobs</p>
                    <p><strong>Avg Wait Time:</strong> ${data.compute.average_wait_time.toFixed(1)}s</p>
                    <p><strong>Error Rate:</strong> ${data.compute.error_rate.toFixed(1)}%</p>
                    <p><strong>Throughput:</strong> ${data.compute.throughput_per_hour.toFixed(0)} jobs/hour</p>

                    <h4>Backend Status</h4>
                    ${Object.entries(data.compute.backends_status).map(([backend, status]) =>
                        `<p><strong>${backend}:</strong> <span class="status-${status}">${status}</span></p>`
                    ).join('')}

                    <h4>Recent Alerts</h4>
                    ${data.alerts.length > 0 ?
                        data.alerts.map(alert =>
                            `<p class="status-${alert.severity}"><strong>${alert.title}:</strong> ${alert.message}</p>`
                        ).join('') :
                        '<p>No active alerts</p>'
                    }
                `;
            }

            function submitSampleJob() {
                fetch('/api/compute/jobs', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        circuit_code: 'circuit = QuantumCircuit(2); circuit.h(0); circuit.cx(0,1); circuit.measure_all()',
                        language: 'qiskit',
                        instance_type: 'sq.small.8q',
                        shots: 1000,
                        tags: {'demo': 'console', 'type': 'bell_state'}
                    })
                })
                .then(response => response.json())
                .then(data => alert(`Job submitted! ID: ${data.job_id}`))
                .catch(error => alert('Error: ' + error));
            }

            function openMarketplace() {
                window.open('/api/marketplace/featured', '_blank');
            }

            function viewCosts() {
                window.open('/api/billing/current', '_blank');
            }

            function openDocumentation() {
                window.open('https://docs.synapse-lang.org', '_blank');
            }

            // Load initial data
            fetch('/api/dashboard/overview')
                .then(response => response.json())
                .then(data => updateDashboard(data));
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
