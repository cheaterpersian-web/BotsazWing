"""Authentication middleware for the bot."""

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User
from typing import Callable, Dict, Any, Awaitable
import structlog
from ..utils.api_client import APIClient

logger = structlog.get_logger()


class AuthMiddleware(BaseMiddleware):
    """Middleware to authenticate users with the backend API."""
    
    def __init__(self):
        """Initialize auth middleware."""
        self.api_client = APIClient()
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """Process authentication for each update."""
        user: User = data.get("event_from_user")
        
        if not user:
            return await handler(event, data)
        
        try:
            # Login user with backend API
            auth_data = await self.api_client.login_user(
                telegram_user_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                language_code=user.language_code or "en"
            )
            
            # Store auth data in context
            data["auth_token"] = auth_data.get("access_token")
            data["user_authenticated"] = True
            
            logger.info("User authenticated", user_id=user.id, username=user.username)
            
        except Exception as e:
            logger.error("Authentication failed", user_id=user.id, error=str(e))
            data["user_authenticated"] = False
            data["auth_error"] = str(e)
        
        return await handler(event, data)