"""Main Telegram bot application."""

import asyncio
import logging
import structlog
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from .config import settings
from .middleware.auth_middleware import AuthMiddleware
from .middleware.rate_limit_middleware import RateLimitMiddleware
from .handlers import start, bots, payments, plans, help

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


async def create_bot() -> Bot:
    """Create and configure bot instance."""
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    # Test bot token
    try:
        bot_info = await bot.get_me()
        logger.info("Bot initialized successfully", bot_username=bot_info.username)
    except Exception as e:
        logger.error("Failed to initialize bot", error=str(e))
        raise
    
    return bot


async def create_dispatcher() -> Dispatcher:
    """Create and configure dispatcher."""
    # Create Redis storage for FSM
    storage = RedisStorage.from_url(settings.redis_url)
    dp = Dispatcher(storage=storage)
    
    # Add middleware
    dp.message.middleware(AuthMiddleware())
    dp.callback_query.middleware(AuthMiddleware())
    dp.message.middleware(RateLimitMiddleware())
    dp.callback_query.middleware(RateLimitMiddleware())
    
    # Include routers
    dp.include_router(start.router)
    dp.include_router(bots.router)
    dp.include_router(payments.router)
    dp.include_router(plans.router)
    dp.include_router(help.router)
    
    return dp


async def on_startup(bot: Bot, webhook_url: str = None):
    """Bot startup handler."""
    logger.info("Bot starting up...")
    
    if webhook_url:
        # Set webhook for production
        await bot.set_webhook(
            url=webhook_url,
            drop_pending_updates=True
        )
        logger.info("Webhook set", webhook_url=webhook_url)
    else:
        # Delete webhook for development
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Webhook deleted for development mode")


async def on_shutdown(bot: Bot):
    """Bot shutdown handler."""
    logger.info("Bot shutting down...")
    await bot.delete_webhook()
    await bot.session.close()


async def create_webhook_app() -> web.Application:
    """Create webhook application."""
    bot = await create_bot()
    dp = await create_dispatcher()
    
    # Create webhook URL
    webhook_url = f"{settings.webhook_url}/webhook/{settings.bot_token}"
    
    # Setup startup and shutdown handlers
    dp.startup.register(lambda: on_startup(bot, webhook_url))
    dp.shutdown.register(lambda: on_shutdown(bot))
    
    # Create web application
    app = web.Application()
    
    # Setup webhook handler
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    webhook_requests_handler.register(app, path=f"/webhook/{settings.bot_token}")
    
    # Setup application
    setup_application(app, dp, bot=bot)
    
    return app


async def run_polling():
    """Run bot in polling mode (development)."""
    bot = await create_bot()
    dp = await create_dispatcher()
    
    # Setup startup and shutdown handlers
    dp.startup.register(lambda: on_startup(bot))
    dp.shutdown.register(lambda: on_shutdown(bot))
    
    try:
        logger.info("Starting bot in polling mode...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error("Error in polling mode", error=str(e))
        raise
    finally:
        await bot.session.close()


async def run_webhook():
    """Run bot in webhook mode (production)."""
    app = await create_webhook_app()
    
    logger.info("Starting webhook server...")
    return app


def main():
    """Main entry point."""
    if settings.webhook_url:
        # Production mode with webhook
        app = asyncio.run(run_webhook())
        web.run_app(
            app,
            host="0.0.0.0",
            port=settings.webhook_port
        )
    else:
        # Development mode with polling
        asyncio.run(run_polling())


if __name__ == "__main__":
    main()