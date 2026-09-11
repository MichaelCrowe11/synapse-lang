"""
API v1 routers
"""

from app.api.v1.api_keys import router as api_keys_router
from app.api.v1.auth import router as auth_router
from app.api.v1.subscriptions import router as subscriptions_router
from app.api.v1.users import router as users_router

# Export routers
auth = auth_router
users = users_router
api_keys = api_keys_router
subscriptions = subscriptions_router

__all__ = ["auth", "users", "api_keys", "subscriptions"]
