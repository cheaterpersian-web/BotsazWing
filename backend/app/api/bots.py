"""Bot instance management API endpoints."""

import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..crud import BotInstanceCRUD, UserCRUD
from ..schemas import BotInstance, BotInstanceCreate, BotInstanceUpdate, PaginatedResponse
from ..api.dependencies import get_current_user, get_current_admin, require_manage_bots
from ..services.docker_service import DockerService
from ..services.deployment_service import DeploymentService
from ..schemas import User

router = APIRouter(prefix="/bots", tags=["bot-instances"])


@router.post("/", response_model=BotInstance)
async def create_bot_instance(
    bot_data: BotInstanceCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new bot instance."""
    # Check if user has reached bot limit
    user_bots = await BotInstanceCRUD.get_by_owner(db, current_user.id)
    max_bots = 10  # This should come from system settings
    
    if len(user_bots) >= max_bots:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum number of bots ({max_bots}) reached"
        )
    
    # Create bot instance
    bot_instance = await BotInstanceCRUD.create(db, bot_data, current_user.id)
    
    # Start deployment in background
    background_tasks.add_task(
        DeploymentService.deploy_bot,
        bot_instance.id,
        bot_data.bot_token,
        bot_data.github_repo,
        bot_data.github_token,
        bot_data.admin_numeric_id,
        bot_data.channel_lock_id
    )
    
    return bot_instance


@router.get("/", response_model=List[BotInstance])
async def list_my_bots(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List current user's bot instances."""
    return await BotInstanceCRUD.get_by_owner(db, current_user.id)


@router.get("/all", response_model=PaginatedResponse)
async def list_all_bots(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    current_admin: User = Depends(require_manage_bots),
    db: AsyncSession = Depends(get_db)
):
    """List all bot instances (admin only)."""
    skip = (page - 1) * size
    bots = await BotInstanceCRUD.list_bots(db, skip=skip, limit=size)
    
    # Get total count
    total = len(await BotInstanceCRUD.list_bots(db, skip=0, limit=1000))  # Simplified for demo
    
    return PaginatedResponse(
        items=bots,
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size
    )


@router.get("/{bot_id}", response_model=BotInstance)
async def get_bot_instance(
    bot_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get bot instance by ID."""
    bot_instance = await BotInstanceCRUD.get_by_id(db, bot_id)
    if not bot_instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bot instance not found"
        )
    
    # Check ownership or admin access
    if bot_instance.owner_user_id != current_user.id:
        # Check if current user is admin
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
    
    return bot_instance


@router.put("/{bot_id}", response_model=BotInstance)
async def update_bot_instance(
    bot_id: uuid.UUID,
    bot_update: BotInstanceUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update bot instance."""
    bot_instance = await BotInstanceCRUD.get_by_id(db, bot_id)
    if not bot_instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bot instance not found"
        )
    
    # Check ownership
    if bot_instance.owner_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Don't allow updates if bot is running
    if bot_instance.status == "running":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update running bot instance"
        )
    
    updated_bot = await BotInstanceCRUD.update(db, bot_id, bot_update)
    return updated_bot


@router.delete("/{bot_id}")
async def delete_bot_instance(
    bot_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete bot instance."""
    bot_instance = await BotInstanceCRUD.get_by_id(db, bot_id)
    if not bot_instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bot instance not found"
        )
    
    # Check ownership
    if bot_instance.owner_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Stop container if running
    if bot_instance.container_id:
        docker_service = DockerService()
        try:
            await docker_service.stop_container(bot_instance.container_id)
        except Exception as e:
            # Log error but continue with deletion
            pass
    
    success = await BotInstanceCRUD.delete(db, bot_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bot instance not found"
        )
    
    return {"message": "Bot instance deleted successfully"}


@router.post("/{bot_id}/start")
async def start_bot_instance(
    bot_id: uuid.UUID,
    current_admin: User = Depends(require_manage_bots),
    db: AsyncSession = Depends(get_db)
):
    """Start bot instance (admin only)."""
    bot_instance = await BotInstanceCRUD.get_by_id(db, bot_id)
    if not bot_instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bot instance not found"
        )
    
    if bot_instance.status == "running":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bot instance is already running"
        )
    
    # Start container
    docker_service = DockerService()
    try:
        container_id = await docker_service.start_container(bot_instance.container_name)
        await BotInstanceCRUD.update_status(db, bot_id, "running")
        return {"message": "Bot instance started successfully", "container_id": container_id}
    except Exception as e:
        await BotInstanceCRUD.update_status(db, bot_id, "error", error_log=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start bot instance: {str(e)}"
        )


@router.post("/{bot_id}/stop")
async def stop_bot_instance(
    bot_id: uuid.UUID,
    current_admin: User = Depends(require_manage_bots),
    db: AsyncSession = Depends(get_db)
):
    """Stop bot instance (admin only)."""
    bot_instance = await BotInstanceCRUD.get_by_id(db, bot_id)
    if not bot_instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bot instance not found"
        )
    
    if bot_instance.status != "running":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bot instance is not running"
        )
    
    # Stop container
    docker_service = DockerService()
    try:
        await docker_service.stop_container(bot_instance.container_id)
        await BotInstanceCRUD.update_status(db, bot_id, "stopped")
        return {"message": "Bot instance stopped successfully"}
    except Exception as e:
        await BotInstanceCRUD.update_status(db, bot_id, "error", error_log=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop bot instance: {str(e)}"
        )


@router.post("/{bot_id}/restart")
async def restart_bot_instance(
    bot_id: uuid.UUID,
    current_admin: User = Depends(require_manage_bots),
    db: AsyncSession = Depends(get_db)
):
    """Restart bot instance (admin only)."""
    bot_instance = await BotInstanceCRUD.get_by_id(db, bot_id)
    if not bot_instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bot instance not found"
        )
    
    # Restart container
    docker_service = DockerService()
    try:
        await docker_service.restart_container(bot_instance.container_id)
        await BotInstanceCRUD.update_status(db, bot_id, "running")
        return {"message": "Bot instance restarted successfully"}
    except Exception as e:
        await BotInstanceCRUD.update_status(db, bot_id, "error", error_log=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to restart bot instance: {str(e)}"
        )