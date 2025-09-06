"""Main FastAPI application."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from .config import settings
from .database import engine, Base
from .api import auth, users, bots, subscriptions, payments
from .api.dependencies import get_current_user_or_admin
from .schemas import HealthCheck, MessageResponse
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize Sentry if DSN is provided
if settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        integrations=[
            FastApiIntegration(auto_enabling_instrumentations=False),
            SqlalchemyIntegration(),
        ],
        traces_sample_rate=0.1,
        environment="production" if not settings.debug else "development",
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting Telegram Bot SaaS Platform...")
    
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("Database tables created successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Telegram Bot SaaS Platform...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="A professional Telegram-based SaaS platform for bot deployment",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if settings.debug else ["localhost", "127.0.0.1"]
)


# Rate limiting middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Simple rate limiting middleware."""
    # This is a basic implementation
    # In production, you should use Redis-based rate limiting
    response = await call_next(request)
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    if settings.debug:
        return JSONResponse(
            status_code=500,
            content={"detail": str(exc), "type": type(exc).__name__}
        )
    else:
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )


# Health check endpoint
@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint."""
    try:
        # Check database connection
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        database_status = True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        database_status = False
    
    # Check Redis connection (if implemented)
    redis_status = True  # Placeholder
    
    # Check Docker connection (if implemented)
    docker_status = True  # Placeholder
    
    return HealthCheck(
        status="healthy" if all([database_status, redis_status, docker_status]) else "unhealthy",
        timestamp=datetime.utcnow(),
        version=settings.app_version,
        database=database_status,
        redis=redis_status,
        docker=docker_status
    )


# Root endpoint
@app.get("/", response_model=MessageResponse)
async def root():
    """Root endpoint."""
    return MessageResponse(message=f"Welcome to {settings.app_name} API")


# Include API routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(bots.router, prefix="/api/v1")
app.include_router(subscriptions.router, prefix="/api/v1")
app.include_router(payments.router, prefix="/api/v1")


# Admin endpoints
@app.get("/api/v1/admin/stats")
async def get_admin_stats(
    current_user_or_admin: tuple = Depends(get_current_user_or_admin)
):
    """Get admin statistics."""
    user, admin = current_user_or_admin
    
    if not admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # This would fetch actual statistics from the database
    return {
        "total_users": 0,
        "total_bots": 0,
        "active_subscriptions": 0,
        "pending_payments": 0,
        "system_health": "healthy"
    }


# Webhook endpoint for Telegram bot
@app.post("/api/v1/webhook/telegram")
async def telegram_webhook(request: Request):
    """Telegram webhook endpoint."""
    # This would be handled by the aiogram bot
    # For now, just return success
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info"
    )