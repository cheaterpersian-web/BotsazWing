"""Authentication API endpoints."""

import uuid
from datetime import timedelta
from typing import Union
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..crud import UserCRUD, AdminCRUD
from ..schemas import User, Admin, Token, UserCreate, AdminCreate
from ..security import create_access_token, verify_token
from .dependencies import get_current_user, get_current_admin
from ..config import settings

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login/telegram", response_model=Token)
async def login_telegram(
    telegram_user_id: int,
    username: str = None,
    first_name: str = None,
    last_name: str = None,
    language_code: str = "en",
    db: AsyncSession = Depends(get_db)
):
    """Login with Telegram user data."""
    # Check if user exists
    user = await UserCRUD.get_by_telegram_id(db, telegram_user_id)
    
    if not user:
        # Create new user
        user_data = UserCreate(
            telegram_user_id=telegram_user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            language_code=language_code
        )
        user = await UserCRUD.create(db, user_data)
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"user_id": str(user.id), "is_admin": False},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login/admin", response_model=Token)
async def login_admin(
    telegram_user_id: int,
    username: str = None,
    first_name: str = None,
    last_name: str = None,
    db: AsyncSession = Depends(get_db)
):
    """Login as admin with Telegram user data."""
    # Check if admin exists
    admin = await AdminCRUD.get_by_telegram_id(db, telegram_user_id)
    
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access not granted"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"admin_id": str(admin.id), "is_admin": True},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=Union[User, Admin])
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    current_admin: Admin = Depends(get_current_admin)
):
    """Get current user or admin information."""
    return current_admin or current_user


@router.post("/verify-token")
async def verify_token_endpoint(token: str):
    """Verify a JWT token."""
    try:
        payload = verify_token(token)
        return {"valid": True, "payload": payload}
    except HTTPException:
        return {"valid": False, "payload": None}