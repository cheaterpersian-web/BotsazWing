"""Security utilities for authentication and encryption."""

import uuid
from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet
from fastapi import HTTPException, status
from .config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
ALGORITHM = settings.algorithm
SECRET_KEY = settings.secret_key
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

# Encryption
fernet = Fernet(settings.encryption_key.encode())


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def encrypt_sensitive_data(data: str) -> str:
    """Encrypt sensitive data like tokens."""
    if not data:
        return data
    return fernet.encrypt(data.encode()).decode()


def decrypt_sensitive_data(encrypted_data: str) -> str:
    """Decrypt sensitive data like tokens."""
    if not encrypted_data:
        return encrypted_data
    try:
        return fernet.decrypt(encrypted_data.encode()).decode()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to decrypt sensitive data"
        )


def generate_reference_code() -> str:
    """Generate a unique reference code for payments."""
    return f"TB{datetime.utcnow().strftime('%Y%m%d')}{uuid.uuid4().hex[:8].upper()}"


def validate_telegram_user_id(user_id: int) -> bool:
    """Validate Telegram user ID format."""
    return isinstance(user_id, int) and user_id > 0


def validate_bot_token(token: str) -> bool:
    """Validate Telegram bot token format."""
    if not token:
        return False
    
    # Basic format validation: should be like "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
    parts = token.split(":")
    if len(parts) != 2:
        return False
    
    try:
        bot_id = int(parts[0])
        return bot_id > 0 and len(parts[1]) > 0
    except ValueError:
        return False


def validate_github_repo(repo_url: str) -> bool:
    """Validate GitHub repository URL format."""
    if not repo_url:
        return False
    
    # Accept both HTTPS and SSH formats
    valid_prefixes = [
        "https://github.com/",
        "git@github.com:",
        "github.com/"
    ]
    
    return any(repo_url.startswith(prefix) for prefix in valid_prefixes)


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """Sanitize user input to prevent injection attacks."""
    if not text:
        return ""
    
    # Remove potentially dangerous characters
    dangerous_chars = ["<", ">", '"', "'", "&", ";", "|", "`", "$", "(", ")", "{", "}"]
    sanitized = text
    
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, "")
    
    # Truncate if too long
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized.strip()


def generate_container_name(user_id: uuid.UUID, bot_name: str) -> str:
    """Generate a unique container name for a bot instance."""
    # Sanitize bot name for container naming
    safe_name = "".join(c for c in bot_name if c.isalnum() or c in "-_").lower()
    safe_name = safe_name[:20]  # Limit length
    
    # Add user ID prefix and timestamp for uniqueness
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    return f"telegram-bot-{user_id.hex[:8]}-{safe_name}-{timestamp}"


def is_admin_user(telegram_user_id: int) -> bool:
    """Check if a Telegram user ID is an admin."""
    # This would typically check against the database
    # For now, we'll use a simple check against environment variable
    admin_ids = settings.secret_key.split(",")  # This is a placeholder
    return str(telegram_user_id) in admin_ids


def rate_limit_key(identifier: Union[str, int]) -> str:
    """Generate a rate limit key for Redis."""
    return f"rate_limit:{identifier}"


def get_client_ip(request) -> str:
    """Extract client IP address from request."""
    # Check for forwarded headers first (for reverse proxy setups)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fallback to direct connection
    return request.client.host if request.client else "unknown"