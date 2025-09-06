"""User management API endpoints."""

import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..crud import UserCRUD
from ..schemas import User, UserCreate, UserUpdate, PaginatedResponse
from ..api.dependencies import get_current_user, get_current_admin, require_manage_users

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=User)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    """Get current user's profile."""
    return current_user


@router.put("/me", response_model=User)
async def update_my_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user's profile."""
    updated_user = await UserCRUD.update(db, current_user.id, user_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return updated_user


@router.get("/", response_model=PaginatedResponse)
async def list_users(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    current_admin: User = Depends(require_manage_users),
    db: AsyncSession = Depends(get_db)
):
    """List all users (admin only)."""
    skip = (page - 1) * size
    users = await UserCRUD.list_users(db, skip=skip, limit=size)
    
    # Get total count
    total = len(await UserCRUD.list_users(db, skip=0, limit=1000))  # Simplified for demo
    
    return PaginatedResponse(
        items=users,
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size
    )


@router.get("/{user_id}", response_model=User)
async def get_user(
    user_id: uuid.UUID,
    current_admin: User = Depends(require_manage_users),
    db: AsyncSession = Depends(get_db)
):
    """Get user by ID (admin only)."""
    user = await UserCRUD.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.put("/{user_id}", response_model=User)
async def update_user(
    user_id: uuid.UUID,
    user_update: UserUpdate,
    current_admin: User = Depends(require_manage_users),
    db: AsyncSession = Depends(get_db)
):
    """Update user by ID (admin only)."""
    updated_user = await UserCRUD.update(db, user_id, user_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return updated_user


@router.delete("/{user_id}")
async def delete_user(
    user_id: uuid.UUID,
    current_admin: User = Depends(require_manage_users),
    db: AsyncSession = Depends(get_db)
):
    """Delete user by ID (admin only)."""
    success = await UserCRUD.delete(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return {"message": "User deleted successfully"}