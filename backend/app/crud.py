"""Database CRUD operations."""

import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from .models import (
    User, Admin, BotInstance, SubscriptionPlan, Subscription, 
    Payment, BuildLog, SystemSetting, NotificationTemplate
)
from .schemas import (
    UserCreate, UserUpdate, AdminCreate, AdminUpdate,
    BotInstanceCreate, BotInstanceUpdate, SubscriptionPlanCreate, SubscriptionPlanUpdate,
    SubscriptionCreate, SubscriptionUpdate, PaymentCreate, PaymentUpdate,
    BuildLogCreate, SystemSettingCreate, SystemSettingUpdate,
    NotificationTemplateCreate, NotificationTemplateUpdate
)
from .security import encrypt_sensitive_data, decrypt_sensitive_data


# User CRUD operations
class UserCRUD:
    """User CRUD operations."""
    
    @staticmethod
    async def create(db: AsyncSession, user_data: UserCreate) -> User:
        """Create a new user."""
        user = User(**user_data.model_dump())
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    
    @staticmethod
    async def get_by_telegram_id(db: AsyncSession, telegram_user_id: int) -> Optional[User]:
        """Get user by Telegram user ID."""
        result = await db.execute(
            select(User).where(User.telegram_user_id == telegram_user_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: uuid.UUID) -> Optional[User]:
        """Get user by ID."""
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def update(db: AsyncSession, user_id: uuid.UUID, user_data: UserUpdate) -> Optional[User]:
        """Update user."""
        update_data = user_data.model_dump(exclude_unset=True)
        if not update_data:
            return await UserCRUD.get_by_id(db, user_id)
        
        await db.execute(
            update(User)
            .where(User.id == user_id)
            .values(**update_data)
        )
        await db.commit()
        return await UserCRUD.get_by_id(db, user_id)
    
    @staticmethod
    async def delete(db: AsyncSession, user_id: uuid.UUID) -> bool:
        """Delete user."""
        result = await db.execute(
            delete(User).where(User.id == user_id)
        )
        await db.commit()
        return result.rowcount > 0
    
    @staticmethod
    async def list_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
        """List users with pagination."""
        result = await db.execute(
            select(User)
            .offset(skip)
            .limit(limit)
            .order_by(User.created_at.desc())
        )
        return result.scalars().all()


# Admin CRUD operations
class AdminCRUD:
    """Admin CRUD operations."""
    
    @staticmethod
    async def create(db: AsyncSession, admin_data: AdminCreate) -> Admin:
        """Create a new admin."""
        admin = Admin(**admin_data.model_dump())
        db.add(admin)
        await db.commit()
        await db.refresh(admin)
        return admin
    
    @staticmethod
    async def get_by_telegram_id(db: AsyncSession, telegram_user_id: int) -> Optional[Admin]:
        """Get admin by Telegram user ID."""
        result = await db.execute(
            select(Admin).where(Admin.telegram_user_id == telegram_user_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_id(db: AsyncSession, admin_id: uuid.UUID) -> Optional[Admin]:
        """Get admin by ID."""
        result = await db.execute(
            select(Admin).where(Admin.id == admin_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def update(db: AsyncSession, admin_id: uuid.UUID, admin_data: AdminUpdate) -> Optional[Admin]:
        """Update admin."""
        update_data = admin_data.model_dump(exclude_unset=True)
        if not update_data:
            return await AdminCRUD.get_by_id(db, admin_id)
        
        await db.execute(
            update(Admin)
            .where(Admin.id == admin_id)
            .values(**update_data)
        )
        await db.commit()
        return await AdminCRUD.get_by_id(db, admin_id)
    
    @staticmethod
    async def list_admins(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Admin]:
        """List admins with pagination."""
        result = await db.execute(
            select(Admin)
            .offset(skip)
            .limit(limit)
            .order_by(Admin.created_at.desc())
        )
        return result.scalars().all()


# Bot Instance CRUD operations
class BotInstanceCRUD:
    """Bot instance CRUD operations."""
    
    @staticmethod
    async def create(db: AsyncSession, bot_data: BotInstanceCreate, owner_id: uuid.UUID) -> BotInstance:
        """Create a new bot instance."""
        bot_dict = bot_data.model_dump()
        
        # Encrypt sensitive data
        bot_dict["bot_token_encrypted"] = encrypt_sensitive_data(bot_dict.pop("bot_token"))
        if bot_dict.get("github_token"):
            bot_dict["github_token_encrypted"] = encrypt_sensitive_data(bot_dict.pop("github_token"))
        
        bot_dict["owner_user_id"] = owner_id
        bot = BotInstance(**bot_dict)
        db.add(bot)
        await db.commit()
        await db.refresh(bot)
        return bot
    
    @staticmethod
    async def get_by_id(db: AsyncSession, bot_id: uuid.UUID) -> Optional[BotInstance]:
        """Get bot instance by ID."""
        result = await db.execute(
            select(BotInstance)
            .where(BotInstance.id == bot_id)
            .options(selectinload(BotInstance.owner))
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_owner(db: AsyncSession, owner_id: uuid.UUID) -> List[BotInstance]:
        """Get bot instances by owner."""
        result = await db.execute(
            select(BotInstance)
            .where(BotInstance.owner_user_id == owner_id)
            .order_by(BotInstance.created_at.desc())
        )
        return result.scalars().all()
    
    @staticmethod
    async def update(db: AsyncSession, bot_id: uuid.UUID, bot_data: BotInstanceUpdate) -> Optional[BotInstance]:
        """Update bot instance."""
        update_data = bot_data.model_dump(exclude_unset=True)
        
        # Encrypt sensitive data if provided
        if "bot_token" in update_data:
            update_data["bot_token_encrypted"] = encrypt_sensitive_data(update_data.pop("bot_token"))
        if "github_token" in update_data:
            if update_data["github_token"]:
                update_data["github_token_encrypted"] = encrypt_sensitive_data(update_data.pop("github_token"))
            else:
                update_data["github_token_encrypted"] = None
        
        if not update_data:
            return await BotInstanceCRUD.get_by_id(db, bot_id)
        
        await db.execute(
            update(BotInstance)
            .where(BotInstance.id == bot_id)
            .values(**update_data)
        )
        await db.commit()
        return await BotInstanceCRUD.get_by_id(db, bot_id)
    
    @staticmethod
    async def update_status(db: AsyncSession, bot_id: uuid.UUID, status: str, 
                          build_log: Optional[str] = None, error_log: Optional[str] = None) -> Optional[BotInstance]:
        """Update bot instance status."""
        update_data = {"status": status}
        if build_log is not None:
            update_data["build_log"] = build_log
        if error_log is not None:
            update_data["error_log"] = error_log
        
        await db.execute(
            update(BotInstance)
            .where(BotInstance.id == bot_id)
            .values(**update_data)
        )
        await db.commit()
        return await BotInstanceCRUD.get_by_id(db, bot_id)
    
    @staticmethod
    async def delete(db: AsyncSession, bot_id: uuid.UUID) -> bool:
        """Delete bot instance."""
        result = await db.execute(
            delete(BotInstance).where(BotInstance.id == bot_id)
        )
        await db.commit()
        return result.rowcount > 0
    
    @staticmethod
    async def list_bots(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[BotInstance]:
        """List all bot instances with pagination."""
        result = await db.execute(
            select(BotInstance)
            .options(selectinload(BotInstance.owner))
            .offset(skip)
            .limit(limit)
            .order_by(BotInstance.created_at.desc())
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_bots_by_status(db: AsyncSession, status: str) -> List[BotInstance]:
        """Get bot instances by status."""
        result = await db.execute(
            select(BotInstance)
            .where(BotInstance.status == status)
            .options(selectinload(BotInstance.owner))
        )
        return result.scalars().all()


# Subscription Plan CRUD operations
class SubscriptionPlanCRUD:
    """Subscription plan CRUD operations."""
    
    @staticmethod
    async def create(db: AsyncSession, plan_data: SubscriptionPlanCreate) -> SubscriptionPlan:
        """Create a new subscription plan."""
        plan = SubscriptionPlan(**plan_data.model_dump())
        db.add(plan)
        await db.commit()
        await db.refresh(plan)
        return plan
    
    @staticmethod
    async def get_by_id(db: AsyncSession, plan_id: uuid.UUID) -> Optional[SubscriptionPlan]:
        """Get subscription plan by ID."""
        result = await db.execute(
            select(SubscriptionPlan).where(SubscriptionPlan.id == plan_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_active_plans(db: AsyncSession) -> List[SubscriptionPlan]:
        """Get all active subscription plans."""
        result = await db.execute(
            select(SubscriptionPlan)
            .where(SubscriptionPlan.is_active == True)
            .order_by(SubscriptionPlan.duration_days)
        )
        return result.scalars().all()
    
    @staticmethod
    async def update(db: AsyncSession, plan_id: uuid.UUID, plan_data: SubscriptionPlanUpdate) -> Optional[SubscriptionPlan]:
        """Update subscription plan."""
        update_data = plan_data.model_dump(exclude_unset=True)
        if not update_data:
            return await SubscriptionPlanCRUD.get_by_id(db, plan_id)
        
        await db.execute(
            update(SubscriptionPlan)
            .where(SubscriptionPlan.id == plan_id)
            .values(**update_data)
        )
        await db.commit()
        return await SubscriptionPlanCRUD.get_by_id(db, plan_id)
    
    @staticmethod
    async def delete(db: AsyncSession, plan_id: uuid.UUID) -> bool:
        """Delete subscription plan."""
        result = await db.execute(
            delete(SubscriptionPlan).where(SubscriptionPlan.id == plan_id)
        )
        await db.commit()
        return result.rowcount > 0


# Subscription CRUD operations
class SubscriptionCRUD:
    """Subscription CRUD operations."""
    
    @staticmethod
    async def create(db: AsyncSession, subscription_data: SubscriptionCreate, user_id: uuid.UUID) -> Subscription:
        """Create a new subscription."""
        sub_dict = subscription_data.model_dump()
        sub_dict["user_id"] = user_id
        subscription = Subscription(**sub_dict)
        db.add(subscription)
        await db.commit()
        await db.refresh(subscription)
        return subscription
    
    @staticmethod
    async def get_by_id(db: AsyncSession, subscription_id: uuid.UUID) -> Optional[Subscription]:
        """Get subscription by ID."""
        result = await db.execute(
            select(Subscription)
            .where(Subscription.id == subscription_id)
            .options(selectinload(Subscription.bot_instance), selectinload(Subscription.plan))
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_bot_instance(db: AsyncSession, bot_instance_id: uuid.UUID) -> Optional[Subscription]:
        """Get active subscription for bot instance."""
        result = await db.execute(
            select(Subscription)
            .where(
                and_(
                    Subscription.bot_instance_id == bot_instance_id,
                    Subscription.status == "active"
                )
            )
            .options(selectinload(Subscription.plan))
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_expiring_subscriptions(db: AsyncSession, days: int) -> List[Subscription]:
        """Get subscriptions expiring within specified days."""
        cutoff_date = datetime.utcnow() + timedelta(days=days)
        result = await db.execute(
            select(Subscription)
            .where(
                and_(
                    Subscription.status == "active",
                    Subscription.end_at <= cutoff_date,
                    Subscription.end_at > datetime.utcnow()
                )
            )
            .options(selectinload(Subscription.bot_instance), selectinload(Subscription.user))
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_expired_subscriptions(db: AsyncSession) -> List[Subscription]:
        """Get expired subscriptions."""
        result = await db.execute(
            select(Subscription)
            .where(
                and_(
                    Subscription.status == "active",
                    Subscription.end_at < datetime.utcnow()
                )
            )
            .options(selectinload(Subscription.bot_instance), selectinload(Subscription.user))
        )
        return result.scalars().all()
    
    @staticmethod
    async def update(db: AsyncSession, subscription_id: uuid.UUID, subscription_data: SubscriptionUpdate) -> Optional[Subscription]:
        """Update subscription."""
        update_data = subscription_data.model_dump(exclude_unset=True)
        if not update_data:
            return await SubscriptionCRUD.get_by_id(db, subscription_id)
        
        await db.execute(
            update(Subscription)
            .where(Subscription.id == subscription_id)
            .values(**update_data)
        )
        await db.commit()
        return await SubscriptionCRUD.get_by_id(db, subscription_id)
    
    @staticmethod
    async def extend_subscription(db: AsyncSession, subscription_id: uuid.UUID, days: int) -> Optional[Subscription]:
        """Extend subscription by specified days."""
        subscription = await SubscriptionCRUD.get_by_id(db, subscription_id)
        if not subscription:
            return None
        
        new_end_date = max(subscription.end_at, datetime.utcnow()) + timedelta(days=days)
        await db.execute(
            update(Subscription)
            .where(Subscription.id == subscription_id)
            .values(end_at=new_end_date, status="active")
        )
        await db.commit()
        return await SubscriptionCRUD.get_by_id(db, subscription_id)
    
    @staticmethod
    async def list_subscriptions(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Subscription]:
        """List subscriptions with pagination."""
        result = await db.execute(
            select(Subscription)
            .offset(skip)
            .limit(limit)
            .order_by(Subscription.created_at.desc())
        )
        return result.scalars().all()


# Payment CRUD operations
class PaymentCRUD:
    """Payment CRUD operations."""
    
    @staticmethod
    async def create(db: AsyncSession, payment_data: PaymentCreate, user_id: uuid.UUID) -> Payment:
        """Create a new payment."""
        payment_dict = payment_data.model_dump()
        payment_dict["user_id"] = user_id
        payment = Payment(**payment_dict)
        db.add(payment)
        await db.commit()
        await db.refresh(payment)
        return payment
    
    @staticmethod
    async def get_by_id(db: AsyncSession, payment_id: uuid.UUID) -> Optional[Payment]:
        """Get payment by ID."""
        result = await db.execute(
            select(Payment)
            .where(Payment.id == payment_id)
            .options(selectinload(Payment.subscription), selectinload(Payment.user))
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_pending_payments(db: AsyncSession) -> List[Payment]:
        """Get all pending payments."""
        result = await db.execute(
            select(Payment)
            .where(Payment.status == "pending")
            .options(selectinload(Payment.subscription), selectinload(Payment.user))
            .order_by(Payment.created_at.desc())
        )
        return result.scalars().all()
    
    @staticmethod
    async def update(db: AsyncSession, payment_id: uuid.UUID, payment_data: PaymentUpdate, 
                    confirmed_by: Optional[uuid.UUID] = None) -> Optional[Payment]:
        """Update payment."""
        update_data = payment_data.model_dump(exclude_unset=True)
        if not update_data:
            return await PaymentCRUD.get_by_id(db, payment_id)
        
        if confirmed_by:
            update_data["confirmed_by"] = confirmed_by
            update_data["confirmed_at"] = datetime.utcnow()
        
        await db.execute(
            update(Payment)
            .where(Payment.id == payment_id)
            .values(**update_data)
        )
        await db.commit()
        return await PaymentCRUD.get_by_id(db, payment_id)
    
    @staticmethod
    async def confirm_payment(db: AsyncSession, payment_id: uuid.UUID, admin_id: uuid.UUID) -> Optional[Payment]:
        """Confirm a payment."""
        payment = await PaymentCRUD.get_by_id(db, payment_id)
        if not payment:
            return None
        
        # Update payment status
        await db.execute(
            update(Payment)
            .where(Payment.id == payment_id)
            .values(
                status="confirmed",
                confirmed_by=admin_id,
                confirmed_at=datetime.utcnow()
            )
        )
        
        # Extend subscription
        subscription = await SubscriptionCRUD.get_by_id(db, payment.subscription_id)
        if subscription:
            plan = await SubscriptionPlanCRUD.get_by_id(db, subscription.plan_id)
            if plan:
                new_end_date = max(subscription.end_at, datetime.utcnow()) + timedelta(days=plan.duration_days)
                await db.execute(
                    update(Subscription)
                    .where(Subscription.id == subscription.id)
                    .values(end_at=new_end_date, status="active")
                )
        
        await db.commit()
        return await PaymentCRUD.get_by_id(db, payment_id)
    
    @staticmethod
    async def list_payments(db: AsyncSession, skip: int = 0, limit: int = 100, status: Optional[str] = None) -> List[Payment]:
        """List payments with pagination and optional status filter."""
        query = select(Payment)
        if status:
            query = query.where(Payment.status == status)
        
        result = await db.execute(
            query
            .offset(skip)
            .limit(limit)
            .order_by(Payment.created_at.desc())
        )
        return result.scalars().all()


# Build Log CRUD operations
class BuildLogCRUD:
    """Build log CRUD operations."""
    
    @staticmethod
    async def create(db: AsyncSession, log_data: BuildLogCreate) -> BuildLog:
        """Create a new build log entry."""
        log = BuildLog(**log_data.model_dump())
        db.add(log)
        await db.commit()
        await db.refresh(log)
        return log
    
    @staticmethod
    async def get_by_bot_instance(db: AsyncSession, bot_instance_id: uuid.UUID, 
                                limit: int = 100) -> List[BuildLog]:
        """Get build logs for a bot instance."""
        result = await db.execute(
            select(BuildLog)
            .where(BuildLog.bot_instance_id == bot_instance_id)
            .order_by(BuildLog.timestamp.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_recent_logs(db: AsyncSession, limit: int = 100) -> List[BuildLog]:
        """Get recent build logs across all bot instances."""
        result = await db.execute(
            select(BuildLog)
            .order_by(BuildLog.timestamp.desc())
            .limit(limit)
        )
        return result.scalars().all()


# System Setting CRUD operations
class SystemSettingCRUD:
    """System setting CRUD operations."""
    
    @staticmethod
    async def get_by_key(db: AsyncSession, key: str) -> Optional[SystemSetting]:
        """Get system setting by key."""
        result = await db.execute(
            select(SystemSetting).where(SystemSetting.key == key)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_value(db: AsyncSession, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get system setting value by key."""
        setting = await SystemSettingCRUD.get_by_key(db, key)
        if setting:
            return setting.value
        return default
    
    @staticmethod
    async def set_value(db: AsyncSession, key: str, value: str, 
                       description: Optional[str] = None, is_encrypted: bool = False) -> SystemSetting:
        """Set system setting value."""
        setting = await SystemSettingCRUD.get_by_key(db, key)
        if setting:
            await db.execute(
                update(SystemSetting)
                .where(SystemSetting.key == key)
                .values(value=value, description=description, is_encrypted=is_encrypted)
            )
        else:
            setting = SystemSetting(
                key=key,
                value=value,
                description=description,
                is_encrypted=is_encrypted
            )
            db.add(setting)
        
        await db.commit()
        await db.refresh(setting)
        return setting