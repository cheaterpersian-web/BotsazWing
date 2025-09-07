"""API dependencies for authentication and authorization."""

import uuid
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..crud import UserCRUD, AdminCRUD
from ..security import verify_token
from ..schemas import User, Admin

# Security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user."""
    token = credentials.credentials
    payload = verify_token(token)
    
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    user = await UserCRUD.get_by_id(db, uuid.UUID(user_id))
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    return user


async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Admin:
    """Get current authenticated admin."""
    token = credentials.credentials
    payload = verify_token(token)
    
    admin_id = payload.get("admin_id")
    is_admin = payload.get("is_admin", False)
    
    if not admin_id or not is_admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin authentication required"
        )
    
    admin = await AdminCRUD.get_by_id(db, uuid.UUID(admin_id))
    if not admin or not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin not found or inactive"
        )
    
    return admin


async def get_current_user_or_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> tuple[Optional[User], Optional[Admin]]:
    """Get current authenticated user or admin."""
    token = credentials.credentials
    payload = verify_token(token)
    
    user_id = payload.get("user_id")
    admin_id = payload.get("admin_id")
    is_admin = payload.get("is_admin", False)
    
    user = None
    admin = None
    
    if user_id:
        user = await UserCRUD.get_by_id(db, uuid.UUID(user_id))
        if not user or not user.is_active:
            user = None
    
    if admin_id and is_admin:
        admin = await AdminCRUD.get_by_id(db, uuid.UUID(admin_id))
        if not admin or not admin.is_active:
            admin = None
    
    if not user and not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    return user, admin


def require_permission(permission: str):
    """Decorator to require specific admin permission."""
    async def permission_checker(admin: Admin = Depends(get_current_admin)):
        if not admin.permissions.get(permission, False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required"
            )
        return admin
    
    return permission_checker


# Permission dependencies
require_manage_users = require_permission("manage_users")
require_manage_bots = require_permission("manage_bots")
require_manage_payments = require_permission("manage_payments")
require_manage_subscriptions = require_permission("manage_subscriptions")