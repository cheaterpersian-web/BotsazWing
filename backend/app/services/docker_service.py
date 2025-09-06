"""Docker service for container management."""

import asyncio
import logging
from typing import Optional, Dict, Any
import docker
from docker.errors import DockerException, ContainerError, ImageNotFound
from ..config import settings

logger = logging.getLogger(__name__)


class DockerService:
    """Service for managing Docker containers."""
    
    def __init__(self):
        """Initialize Docker client."""
        try:
            self.client = docker.from_env()
            self.network_name = settings.docker_network
            self._ensure_network_exists()
        except DockerException as e:
            logger.error(f"Failed to initialize Docker client: {e}")
            raise
    
    def _ensure_network_exists(self):
        """Ensure the Docker network exists."""
        try:
            networks = self.client.networks.list()
            network_names = [net.name for net in networks]
            
            if self.network_name not in network_names:
                self.client.networks.create(
                    self.network_name,
                    driver="bridge",
                    check_duplicate=True
                )
                logger.info(f"Created Docker network: {self.network_name}")
        except DockerException as e:
            logger.error(f"Failed to create network {self.network_name}: {e}")
            raise
    
    async def build_image(self, dockerfile_path: str, image_name: str, 
                         build_args: Optional[Dict[str, str]] = None) -> str:
        """Build Docker image from Dockerfile."""
        try:
            logger.info(f"Building image {image_name} from {dockerfile_path}")
            
            # Run build in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            image, build_logs = await loop.run_in_executor(
                None,
                self._build_image_sync,
                dockerfile_path,
                image_name,
                build_args
            )
            
            logger.info(f"Successfully built image {image_name}")
            return image.id
            
        except Exception as e:
            logger.error(f"Failed to build image {image_name}: {e}")
            raise
    
    def _build_image_sync(self, dockerfile_path: str, image_name: str, 
                         build_args: Optional[Dict[str, str]] = None):
        """Synchronous image building."""
        return self.client.images.build(
            path=dockerfile_path,
            tag=image_name,
            buildargs=build_args or {},
            rm=True,
            forcerm=True
        )
    
    async def create_container(self, image_name: str, container_name: str,
                              environment: Optional[Dict[str, str]] = None,
                              ports: Optional[Dict[str, str]] = None) -> str:
        """Create Docker container."""
        try:
            logger.info(f"Creating container {container_name} from image {image_name}")
            
            # Run container creation in thread pool
            loop = asyncio.get_event_loop()
            container = await loop.run_in_executor(
                None,
                self._create_container_sync,
                image_name,
                container_name,
                environment,
                ports
            )
            
            logger.info(f"Successfully created container {container_name}")
            return container.id
            
        except Exception as e:
            logger.error(f"Failed to create container {container_name}: {e}")
            raise
    
    def _create_container_sync(self, image_name: str, container_name: str,
                              environment: Optional[Dict[str, str]] = None,
                              ports: Optional[Dict[str, str]] = None):
        """Synchronous container creation."""
        container = self.client.containers.create(
            image=image_name,
            name=container_name,
            environment=environment or {},
            ports=ports or {},
            network=self.network_name,
            detach=True,
            restart_policy={"Name": "unless-stopped"}
        )
        return container
    
    async def start_container(self, container_name: str) -> str:
        """Start Docker container."""
        try:
            logger.info(f"Starting container {container_name}")
            
            # Run container start in thread pool
            loop = asyncio.get_event_loop()
            container = await loop.run_in_executor(
                None,
                self._start_container_sync,
                container_name
            )
            
            logger.info(f"Successfully started container {container_name}")
            return container.id
            
        except Exception as e:
            logger.error(f"Failed to start container {container_name}: {e}")
            raise
    
    def _start_container_sync(self, container_name: str):
        """Synchronous container start."""
        container = self.client.containers.get(container_name)
        container.start()
        return container
    
    async def stop_container(self, container_id: str) -> bool:
        """Stop Docker container."""
        try:
            logger.info(f"Stopping container {container_id}")
            
            # Run container stop in thread pool
            loop = asyncio.get_event_loop()
            success = await loop.run_in_executor(
                None,
                self._stop_container_sync,
                container_id
            )
            
            logger.info(f"Successfully stopped container {container_id}")
            return success
            
        except Exception as e:
            logger.error(f"Failed to stop container {container_id}: {e}")
            raise
    
    def _stop_container_sync(self, container_id: str) -> bool:
        """Synchronous container stop."""
        try:
            container = self.client.containers.get(container_id)
            container.stop(timeout=10)
            return True
        except ContainerError:
            return False
    
    async def restart_container(self, container_id: str) -> bool:
        """Restart Docker container."""
        try:
            logger.info(f"Restarting container {container_id}")
            
            # Run container restart in thread pool
            loop = asyncio.get_event_loop()
            success = await loop.run_in_executor(
                None,
                self._restart_container_sync,
                container_id
            )
            
            logger.info(f"Successfully restarted container {container_id}")
            return success
            
        except Exception as e:
            logger.error(f"Failed to restart container {container_id}: {e}")
            raise
    
    def _restart_container_sync(self, container_id: str) -> bool:
        """Synchronous container restart."""
        try:
            container = self.client.containers.get(container_id)
            container.restart(timeout=10)
            return True
        except ContainerError:
            return False
    
    async def remove_container(self, container_id: str, force: bool = False) -> bool:
        """Remove Docker container."""
        try:
            logger.info(f"Removing container {container_id}")
            
            # Run container removal in thread pool
            loop = asyncio.get_event_loop()
            success = await loop.run_in_executor(
                None,
                self._remove_container_sync,
                container_id,
                force
            )
            
            logger.info(f"Successfully removed container {container_id}")
            return success
            
        except Exception as e:
            logger.error(f"Failed to remove container {container_id}: {e}")
            raise
    
    def _remove_container_sync(self, container_id: str, force: bool = False) -> bool:
        """Synchronous container removal."""
        try:
            container = self.client.containers.get(container_id)
            container.remove(force=force)
            return True
        except ContainerError:
            return False
    
    async def get_container_status(self, container_id: str) -> Optional[str]:
        """Get container status."""
        try:
            # Run container status check in thread pool
            loop = asyncio.get_event_loop()
            status = await loop.run_in_executor(
                None,
                self._get_container_status_sync,
                container_id
            )
            return status
            
        except Exception as e:
            logger.error(f"Failed to get container status {container_id}: {e}")
            return None
    
    def _get_container_status_sync(self, container_id: str) -> Optional[str]:
        """Synchronous container status check."""
        try:
            container = self.client.containers.get(container_id)
            return container.status
        except ContainerError:
            return None
    
    async def get_container_logs(self, container_id: str, tail: int = 100) -> str:
        """Get container logs."""
        try:
            # Run container logs retrieval in thread pool
            loop = asyncio.get_event_loop()
            logs = await loop.run_in_executor(
                None,
                self._get_container_logs_sync,
                container_id,
                tail
            )
            return logs
            
        except Exception as e:
            logger.error(f"Failed to get container logs {container_id}: {e}")
            return ""
    
    def _get_container_logs_sync(self, container_id: str, tail: int = 100) -> str:
        """Synchronous container logs retrieval."""
        try:
            container = self.client.containers.get(container_id)
            return container.logs(tail=tail).decode('utf-8')
        except ContainerError:
            return ""
    
    async def list_containers(self, all_containers: bool = False) -> list:
        """List Docker containers."""
        try:
            # Run container listing in thread pool
            loop = asyncio.get_event_loop()
            containers = await loop.run_in_executor(
                None,
                self._list_containers_sync,
                all_containers
            )
            return containers
            
        except Exception as e:
            logger.error(f"Failed to list containers: {e}")
            return []
    
    def _list_containers_sync(self, all_containers: bool = False) -> list:
        """Synchronous container listing."""
        try:
            containers = self.client.containers.list(all=all_containers)
            return [
                {
                    "id": container.id,
                    "name": container.name,
                    "status": container.status,
                    "image": container.image.tags[0] if container.image.tags else container.image.id,
                    "created": container.attrs["Created"]
                }
                for container in containers
            ]
        except Exception as e:
            logger.error(f"Failed to list containers: {e}")
            return []
    
    async def cleanup_old_containers(self, older_than_hours: int = 24) -> int:
        """Clean up old stopped containers."""
        try:
            logger.info(f"Cleaning up containers older than {older_than_hours} hours")
            
            # Run cleanup in thread pool
            loop = asyncio.get_event_loop()
            removed_count = await loop.run_in_executor(
                None,
                self._cleanup_old_containers_sync,
                older_than_hours
            )
            
            logger.info(f"Removed {removed_count} old containers")
            return removed_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old containers: {e}")
            return 0
    
    def _cleanup_old_containers_sync(self, older_than_hours: int = 24) -> int:
        """Synchronous cleanup of old containers."""
        import datetime
        
        try:
            containers = self.client.containers.list(all=True, filters={"status": "exited"})
            cutoff_time = datetime.datetime.now() - datetime.timedelta(hours=older_than_hours)
            removed_count = 0
            
            for container in containers:
                created_time = datetime.datetime.fromisoformat(
                    container.attrs["Created"].replace("Z", "+00:00")
                )
                
                if created_time < cutoff_time:
                    try:
                        container.remove()
                        removed_count += 1
                    except Exception as e:
                        logger.warning(f"Failed to remove container {container.id}: {e}")
            
            return removed_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old containers: {e}")
            return 0