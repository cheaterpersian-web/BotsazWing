"""Database models."""

import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, Numeric, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class User(Base):
    """User model."""
    
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    telegram_user_id = Column(Integer, unique=True, nullable=False, index=True)
    username = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    language_code = Column(String(10), default="en")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    bot_instances = relationship("BotInstance", back_populates="owner", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="user", cascade="all, delete-orphan")


class Admin(Base):
    """Admin model."""
    
    __tablename__ = "admins"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    telegram_user_id = Column(Integer, unique=True, nullable=False, index=True)
    username = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    permissions = Column(JSONB, default={"manage_users": True, "manage_bots": True, "manage_payments": True, "manage_subscriptions": True})
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    confirmed_payments = relationship("Payment", back_populates="confirmed_by_admin")


class BotInstance(Base):
    """Bot instance model."""
    
    __tablename__ = "bot_instances"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    bot_name = Column(String(255), nullable=False)
    bot_token_encrypted = Column(Text, nullable=False)
    github_repo = Column(String(500), nullable=False)
    github_token_encrypted = Column(Text)
    admin_numeric_id = Column(Integer, nullable=False)
    channel_lock_id = Column(Integer)
    container_id = Column(String(255))
    container_name = Column(String(255))
    status = Column(String(50), default="pending", index=True)  # pending, building, running, stopped, error
    build_log = Column(Text)
    error_log = Column(Text)
    last_health_check = Column(DateTime(timezone=True))
    is_healthy = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="bot_instances")
    subscriptions = relationship("Subscription", back_populates="bot_instance", cascade="all, delete-orphan")
    build_logs = relationship("BuildLog", back_populates="bot_instance", cascade="all, delete-orphan")


class SubscriptionPlan(Base):
    """Subscription plan model."""
    
    __tablename__ = "subscription_plans"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    duration_days = Column(Integer, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="USD")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    subscriptions = relationship("Subscription", back_populates="plan")


class Subscription(Base):
    """Subscription model."""
    
    __tablename__ = "subscriptions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bot_instance_id = Column(UUID(as_uuid=True), ForeignKey("bot_instances.id", ondelete="CASCADE"), nullable=False, index=True)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("subscription_plans.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    start_at = Column(DateTime(timezone=True), nullable=False)
    end_at = Column(DateTime(timezone=True), nullable=False, index=True)
    status = Column(String(50), default="active", index=True)  # active, expired, cancelled, suspended
    auto_renew = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    bot_instance = relationship("BotInstance", back_populates="subscriptions")
    plan = relationship("SubscriptionPlan", back_populates="subscriptions")
    user = relationship("User", back_populates="subscriptions")
    payments = relationship("Payment", back_populates="subscription", cascade="all, delete-orphan")


class Payment(Base):
    """Payment model."""
    
    __tablename__ = "payments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="USD")
    payment_method = Column(String(50), nullable=False)  # bank_transfer, crypto
    status = Column(String(50), default="pending", index=True)  # pending, confirmed, rejected, cancelled
    receipt_url = Column(Text)
    transaction_hash = Column(String(255))
    bank_reference = Column(String(255))
    admin_notes = Column(Text)
    confirmed_by = Column(UUID(as_uuid=True), ForeignKey("admins.id"))
    confirmed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    subscription = relationship("Subscription", back_populates="payments")
    user = relationship("User", back_populates="payments")
    confirmed_by_admin = relationship("Admin", back_populates="confirmed_payments")


class BuildLog(Base):
    """Build log model."""
    
    __tablename__ = "build_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bot_instance_id = Column(UUID(as_uuid=True), ForeignKey("bot_instances.id", ondelete="CASCADE"), nullable=False, index=True)
    event = Column(String(255), nullable=False)
    level = Column(String(20), default="info")  # info, warning, error
    message = Column(Text, nullable=False)
    metadata = Column(JSONB)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    bot_instance = relationship("BotInstance", back_populates="build_logs")


class SystemSetting(Base):
    """System setting model."""
    
    __tablename__ = "system_settings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key = Column(String(255), unique=True, nullable=False)
    value = Column(Text, nullable=False)
    description = Column(Text)
    is_encrypted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class NotificationTemplate(Base):
    """Notification template model."""
    
    __tablename__ = "notification_templates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False)
    subject = Column(String(500))
    template = Column(Text, nullable=False)
    variables = Column(JSONB)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())