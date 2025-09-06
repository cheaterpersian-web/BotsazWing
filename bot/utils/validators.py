"""Validation utilities for bot inputs."""

import re
from typing import Optional


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
    valid_patterns = [
        r"^https://github\.com/[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+/?$",
        r"^git@github\.com:[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+\.git$",
        r"^github\.com/[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+/?$"
    ]
    
    return any(re.match(pattern, repo_url) for pattern in valid_patterns)


def validate_github_token(token: str) -> bool:
    """Validate GitHub token format."""
    if not token:
        return True  # Optional field
    
    # GitHub tokens are typically 40 characters for personal access tokens
    # or start with 'ghp_' for newer tokens
    if len(token) == 40 and token.isalnum():
        return True
    
    if token.startswith('ghp_') and len(token) > 40:
        return True
    
    return False


def validate_admin_id(admin_id: str) -> Optional[int]:
    """Validate admin numeric ID."""
    try:
        admin_id_int = int(admin_id)
        if admin_id_int > 0:
            return admin_id_int
    except ValueError:
        pass
    return None


def validate_channel_id(channel_id: str) -> Optional[int]:
    """Validate channel ID."""
    if not channel_id:
        return None  # Optional field
    
    try:
        channel_id_int = int(channel_id)
        # Channel IDs are typically negative for groups/channels
        if channel_id_int < 0:
            return channel_id_int
    except ValueError:
        pass
    return None


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


def validate_payment_amount(amount: str) -> Optional[float]:
    """Validate payment amount."""
    try:
        amount_float = float(amount)
        if amount_float > 0:
            return amount_float
    except ValueError:
        pass
    return None


def validate_transaction_hash(tx_hash: str) -> bool:
    """Validate cryptocurrency transaction hash."""
    if not tx_hash:
        return False
    
    # Basic validation for common crypto transaction hashes
    # Bitcoin: 64 hex characters
    # Ethereum: 66 hex characters (0x + 64 hex)
    if len(tx_hash) == 64 and all(c in '0123456789abcdefABCDEF' for c in tx_hash):
        return True
    
    if len(tx_hash) == 66 and tx_hash.startswith('0x') and all(c in '0123456789abcdefABCDEF' for c in tx_hash[2:]):
        return True
    
    return False


def validate_bank_reference(reference: str) -> bool:
    """Validate bank transfer reference."""
    if not reference:
        return False
    
    # Bank references should be alphanumeric and reasonable length
    if len(reference) < 3 or len(reference) > 50:
        return False
    
    return all(c.isalnum() or c in '-_' for c in reference)