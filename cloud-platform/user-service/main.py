"""
Synapse User Management Service
Authentication, authorization, and subscription management
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
import bcrypt
import jwt
import uuid
from datetime import datetime, timedelta
import motor.motor_asyncio
import stripe
import os
from enum import Enum

app = FastAPI(
    title="Synapse User Service",
    description="User management and authentication service",
    version="1.0.0"
)

# Configuration
JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key')
MONGO_URL = os.getenv('MONGODB_URL', 'mongodb://mongo:27017/users')
STRIPE_API_KEY = os.getenv('STRIPE_API_KEY')

# Initialize services
security = HTTPBearer()
mongo_client = None
db = None
stripe.api_key = STRIPE_API_KEY

class SubscriptionTier(str, Enum):
    COMMUNITY = "community"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    ACADEMIC = "academic"

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"
    ENTERPRISE_ADMIN = "enterprise_admin"

# --- Models ---

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str
    organization: Optional[str] = None
    role: UserRole = UserRole.USER

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    organization: Optional[str]
    role: UserRole
    subscription_tier: SubscriptionTier
    created_at: datetime
    last_login: Optional[datetime]
    verified: bool
    active: bool

class SubscriptionPlan(BaseModel):
    tier: SubscriptionTier
    name: str
    price_monthly: float
    price_yearly: float
    max_qubits: int
    monthly_quota: int
    gpu_access: bool
    hardware_access: bool
    support_level: str
    features: List[str]

class SubscriptionUpdate(BaseModel):
    tier: SubscriptionTier
    billing_cycle: str = "monthly"  # monthly or yearly

class TeamCreate(BaseModel):
    name: str
    description: str
    max_members: int = 10

class TeamMember(BaseModel):
    user_id: str
    role: str = "member"  # member, admin, owner
    joined_at: datetime

# --- Startup/Shutdown ---

@app.on_event("startup")
async def startup():
    global mongo_client, db
    
    # Connect to MongoDB
    mongo_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
    db = mongo_client.users
    
    # Create indices
    await db.users.create_index("email", unique=True)
    await db.teams.create_index("name", unique=True)
    await db.sessions.create_index("user_id")
    await db.sessions.create_index("expires_at", expireAfterSeconds=0)

@app.on_event("shutdown")
async def shutdown():
    mongo_client.close()

# --- Authentication ---

@app.post("/api/v1/auth/register")
async def register_user(user_data: UserCreate):
    """Register a new user"""
    
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(400, "User already exists")
    
    # Hash password
    password_hash = bcrypt.hashpw(
        user_data.password.encode('utf-8'),
        bcrypt.gensalt()
    )
    
    # Create user document
    user_id = str(uuid.uuid4())
    user_doc = {
        "_id": user_id,
        "email": user_data.email,
        "password_hash": password_hash,
        "full_name": user_data.full_name,
        "organization": user_data.organization,
        "role": user_data.role,
        "subscription_tier": SubscriptionTier.COMMUNITY,
        "created_at": datetime.utcnow(),
        "last_login": None,
        "verified": False,
        "active": True,
        "stripe_customer_id": None,
        "usage_stats": {
            "circuits_run": 0,
            "compute_time": 0,
            "monthly_usage": 0
        }
    }
    
    # Create Stripe customer
    if STRIPE_API_KEY:
        try:
            customer = stripe.Customer.create(
                email=user_data.email,
                name=user_data.full_name,
                metadata={"user_id": user_id}
            )
            user_doc["stripe_customer_id"] = customer.id
        except Exception as e:
            print(f"Failed to create Stripe customer: {e}")
    
    # Insert user
    await db.users.insert_one(user_doc)
    
    # Generate JWT token
    token = generate_jwt_token(user_id, user_data.email, user_data.role)
    
    return {
        "user_id": user_id,
        "email": user_data.email,
        "token": token,
        "subscription_tier": SubscriptionTier.COMMUNITY,
        "message": "User registered successfully"
    }

@app.post("/api/v1/auth/login")
async def login_user(login_data: UserLogin):
    """Authenticate user and return JWT token"""
    
    # Find user
    user = await db.users.find_one({"email": login_data.email})
    if not user:
        raise HTTPException(401, "Invalid credentials")
    
    # Verify password
    if not bcrypt.checkpw(
        login_data.password.encode('utf-8'),
        user["password_hash"]
    ):
        raise HTTPException(401, "Invalid credentials")
    
    # Check if user is active
    if not user.get("active", True):
        raise HTTPException(403, "Account deactivated")
    
    # Update last login
    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"last_login": datetime.utcnow()}}
    )
    
    # Generate JWT token
    token = generate_jwt_token(
        user["_id"],
        user["email"],
        user["role"]
    )
    
    return {
        "user_id": user["_id"],
        "email": user["email"],
        "token": token,
        "subscription_tier": user["subscription_tier"],
        "role": user["role"]
    }

@app.post("/api/v1/auth/logout")
async def logout_user(token: str = Depends(verify_token)):
    """Logout user and invalidate token"""
    
    # Add token to blacklist (in Redis in production)
    await db.blacklisted_tokens.insert_one({
        "token": token,
        "blacklisted_at": datetime.utcnow()
    })
    
    return {"message": "Logged out successfully"}

# --- User Management ---

@app.get("/api/v1/users/profile")
async def get_user_profile(current_user = Depends(get_current_user)):
    """Get current user's profile"""
    
    user = await db.users.find_one({"_id": current_user["user_id"]})
    if not user:
        raise HTTPException(404, "User not found")
    
    return UserResponse(
        id=user["_id"],
        email=user["email"],
        full_name=user["full_name"],
        organization=user.get("organization"),
        role=user["role"],
        subscription_tier=user["subscription_tier"],
        created_at=user["created_at"],
        last_login=user.get("last_login"),
        verified=user.get("verified", False),
        active=user.get("active", True)
    )

@app.put("/api/v1/users/profile")
async def update_user_profile(
    updates: Dict[str, Any],
    current_user = Depends(get_current_user)
):
    """Update user profile"""
    
    # Only allow certain fields to be updated
    allowed_fields = {"full_name", "organization"}
    update_data = {k: v for k, v in updates.items() if k in allowed_fields}
    
    if not update_data:
        raise HTTPException(400, "No valid fields to update")
    
    # Update user
    result = await db.users.update_one(
        {"_id": current_user["user_id"]},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(404, "User not found")
    
    return {"message": "Profile updated successfully"}

@app.delete("/api/v1/users/account")
async def delete_user_account(current_user = Depends(get_current_user)):
    """Delete user account"""
    
    user_id = current_user["user_id"]
    
    # Get user for Stripe cleanup
    user = await db.users.find_one({"_id": user_id})
    if not user:
        raise HTTPException(404, "User not found")
    
    # Cancel Stripe subscription if exists
    if user.get("stripe_customer_id") and STRIPE_API_KEY:
        try:
            subscriptions = stripe.Subscription.list(
                customer=user["stripe_customer_id"]
            )
            for sub in subscriptions.data:
                stripe.Subscription.delete(sub.id)
        except Exception as e:
            print(f"Failed to cancel Stripe subscription: {e}")
    
    # Soft delete user
    await db.users.update_one(
        {"_id": user_id},
        {
            "$set": {
                "active": False,
                "deleted_at": datetime.utcnow(),
                "email": f"deleted_{user_id}@deleted.com"
            }
        }
    )
    
    return {"message": "Account deleted successfully"}

# --- Subscription Management ---

@app.get("/api/v1/subscriptions/plans")
async def get_subscription_plans():
    """Get available subscription plans"""
    
    plans = [
        SubscriptionPlan(
            tier=SubscriptionTier.COMMUNITY,
            name="Community",
            price_monthly=0,
            price_yearly=0,
            max_qubits=5,
            monthly_quota=1000,
            gpu_access=False,
            hardware_access=False,
            support_level="community",
            features=[
                "Basic quantum simulator",
                "Community support",
                "Limited circuit execution"
            ]
        ),
        SubscriptionPlan(
            tier=SubscriptionTier.PROFESSIONAL,
            name="Professional",
            price_monthly=299,
            price_yearly=2990,
            max_qubits=20,
            monthly_quota=10000,
            gpu_access=True,
            hardware_access=False,
            support_level="priority",
            features=[
                "Advanced quantum simulator",
                "GPU acceleration",
                "Priority support",
                "Cloud execution",
                "Package registry access"
            ]
        ),
        SubscriptionPlan(
            tier=SubscriptionTier.ENTERPRISE,
            name="Enterprise",
            price_monthly=2999,
            price_yearly=29990,
            max_qubits=50,
            monthly_quota=100000,
            gpu_access=True,
            hardware_access=True,
            support_level="dedicated",
            features=[
                "Unlimited simulator access",
                "Real hardware access",
                "Private cloud deployment",
                "24/7 dedicated support",
                "Custom integrations",
                "Team management",
                "SSO integration"
            ]
        ),
        SubscriptionPlan(
            tier=SubscriptionTier.ACADEMIC,
            name="Academic",
            price_monthly=99,
            price_yearly=990,
            max_qubits=15,
            monthly_quota=5000,
            gpu_access=True,
            hardware_access=False,
            support_level="standard",
            features=[
                "Educational resources",
                "Classroom tools",
                "Student management",
                "Research collaboration"
            ]
        )
    ]
    
    return {"plans": plans}

@app.post("/api/v1/subscriptions/upgrade")
async def upgrade_subscription(
    subscription_data: SubscriptionUpdate,
    current_user = Depends(get_current_user)
):
    """Upgrade user subscription"""
    
    user_id = current_user["user_id"]
    
    # Get user
    user = await db.users.find_one({"_id": user_id})
    if not user:
        raise HTTPException(404, "User not found")
    
    # Check if downgrading
    current_tier = user["subscription_tier"]
    if subscription_data.tier == current_tier:
        raise HTTPException(400, "Already on this subscription tier")
    
    # Create Stripe subscription
    if STRIPE_API_KEY and user.get("stripe_customer_id"):
        try:
            # Get price ID based on tier and billing cycle
            price_id = get_stripe_price_id(subscription_data.tier, subscription_data.billing_cycle)
            
            # Create subscription
            subscription = stripe.Subscription.create(
                customer=user["stripe_customer_id"],
                items=[{"price": price_id}],
                metadata={
                    "user_id": user_id,
                    "tier": subscription_data.tier
                }
            )
            
            # Update user subscription
            await db.users.update_one(
                {"_id": user_id},
                {
                    "$set": {
                        "subscription_tier": subscription_data.tier,
                        "stripe_subscription_id": subscription.id,
                        "subscription_updated_at": datetime.utcnow()
                    }
                }
            )
            
            return {
                "message": "Subscription upgraded successfully",
                "subscription_id": subscription.id,
                "tier": subscription_data.tier
            }
            
        except Exception as e:
            raise HTTPException(500, f"Failed to create subscription: {e}")
    else:
        # Update without payment (for testing or free tiers)
        await db.users.update_one(
            {"_id": user_id},
            {
                "$set": {
                    "subscription_tier": subscription_data.tier,
                    "subscription_updated_at": datetime.utcnow()
                }
            }
        )
        
        return {
            "message": "Subscription updated successfully",
            "tier": subscription_data.tier
        }

# --- Team Management ---

@app.post("/api/v1/teams")
async def create_team(
    team_data: TeamCreate,
    current_user = Depends(get_current_user)
):
    """Create a new team (Enterprise only)"""
    
    # Check if user has enterprise subscription
    user = await db.users.find_one({"_id": current_user["user_id"]})
    if user["subscription_tier"] != SubscriptionTier.ENTERPRISE:
        raise HTTPException(403, "Enterprise subscription required")
    
    # Check if team name exists
    existing_team = await db.teams.find_one({"name": team_data.name})
    if existing_team:
        raise HTTPException(400, "Team name already exists")
    
    # Create team
    team_id = str(uuid.uuid4())
    team_doc = {
        "_id": team_id,
        "name": team_data.name,
        "description": team_data.description,
        "max_members": team_data.max_members,
        "owner_id": current_user["user_id"],
        "created_at": datetime.utcnow(),
        "members": [
            {
                "user_id": current_user["user_id"],
                "role": "owner",
                "joined_at": datetime.utcnow()
            }
        ]
    }
    
    await db.teams.insert_one(team_doc)
    
    return {
        "team_id": team_id,
        "name": team_data.name,
        "message": "Team created successfully"
    }

@app.post("/api/v1/teams/{team_id}/members")
async def add_team_member(
    team_id: str,
    member_email: str,
    role: str = "member",
    current_user = Depends(get_current_user)
):
    """Add member to team"""
    
    # Check if user is team admin/owner
    team = await db.teams.find_one({"_id": team_id})
    if not team:
        raise HTTPException(404, "Team not found")
    
    user_role = next(
        (m["role"] for m in team["members"] if m["user_id"] == current_user["user_id"]),
        None
    )
    
    if user_role not in ["owner", "admin"]:
        raise HTTPException(403, "Admin access required")
    
    # Find user to add
    new_member = await db.users.find_one({"email": member_email})
    if not new_member:
        raise HTTPException(404, "User not found")
    
    # Check if already a member
    existing_member = next(
        (m for m in team["members"] if m["user_id"] == new_member["_id"]),
        None
    )
    
    if existing_member:
        raise HTTPException(400, "User is already a team member")
    
    # Add member
    await db.teams.update_one(
        {"_id": team_id},
        {
            "$push": {
                "members": {
                    "user_id": new_member["_id"],
                    "role": role,
                    "joined_at": datetime.utcnow()
                }
            }
        }
    )
    
    return {
        "message": f"Added {member_email} to team",
        "user_id": new_member["_id"],
        "role": role
    }

# --- Helper Functions ---

def generate_jwt_token(user_id: str, email: str, role: str) -> str:
    """Generate JWT token for user"""
    
    payload = {
        "user_id": user_id,
        "email": email,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=24),
        "iat": datetime.utcnow()
    }
    
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token"""
    
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        
        # Check if token is blacklisted
        blacklisted = await db.blacklisted_tokens.find_one({"token": token})
        if blacklisted:
            raise HTTPException(401, "Token has been revoked")
        
        return payload
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid token")

async def get_current_user(token_payload = Depends(verify_token)):
    """Get current user from token"""
    return token_payload

def get_stripe_price_id(tier: SubscriptionTier, billing_cycle: str) -> str:
    """Get Stripe price ID for subscription tier and billing cycle"""
    
    # These would be actual Stripe price IDs
    price_map = {
        (SubscriptionTier.PROFESSIONAL, "monthly"): "price_professional_monthly",
        (SubscriptionTier.PROFESSIONAL, "yearly"): "price_professional_yearly",
        (SubscriptionTier.ENTERPRISE, "monthly"): "price_enterprise_monthly",
        (SubscriptionTier.ENTERPRISE, "yearly"): "price_enterprise_yearly",
        (SubscriptionTier.ACADEMIC, "monthly"): "price_academic_monthly",
        (SubscriptionTier.ACADEMIC, "yearly"): "price_academic_yearly",
    }
    
    return price_map.get((tier, billing_cycle), "default_price")

# --- Health Check ---

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    
    try:
        # Test MongoDB connection
        await db.command("ping")
        
        return {
            "status": "healthy",
            "services": {
                "mongodb": "connected",
                "stripe": "configured" if STRIPE_API_KEY else "not_configured"
            },
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(503, f"Service unhealthy: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)