"""Bot deployment service."""

import asyncio
import logging
import os
import shutil
import tempfile
from typing import Optional, Dict, Any
import git
from ..config import settings
from ..database import AsyncSessionLocal
from ..crud import BotInstanceCRUD, BuildLogCRUD
from ..security import decrypt_sensitive_data, generate_container_name
from .docker_service import DockerService

logger = logging.getLogger(__name__)


class DeploymentService:
    """Service for deploying bot instances."""
    
    def __init__(self):
        """Initialize deployment service."""
        self.docker_service = DockerService()
        self.temp_dir = "/tmp/telegram-bot-deployments"
        self._ensure_temp_dir()
    
    def _ensure_temp_dir(self):
        """Ensure temporary directory exists."""
        os.makedirs(self.temp_dir, exist_ok=True)
    
    @staticmethod
    async def deploy_bot(
        bot_instance_id: str,
        bot_token: str,
        github_repo: str,
        github_token: Optional[str] = None,
        admin_numeric_id: int = None,
        channel_lock_id: Optional[int] = None
    ):
        """Deploy a bot instance."""
        deployment_service = DeploymentService()
        await deployment_service._deploy_bot_async(
            bot_instance_id, bot_token, github_repo, github_token,
            admin_numeric_id, channel_lock_id
        )
    
    async def _deploy_bot_async(
        self,
        bot_instance_id: str,
        bot_token: str,
        github_repo: str,
        github_token: Optional[str] = None,
        admin_numeric_id: int = None,
        channel_lock_id: Optional[int] = None
    ):
        """Async bot deployment process."""
        async with AsyncSessionLocal() as db:
            try:
                # Update bot status to building
                await BotInstanceCRUD.update_status(db, bot_instance_id, "building")
                await BuildLogCRUD.create(db, BuildLogCreate(
                    bot_instance_id=bot_instance_id,
                    event="build_started",
                    level="info",
                    message="Starting bot deployment process"
                ))
                
                # Clone repository
                repo_path = await self._clone_repository(github_repo, github_token, bot_instance_id)
                
                # Prepare environment variables
                env_vars = self._prepare_environment_variables(
                    bot_token, admin_numeric_id, channel_lock_id
                )
                
                # Build Docker image
                image_name = f"telegram-bot-{bot_instance_id}"
                await self._build_docker_image(repo_path, image_name, env_vars, bot_instance_id)
                
                # Create and start container
                container_name = generate_container_name(bot_instance_id, f"bot-{bot_instance_id}")
                container_id = await self._create_and_start_container(
                    image_name, container_name, env_vars, bot_instance_id
                )
                
                # Update bot instance with container info
                await BotInstanceCRUD.update_status(
                    db, bot_instance_id, "running",
                    build_log="Deployment completed successfully"
                )
                
                await BuildLogCRUD.create(db, BuildLogCreate(
                    bot_instance_id=bot_instance_id,
                    event="deployment_completed",
                    level="info",
                    message="Bot deployed and started successfully"
                ))
                
                logger.info(f"Successfully deployed bot {bot_instance_id}")
                
            except Exception as e:
                logger.error(f"Failed to deploy bot {bot_instance_id}: {e}")
                
                # Update bot status to error
                await BotInstanceCRUD.update_status(
                    db, bot_instance_id, "error",
                    error_log=str(e)
                )
                
                await BuildLogCRUD.create(db, BuildLogCreate(
                    bot_instance_id=bot_instance_id,
                    event="deployment_failed",
                    level="error",
                    message=f"Deployment failed: {str(e)}"
                ))
                
                # Cleanup on failure
                await self._cleanup_failed_deployment(bot_instance_id)
    
    async def _clone_repository(self, github_repo: str, github_token: Optional[str], 
                               bot_instance_id: str) -> str:
        """Clone GitHub repository."""
        try:
            # Create unique directory for this deployment
            repo_dir = os.path.join(self.temp_dir, f"repo-{bot_instance_id}")
            
            if os.path.exists(repo_dir):
                shutil.rmtree(repo_dir)
            
            # Prepare repository URL
            if github_token:
                # For private repositories
                if github_repo.startswith("https://github.com/"):
                    repo_url = github_repo.replace(
                        "https://github.com/",
                        f"https://{github_token}@github.com/"
                    )
                else:
                    repo_url = github_repo
            else:
                repo_url = github_repo
            
            # Clone repository
            logger.info(f"Cloning repository {github_repo} to {repo_dir}")
            repo = git.Repo.clone_from(repo_url, repo_dir)
            
            return repo_dir
            
        except Exception as e:
            logger.error(f"Failed to clone repository {github_repo}: {e}")
            raise
    
    def _prepare_environment_variables(
        self, bot_token: str, admin_numeric_id: int, 
        channel_lock_id: Optional[int] = None
    ) -> Dict[str, str]:
        """Prepare environment variables for the bot."""
        env_vars = {
            "BOT_TOKEN": bot_token,
            "ADMIN_NUMERIC_ID": str(admin_numeric_id),
            "ENVIRONMENT": "production"
        }
        
        if channel_lock_id:
            env_vars["CHANNEL_LOCK_ID"] = str(channel_lock_id)
        
        return env_vars
    
    async def _build_docker_image(self, repo_path: str, image_name: str, 
                                 env_vars: Dict[str, str], bot_instance_id: str):
        """Build Docker image for the bot."""
        try:
            # Check if Dockerfile exists
            dockerfile_path = os.path.join(repo_path, "Dockerfile")
            if not os.path.exists(dockerfile_path):
                # Create a default Dockerfile if none exists
                await self._create_default_dockerfile(repo_path)
            
            # Build image
            logger.info(f"Building Docker image {image_name}")
            await self.docker_service.build_image(repo_path, image_name)
            
            await BuildLogCRUD.create(AsyncSessionLocal(), BuildLogCreate(
                bot_instance_id=bot_instance_id,
                event="image_built",
                level="info",
                message=f"Docker image {image_name} built successfully"
            ))
            
        except Exception as e:
            logger.error(f"Failed to build Docker image {image_name}: {e}")
            raise
    
    async def _create_default_dockerfile(self, repo_path: str):
        """Create a default Dockerfile if none exists."""
        dockerfile_content = """
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    git \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash bot
RUN chown -R bot:bot /app
USER bot

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run the bot
CMD ["python", "main.py"]
"""
        
        dockerfile_path = os.path.join(repo_path, "Dockerfile")
        with open(dockerfile_path, "w") as f:
            f.write(dockerfile_content.strip())
        
        # Also create a default requirements.txt if it doesn't exist
        requirements_path = os.path.join(repo_path, "requirements.txt")
        if not os.path.exists(requirements_path):
            with open(requirements_path, "w") as f:
                f.write("aiogram==3.1.1\npython-dotenv==1.0.0\n")
    
    async def _create_and_start_container(self, image_name: str, container_name: str,
                                         env_vars: Dict[str, str], bot_instance_id: str) -> str:
        """Create and start Docker container."""
        try:
            # Create container
            container_id = await self.docker_service.create_container(
                image_name=image_name,
                container_name=container_name,
                environment=env_vars
            )
            
            # Start container
            await self.docker_service.start_container(container_name)
            
            # Update bot instance with container info
            async with AsyncSessionLocal() as db:
                await BotInstanceCRUD.update_status(
                    db, bot_instance_id, "running",
                    build_log="Container created and started successfully"
                )
            
            await BuildLogCRUD.create(AsyncSessionLocal(), BuildLogCreate(
                bot_instance_id=bot_instance_id,
                event="container_started",
                level="info",
                message=f"Container {container_name} started successfully"
            ))
            
            return container_id
            
        except Exception as e:
            logger.error(f"Failed to create/start container {container_name}: {e}")
            raise
    
    async def _cleanup_failed_deployment(self, bot_instance_id: str):
        """Clean up resources after failed deployment."""
        try:
            # Remove temporary repository directory
            repo_dir = os.path.join(self.temp_dir, f"repo-{bot_instance_id}")
            if os.path.exists(repo_dir):
                shutil.rmtree(repo_dir)
            
            # Remove any created Docker images
            image_name = f"telegram-bot-{bot_instance_id}"
            try:
                # This would require additional Docker API calls to remove images
                pass
            except Exception as e:
                logger.warning(f"Failed to cleanup Docker image {image_name}: {e}")
            
        except Exception as e:
            logger.error(f"Failed to cleanup failed deployment for {bot_instance_id}: {e}")
    
    async def redeploy_bot(self, bot_instance_id: str):
        """Redeploy an existing bot instance."""
        async with AsyncSessionLocal() as db:
            bot_instance = await BotInstanceCRUD.get_by_id(db, bot_instance_id)
            if not bot_instance:
                raise ValueError(f"Bot instance {bot_instance_id} not found")
            
            # Stop existing container if running
            if bot_instance.container_id:
                try:
                    await self.docker_service.stop_container(bot_instance.container_id)
                    await self.docker_service.remove_container(bot_instance.container_id)
                except Exception as e:
                    logger.warning(f"Failed to stop existing container: {e}")
            
            # Decrypt sensitive data
            bot_token = decrypt_sensitive_data(bot_instance.bot_token_encrypted)
            github_token = None
            if bot_instance.github_token_encrypted:
                github_token = decrypt_sensitive_data(bot_instance.github_token_encrypted)
            
            # Redeploy
            await self._deploy_bot_async(
                bot_instance_id, bot_token, bot_instance.github_repo,
                github_token, bot_instance.admin_numeric_id, bot_instance.channel_lock_id
            )
    
    async def stop_bot(self, bot_instance_id: str):
        """Stop a bot instance."""
        async with AsyncSessionLocal() as db:
            bot_instance = await BotInstanceCRUD.get_by_id(db, bot_instance_id)
            if not bot_instance:
                raise ValueError(f"Bot instance {bot_instance_id} not found")
            
            if bot_instance.container_id:
                try:
                    await self.docker_service.stop_container(bot_instance.container_id)
                    await BotInstanceCRUD.update_status(db, bot_instance_id, "stopped")
                    
                    await BuildLogCRUD.create(db, BuildLogCreate(
                        bot_instance_id=bot_instance_id,
                        event="container_stopped",
                        level="info",
                        message="Bot container stopped successfully"
                    ))
                    
                except Exception as e:
                    logger.error(f"Failed to stop bot {bot_instance_id}: {e}")
                    await BotInstanceCRUD.update_status(
                        db, bot_instance_id, "error",
                        error_log=f"Failed to stop container: {str(e)}"
                    )
    
    async def get_bot_logs(self, bot_instance_id: str, tail: int = 100) -> str:
        """Get logs for a bot instance."""
        async with AsyncSessionLocal() as db:
            bot_instance = await BotInstanceCRUD.get_by_id(db, bot_instance_id)
            if not bot_instance or not bot_instance.container_id:
                return ""
            
            try:
                return await self.docker_service.get_container_logs(
                    bot_instance.container_id, tail
                )
            except Exception as e:
                logger.error(f"Failed to get logs for bot {bot_instance_id}: {e}")
                return ""