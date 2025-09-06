"""Subscription management API endpoints."""

import uuid
from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..crud import SubscriptionCRUD, SubscriptionPlanCRUD, BotInstanceCRUD
from ..schemas import (
    Subscription, SubscriptionCreate, SubscriptionUpdate, 
    SubscriptionPlan, SubscriptionPlanCreate, SubscriptionPlanUpdate,
    PaginatedResponse
)
from ..api.dependencies import get_current_user, get_current_admin, require_manage_subscriptions
from ..schemas import User

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.get("/plans", response_model=List[SubscriptionPlan])
async def get_subscription_plans(db: AsyncSession = Depends(get_db)):
    """Get all active subscription plans."""
    return await SubscriptionPlanCRUD.get_active_plans(db)


@router.post("/plans", response_model=SubscriptionPlan)
async def create_subscription_plan(
    plan_data: SubscriptionPlanCreate,
    current_admin: User = Depends(require_manage_subscriptions),
    db: AsyncSession = Depends(get_db)
):
    """Create a new subscription plan (admin only)."""
    return await SubscriptionPlanCRUD.create(db, plan_data)


@router.put("/plans/{plan_id}", response_model=SubscriptionPlan)
async def update_subscription_plan(
    plan_id: uuid.UUID,
    plan_data: SubscriptionPlanUpdate,
    current_admin: User = Depends(require_manage_subscriptions),
    db: AsyncSession = Depends(get_db)
):
    """Update subscription plan (admin only)."""
    updated_plan = await SubscriptionPlanCRUD.update(db, plan_id, plan_data)
    if not updated_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription plan not found"
        )
    return updated_plan


@router.delete("/plans/{plan_id}")
async def delete_subscription_plan(
    plan_id: uuid.UUID,
    current_admin: User = Depends(require_manage_subscriptions),
    db: AsyncSession = Depends(get_db)
):
    """Delete subscription plan (admin only)."""
    success = await SubscriptionPlanCRUD.delete(db, plan_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription plan not found"
        )
    return {"message": "Subscription plan deleted successfully"}


@router.post("/", response_model=Subscription)
async def create_subscription(
    subscription_data: SubscriptionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new subscription."""
    # Verify bot instance exists and belongs to user
    bot_instance = await BotInstanceCRUD.get_by_id(db, subscription_data.bot_instance_id)
    if not bot_instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bot instance not found"
        )
    
    if bot_instance.owner_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Check if bot already has an active subscription
    existing_subscription = await SubscriptionCRUD.get_by_bot_instance(
        db, subscription_data.bot_instance_id
    )
    if existing_subscription:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bot instance already has an active subscription"
        )
    
    # Verify plan exists
    plan = await SubscriptionPlanCRUD.get_by_id(db, subscription_data.plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription plan not found"
        )
    
    return await SubscriptionCRUD.create(db, subscription_data, current_user.id)


@router.get("/", response_model=List[Subscription])
async def list_my_subscriptions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List current user's subscriptions."""
    # This would need a new CRUD method to get subscriptions by user
    # For now, we'll get all subscriptions and filter
    all_subs = await SubscriptionCRUD.list_subscriptions(db, skip=0, limit=1000)
    return [sub for sub in all_subs if sub.user_id == current_user.id]


@router.get("/all", response_model=PaginatedResponse)
async def list_all_subscriptions(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    current_admin: User = Depends(require_manage_subscriptions),
    db: AsyncSession = Depends(get_db)
):
    """List all subscriptions (admin only)."""
    skip = (page - 1) * size
    subscriptions = await SubscriptionCRUD.list_subscriptions(db, skip=skip, limit=size)
    
    # Get total count
    total = len(await SubscriptionCRUD.list_subscriptions(db, skip=0, limit=1000))
    
    return PaginatedResponse(
        items=subscriptions,
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size
    )


@router.get("/{subscription_id}", response_model=Subscription)
async def get_subscription(
    subscription_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get subscription by ID."""
    subscription = await SubscriptionCRUD.get_by_id(db, subscription_id)
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )
    
    # Check ownership or admin access
    if subscription.user_id != current_user.id:
        try:
            admin = await get_current_admin()
            if not admin:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied"
                )
        except:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    return subscription


@router.put("/{subscription_id}", response_model=Subscription)
async def update_subscription(
    subscription_id: uuid.UUID,
    subscription_data: SubscriptionUpdate,
    current_admin: User = Depends(require_manage_subscriptions),
    db: AsyncSession = Depends(get_db)
):
    """Update subscription (admin only)."""
    updated_subscription = await SubscriptionCRUD.update(db, subscription_id, subscription_data)
    if not updated_subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )
    return updated_subscription


@router.post("/{subscription_id}/extend")
async def extend_subscription(
    subscription_id: uuid.UUID,
    days: int = Query(..., ge=1, le=365),
    current_admin: User = Depends(require_manage_subscriptions),
    db: AsyncSession = Depends(get_db)
):
    """Extend subscription by specified days (admin only)."""
    extended_subscription = await SubscriptionCRUD.extend_subscription(
        db, subscription_id, days
    )
    if not extended_subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )
    
    return {
        "message": f"Subscription extended by {days} days",
        "new_end_date": extended_subscription.end_at
    }


@router.get("/expiring/reminders")
async def get_expiring_subscriptions(
    days: int = Query(7, ge=1, le=30),
    current_admin: User = Depends(require_manage_subscriptions),
    db: AsyncSession = Depends(get_db)
):
    """Get subscriptions expiring within specified days (admin only)."""
    expiring_subscriptions = await SubscriptionCRUD.get_expiring_subscriptions(db, days)
    return {
        "expiring_subscriptions": expiring_subscriptions,
        "count": len(expiring_subscriptions),
        "days": days
    }


@router.get("/expired/list")
async def get_expired_subscriptions(
    current_admin: User = Depends(require_manage_subscriptions),
    db: AsyncSession = Depends(get_db)
):
    """Get expired subscriptions (admin only)."""
    expired_subscriptions = await SubscriptionCRUD.get_expired_subscriptions(db)
    return {
        "expired_subscriptions": expired_subscriptions,
        "count": len(expired_subscriptions)
    }