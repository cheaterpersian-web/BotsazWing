"""Pydantic schemas for API requests and responses."""

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict


# Base schemas
class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    
    model_config = ConfigDict(from_attributes=True)


# User schemas
class UserBase(BaseSchema):
    """Base user schema."""
    telegram_user_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    language_code: str = "en"


class UserCreate(UserBase):
    """User creation schema."""
    pass


class UserUpdate(BaseSchema):
    """User update schema."""
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    language_code: Optional[str] = None
    is_active: Optional[bool] = None


class User(UserBase):
    """User response schema."""
    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime


# Admin schemas
class AdminBase(BaseSchema):
    """Base admin schema."""
    telegram_user_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    permissions: Dict[str, bool] = Field(default_factory=lambda: {
        "manage_users": True,
        "manage_bots": True,
        "manage_payments": True,
        "manage_subscriptions": True
    })


class AdminCreate(AdminBase):
    """Admin creation schema."""
    pass


class AdminUpdate(BaseSchema):
    """Admin update schema."""
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    permissions: Optional[Dict[str, bool]] = None
    is_active: Optional[bool] = None


class Admin(AdminBase):
    """Admin response schema."""
    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime


# Bot instance schemas
class BotInstanceBase(BaseSchema):
    """Base bot instance schema."""
    bot_name: str = Field(..., min_length=1, max_length=255)
    bot_token: str = Field(..., min_length=1)
    github_repo: str = Field(..., min_length=1, max_length=500)
    github_token: Optional[str] = None
    admin_numeric_id: int
    channel_lock_id: Optional[int] = None


class BotInstanceCreate(BotInstanceBase):
    """Bot instance creation schema."""
    pass


class BotInstanceUpdate(BaseSchema):
    """Bot instance update schema."""
    bot_name: Optional[str] = Field(None, min_length=1, max_length=255)
    github_repo: Optional[str] = Field(None, min_length=1, max_length=500)
    github_token: Optional[str] = None
    admin_numeric_id: Optional[int] = None
    channel_lock_id: Optional[int] = None


class BotInstance(BotInstanceBase):
    """Bot instance response schema."""
    id: uuid.UUID
    owner_user_id: uuid.UUID
    status: str
    container_id: Optional[str] = None
    container_name: Optional[str] = None
    build_log: Optional[str] = None
    error_log: Optional[str] = None
    last_health_check: Optional[datetime] = None
    is_healthy: bool
    created_at: datetime
    updated_at: datetime
    
    # Exclude sensitive fields
    model_config = ConfigDict(from_attributes=True, exclude={"bot_token_encrypted", "github_token_encrypted"})


# Subscription plan schemas
class SubscriptionPlanBase(BaseSchema):
    """Base subscription plan schema."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    duration_days: int = Field(..., gt=0)
    price: Decimal = Field(..., gt=0)
    currency: str = Field(default="USD", max_length=3)


class SubscriptionPlanCreate(SubscriptionPlanBase):
    """Subscription plan creation schema."""
    pass


class SubscriptionPlanUpdate(BaseSchema):
    """Subscription plan update schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    duration_days: Optional[int] = Field(None, gt=0)
    price: Optional[Decimal] = Field(None, gt=0)
    currency: Optional[str] = Field(None, max_length=3)
    is_active: Optional[bool] = None


class SubscriptionPlan(SubscriptionPlanBase):
    """Subscription plan response schema."""
    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime


# Subscription schemas
class SubscriptionBase(BaseSchema):
    """Base subscription schema."""
    plan_id: uuid.UUID
    start_at: datetime
    end_at: datetime
    auto_renew: bool = False


class SubscriptionCreate(SubscriptionBase):
    """Subscription creation schema."""
    bot_instance_id: uuid.UUID


class SubscriptionUpdate(BaseSchema):
    """Subscription update schema."""
    status: Optional[str] = None
    auto_renew: Optional[bool] = None


class Subscription(SubscriptionBase):
    """Subscription response schema."""
    id: uuid.UUID
    bot_instance_id: uuid.UUID
    user_id: uuid.UUID
    status: str
    created_at: datetime
    updated_at: datetime


# Payment schemas
class PaymentBase(BaseSchema):
    """Base payment schema."""
    subscription_id: uuid.UUID
    amount: Decimal = Field(..., gt=0)
    currency: str = Field(default="USD", max_length=3)
    payment_method: str = Field(..., regex="^(bank_transfer|crypto)$")


class PaymentCreate(PaymentBase):
    """Payment creation schema."""
    transaction_hash: Optional[str] = None
    bank_reference: Optional[str] = None


class PaymentUpdate(BaseSchema):
    """Payment update schema."""
    status: Optional[str] = None
    receipt_url: Optional[str] = None
    transaction_hash: Optional[str] = None
    bank_reference: Optional[str] = None
    admin_notes: Optional[str] = None


class Payment(PaymentBase):
    """Payment response schema."""
    id: uuid.UUID
    user_id: uuid.UUID
    status: str
    receipt_url: Optional[str] = None
    transaction_hash: Optional[str] = None
    bank_reference: Optional[str] = None
    admin_notes: Optional[str] = None
    confirmed_by: Optional[uuid.UUID] = None
    confirmed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


# Build log schemas
class BuildLogBase(BaseSchema):
    """Base build log schema."""
    event: str = Field(..., min_length=1, max_length=255)
    level: str = Field(default="info", regex="^(info|warning|error)$")
    message: str = Field(..., min_length=1)
    metadata: Optional[Dict[str, Any]] = None


class BuildLogCreate(BuildLogBase):
    """Build log creation schema."""
    bot_instance_id: uuid.UUID


class BuildLog(BuildLogBase):
    """Build log response schema."""
    id: uuid.UUID
    bot_instance_id: uuid.UUID
    timestamp: datetime


# System setting schemas
class SystemSettingBase(BaseSchema):
    """Base system setting schema."""
    key: str = Field(..., min_length=1, max_length=255)
    value: str = Field(..., min_length=1)
    description: Optional[str] = None
    is_encrypted: bool = False


class SystemSettingCreate(SystemSettingBase):
    """System setting creation schema."""
    pass


class SystemSettingUpdate(BaseSchema):
    """System setting update schema."""
    value: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
    is_encrypted: Optional[bool] = None


class SystemSetting(SystemSettingBase):
    """System setting response schema."""
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# Notification template schemas
class NotificationTemplateBase(BaseSchema):
    """Base notification template schema."""
    name: str = Field(..., min_length=1, max_length=255)
    subject: Optional[str] = Field(None, max_length=500)
    template: str = Field(..., min_length=1)
    variables: Optional[List[str]] = None


class NotificationTemplateCreate(NotificationTemplateBase):
    """Notification template creation schema."""
    pass


class NotificationTemplateUpdate(BaseSchema):
    """Notification template update schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    subject: Optional[str] = Field(None, max_length=500)
    template: Optional[str] = Field(None, min_length=1)
    variables: Optional[List[str]] = None
    is_active: Optional[bool] = None


class NotificationTemplate(NotificationTemplateBase):
    """Notification template response schema."""
    id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime


# Authentication schemas
class Token(BaseSchema):
    """Token response schema."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseSchema):
    """Token data schema."""
    user_id: Optional[uuid.UUID] = None
    admin_id: Optional[uuid.UUID] = None
    is_admin: bool = False


# Response schemas
class MessageResponse(BaseSchema):
    """Generic message response schema."""
    message: str


class PaginatedResponse(BaseSchema):
    """Paginated response schema."""
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int


# Health check schema
class HealthCheck(BaseSchema):
    """Health check response schema."""
    status: str
    timestamp: datetime
    version: str
    database: bool
    redis: bool
    docker: bool