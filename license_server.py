"""
Synapse-Lang License Server
Handles license validation, activation, and management
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
import datetime
import hashlib
import secrets
import json
import sqlite3
from contextlib import contextmanager
import stripe
import os
from synapse_licensing import LicenseType, LicenseManager

# Configuration
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "sk_test_...")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_...")
DATABASE_URL = os.getenv("DATABASE_URL", "licenses.db")
API_KEY = os.getenv("API_KEY", "synapse-api-key-2024")

stripe.api_key = STRIPE_SECRET_KEY

app = FastAPI(title="Synapse-Lang License Server", version="1.0.0")
security = HTTPBearer()

# Database schema
SCHEMA = """
CREATE TABLE IF NOT EXISTS licenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    license_key TEXT UNIQUE NOT NULL,
    license_type TEXT NOT NULL,
    owner_name TEXT NOT NULL,
    owner_email TEXT NOT NULL,
    organization TEXT,
    issued_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expiry_date TIMESTAMP,
    max_cores INTEGER DEFAULT 4,
    max_qubits INTEGER DEFAULT 30,
    max_activations INTEGER DEFAULT 1,
    activation_count INTEGER DEFAULT 0,
    stripe_customer_id TEXT,
    stripe_subscription_id TEXT,
    metadata TEXT,
    active BOOLEAN DEFAULT 1
);

CREATE TABLE IF NOT EXISTS activations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    license_key TEXT NOT NULL,
    machine_id TEXT NOT NULL,
    activation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP,
    ip_address TEXT,
    platform TEXT,
    FOREIGN KEY (license_key) REFERENCES licenses(license_key)
);

CREATE TABLE IF NOT EXISTS usage_telemetry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    license_key TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    feature_used TEXT,
    duration_seconds REAL,
    cpu_cores_used INTEGER,
    memory_mb_used INTEGER,
    metadata TEXT,
    FOREIGN KEY (license_key) REFERENCES licenses(license_key)
);
"""

# Models
class LicenseActivation(BaseModel):
    license_key: str
    email: EmailStr
    machine_id: str
    platform: Optional[str] = None

class LicenseValidation(BaseModel):
    license_key: str
    machine_id: str

class LicenseCreation(BaseModel):
    license_type: str
    owner_name: str
    owner_email: EmailStr
    organization: Optional[str] = None
    duration_days: Optional[int] = None
    max_activations: int = 1

class UsageTelemetry(BaseModel):
    license_key: str
    feature_used: str
    duration_seconds: float
    cpu_cores_used: Optional[int] = None
    memory_mb_used: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

# Database connection
@contextmanager
def get_db():
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

# Initialize database
def init_db():
    with get_db() as conn:
        conn.executescript(SCHEMA)
        conn.commit()

# Authentication
def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return credentials.credentials

# Endpoints
@app.on_event("startup")
async def startup():
    """Initialize database on startup"""
    init_db()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "service": "Synapse-Lang License Server"}

@app.post("/api/v1/licenses/create")
async def create_license(
    license_data: LicenseCreation,
    api_key: str = Depends(verify_api_key)
):
    """Create a new license"""
    lm = LicenseManager()
    
    # Generate license key
    license_type = LicenseType(license_data.license_type)
    license_key = lm.generate_license_key(license_type)
    
    # Calculate expiry
    expiry_date = None
    if license_data.duration_days:
        expiry_date = datetime.datetime.now() + datetime.timedelta(days=license_data.duration_days)
    
    # Set limits based on type
    limits = {
        LicenseType.COMMUNITY: (4, 30),
        LicenseType.PROFESSIONAL: (16, 100),
        LicenseType.ENTERPRISE: (-1, -1),
        LicenseType.ACADEMIC: (32, 200),
        LicenseType.TRIAL: (8, 50),
    }
    max_cores, max_qubits = limits.get(license_type, (4, 30))
    
    # Insert into database
    with get_db() as conn:
        try:
            conn.execute("""
                INSERT INTO licenses (
                    license_key, license_type, owner_name, owner_email,
                    organization, expiry_date, max_cores, max_qubits,
                    max_activations
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                license_key, license_data.license_type, license_data.owner_name,
                license_data.owner_email, license_data.organization,
                expiry_date, max_cores, max_qubits, license_data.max_activations
            ))
            conn.commit()
            
            return {
                "license_key": license_key,
                "license_type": license_data.license_type,
                "owner": license_data.owner_name,
                "email": license_data.owner_email,
                "expires": expiry_date.isoformat() if expiry_date else None,
                "max_cores": max_cores,
                "max_qubits": max_qubits
            }
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=400, detail="License creation failed")

@app.post("/api/v1/licenses/activate")
async def activate_license(activation: LicenseActivation):
    """Activate a license for a machine"""
    with get_db() as conn:
        # Check if license exists and is valid
        license_row = conn.execute(
            "SELECT * FROM licenses WHERE license_key = ? AND active = 1",
            (activation.license_key,)
        ).fetchone()
        
        if not license_row:
            raise HTTPException(status_code=404, detail="Invalid license key")
        
        # Check email matches
        if license_row["owner_email"] != activation.email:
            raise HTTPException(status_code=403, detail="Email does not match license")
        
        # Check expiry
        if license_row["expiry_date"]:
            expiry = datetime.datetime.fromisoformat(license_row["expiry_date"])
            if datetime.datetime.now() > expiry:
                raise HTTPException(status_code=403, detail="License has expired")
        
        # Check activation limit
        activation_count = conn.execute(
            "SELECT COUNT(*) as count FROM activations WHERE license_key = ?",
            (activation.license_key,)
        ).fetchone()["count"]
        
        if activation_count >= license_row["max_activations"]:
            # Check if this machine is already activated
            existing = conn.execute(
                "SELECT * FROM activations WHERE license_key = ? AND machine_id = ?",
                (activation.license_key, activation.machine_id)
            ).fetchone()
            
            if not existing:
                raise HTTPException(
                    status_code=403,
                    detail=f"License activation limit reached ({license_row['max_activations']})"
                )
        
        # Create or update activation
        conn.execute("""
            INSERT OR REPLACE INTO activations (
                license_key, machine_id, activation_date, last_seen, platform
            ) VALUES (?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, ?)
        """, (activation.license_key, activation.machine_id, activation.platform))
        
        # Update activation count
        conn.execute(
            "UPDATE licenses SET activation_count = ? WHERE license_key = ?",
            (activation_count + 1, activation.license_key)
        )
        conn.commit()
        
        return {
            "status": "activated",
            "license_type": license_row["license_type"],
            "expires": license_row["expiry_date"],
            "max_cores": license_row["max_cores"],
            "max_qubits": license_row["max_qubits"]
        }

@app.post("/api/v1/licenses/validate")
async def validate_license(validation: LicenseValidation):
    """Validate a license is active and valid for a machine"""
    with get_db() as conn:
        # Check license and activation
        result = conn.execute("""
            SELECT l.*, a.activation_date
            FROM licenses l
            JOIN activations a ON l.license_key = a.license_key
            WHERE l.license_key = ? AND a.machine_id = ? AND l.active = 1
        """, (validation.license_key, validation.machine_id)).fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="License not found or not activated")
        
        # Check expiry
        if result["expiry_date"]:
            expiry = datetime.datetime.fromisoformat(result["expiry_date"])
            if datetime.datetime.now() > expiry:
                raise HTTPException(status_code=403, detail="License has expired")
        
        # Update last seen
        conn.execute(
            "UPDATE activations SET last_seen = CURRENT_TIMESTAMP WHERE license_key = ? AND machine_id = ?",
            (validation.license_key, validation.machine_id)
        )
        conn.commit()
        
        return {
            "valid": True,
            "license_type": result["license_type"],
            "expires": result["expiry_date"],
            "features": get_features_for_type(result["license_type"])
        }

@app.post("/api/v1/telemetry/usage")
async def report_usage(telemetry: UsageTelemetry):
    """Report usage telemetry (Enterprise only)"""
    with get_db() as conn:
        # Verify license is enterprise
        license_row = conn.execute(
            "SELECT license_type FROM licenses WHERE license_key = ?",
            (telemetry.license_key,)
        ).fetchone()
        
        if not license_row or license_row["license_type"] != "enterprise":
            raise HTTPException(status_code=403, detail="Telemetry requires Enterprise license")
        
        # Store telemetry
        conn.execute("""
            INSERT INTO usage_telemetry (
                license_key, feature_used, duration_seconds,
                cpu_cores_used, memory_mb_used, metadata
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            telemetry.license_key, telemetry.feature_used,
            telemetry.duration_seconds, telemetry.cpu_cores_used,
            telemetry.memory_mb_used,
            json.dumps(telemetry.metadata) if telemetry.metadata else None
        ))
        conn.commit()
        
        return {"status": "recorded"}

@app.post("/api/v1/stripe/webhook")
async def stripe_webhook(request: dict, stripe_signature: str = Header(None)):
    """Handle Stripe webhooks for subscription management"""
    try:
        event = stripe.Webhook.construct_event(
            json.dumps(request), stripe_signature, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Handle subscription events
    if event["type"] == "customer.subscription.created":
        handle_subscription_created(event["data"]["object"])
    elif event["type"] == "customer.subscription.deleted":
        handle_subscription_cancelled(event["data"]["object"])
    elif event["type"] == "customer.subscription.updated":
        handle_subscription_updated(event["data"]["object"])
    
    return {"status": "success"}

def handle_subscription_created(subscription):
    """Handle new subscription from Stripe"""
    # Create license based on subscription plan
    plan_to_license = {
        "price_professional_monthly": LicenseType.PROFESSIONAL,
        "price_enterprise_monthly": LicenseType.ENTERPRISE,
        "price_academic_yearly": LicenseType.ACADEMIC,
    }
    
    license_type = plan_to_license.get(subscription["items"]["data"][0]["price"]["id"])
    if not license_type:
        return
    
    # Create license in database
    with get_db() as conn:
        lm = LicenseManager()
        license_key = lm.generate_license_key(license_type)
        
        conn.execute("""
            INSERT INTO licenses (
                license_key, license_type, owner_email,
                stripe_customer_id, stripe_subscription_id,
                max_cores, max_qubits, max_activations
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            license_key, license_type.value,
            subscription["customer_email"],
            subscription["customer"],
            subscription["id"],
            -1 if license_type == LicenseType.ENTERPRISE else 16,
            -1 if license_type == LicenseType.ENTERPRISE else 100,
            5 if license_type == LicenseType.ENTERPRISE else 2
        ))
        conn.commit()
        
        # Send license key to customer
        # send_license_email(subscription["customer_email"], license_key)

def handle_subscription_cancelled(subscription):
    """Handle cancelled subscription"""
    with get_db() as conn:
        conn.execute(
            "UPDATE licenses SET active = 0 WHERE stripe_subscription_id = ?",
            (subscription["id"],)
        )
        conn.commit()

def handle_subscription_updated(subscription):
    """Handle subscription updates"""
    # Update license based on new plan
    pass

def get_features_for_type(license_type: str) -> List[str]:
    """Get feature list for license type"""
    lm = LicenseManager()
    lt = LicenseType(license_type)
    return [f.value for f in lm.FEATURE_SETS[lt]]

@app.get("/api/v1/stats")
async def get_stats(api_key: str = Depends(verify_api_key)):
    """Get license statistics"""
    with get_db() as conn:
        stats = {
            "total_licenses": conn.execute("SELECT COUNT(*) as c FROM licenses").fetchone()["c"],
            "active_licenses": conn.execute("SELECT COUNT(*) as c FROM licenses WHERE active = 1").fetchone()["c"],
            "total_activations": conn.execute("SELECT COUNT(*) as c FROM activations").fetchone()["c"],
            "licenses_by_type": dict(conn.execute(
                "SELECT license_type, COUNT(*) as c FROM licenses GROUP BY license_type"
            ).fetchall()),
            "recent_activations": conn.execute(
                "SELECT COUNT(*) as c FROM activations WHERE activation_date > datetime('now', '-7 days')"
            ).fetchone()["c"]
        }
        return stats

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)