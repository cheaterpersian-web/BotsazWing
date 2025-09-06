"""Rate limiting middleware for the bot."""

import time
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User
from typing import Callable, Dict, Any, Awaitable
import structlog
from ..config import settings

logger = structlog.get_logger()


class RateLimitMiddleware(BaseMiddleware):
    """Middleware to implement rate limiting."""
    
    def __init__(self, max_requests: int = 10, time_window: int = 60):
        """Initialize rate limit middleware."""
        self.max_requests = max_requests
        self.time_window = time_window
        self.user_requests = {}  # In production, use Redis
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """Process rate limiting for each update."""
        user: User = data.get("event_from_user")
        
        if not user:
            return await handler(event, data)
        
        current_time = time.time()
        user_id = user.id
        
        # Clean old requests
        if user_id in self.user_requests:
            self.user_requests[user_id] = [
                req_time for req_time in self.user_requests[user_id]
                if current_time - req_time < self.time_window
            ]
        else:
            self.user_requests[user_id] = []
        
        # Check rate limit
        if len(self.user_requests[user_id]) >= self.max_requests:
            logger.warning("Rate limit exceeded", user_id=user_id)
            data["rate_limited"] = True
            return  # Skip handler execution
        
        # Add current request
        self.user_requests[user_id].append(current_time)
        data["rate_limited"] = False
        
        return await handler(event, data)