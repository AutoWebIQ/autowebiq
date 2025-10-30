# Docker Container Management for AutoWebIQ
# Manages user workspace containers

import docker
import os
import logging
from typing import Dict, Optional
import random
import string

logger = logging.getLogger(__name__)

class DockerManager:
    """Manages Docker containers for user workspaces"""
    
    def __init__(self):
        try:
            self.client = docker.from_env()
            self.registry = "aashikzm098"  # Docker Hub username
            self.image_name = f"{self.registry}/autowebiq-workspace"
            self.image_tag = "latest"
            logger.info("Docker client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Docker client: {e}")
            self.client = None
    
    def is_docker_available(self) -> bool:
        """Check if Docker is available"""
        return self.client is not None
    
    async def create_container(self, user_id: str, project_id: str, frontend_code: str, backend_code: str = "") -> Dict:
        """
        Create a new Docker container for a project
        Returns: container info with URL
        """
        if not self.is_docker_available():
            return {
                "status": "error",
                "message": "Docker not available. Using fallback preview."
            }
        
        try:
            # Generate unique container name
            container_name = f"autowebiq-{user_id}-{project_id}"[:63]  # Docker name limit
            
            # Allocate random port (avoid conflicts)
            port = random.randint(10000, 60000)
            
            # Create container
            container = self.client.containers.run(
                image=f"{self.image_name}:{self.image_tag}",
                name=container_name,
                detach=True,
                ports={'80/tcp': port},
                environment={
                    'USER_ID': user_id,
                    'PROJECT_ID': project_id
                },
                labels={
                    'autowebiq.user_id': user_id,
                    'autowebiq.project_id': project_id,
                    'autowebiq.type': 'workspace'
                },
                remove=False,  # Keep container after stop
                mem_limit='512m',  # Limit memory per container
                cpu_period=100000,
                cpu_quota=50000  # 50% of 1 CPU
            )
            
            # Write code to container
            await self._write_code_to_container(container, frontend_code, backend_code)
            
            logger.info(f"Container {container_name} created on port {port}")
            
            return {
                "status": "success",
                "container_id": container.id,
                "container_name": container_name,
                "port": port,
                "preview_url": f"http://localhost:{port}",
                "message": "Container created successfully"
            }
            
        except docker.errors.ImageNotFound:
            logger.error(f"Image {self.image_name}:{self.image_tag} not found")
            return {
                "status": "error",
                "message": "Workspace image not found. Please build the image first."
            }
        except Exception as e:
            logger.error(f"Failed to create container: {e}")
            return {
                "status": "error",
                "message": f"Container creation failed: {str(e)}"
            }
    
    async def _write_code_to_container(self, container, frontend_code: str, backend_code: str):
        """Write generated code to container"""
        try:
            # Write frontend code (index.html)
            container.exec_run(
                f"sh -c 'echo {self._escape_code(frontend_code)} > /workspace/frontend/index.html'"
            )
            
            # Write backend code if exists
            if backend_code:
                container.exec_run(
                    f"sh -c 'echo {self._escape_code(backend_code)} > /workspace/backend/server.py'"
                )
            
            # Restart services
            container.exec_run("supervisorctl restart all")
            
        except Exception as e:
            logger.error(f"Failed to write code to container: {e}")
    
    def _escape_code(self, code: str) -> str:
        """Escape code for shell command"""
        return code.replace("'", "'\\''")
    
    async def stop_container(self, container_name: str) -> Dict:
        """Stop a container"""
        try:
            container = self.client.containers.get(container_name)
            container.stop()
            logger.info(f"Container {container_name} stopped")
            return {"status": "success", "message": "Container stopped"}
        except Exception as e:
            logger.error(f"Failed to stop container: {e}")
            return {"status": "error", "message": str(e)}
    
    async def start_container(self, container_name: str) -> Dict:
        """Start a stopped container"""
        try:
            container = self.client.containers.get(container_name)
            container.start()
            logger.info(f"Container {container_name} started")
            return {"status": "success", "message": "Container started"}
        except Exception as e:
            logger.error(f"Failed to start container: {e}")
            return {"status": "error", "message": str(e)}
    
    async def delete_container(self, container_name: str) -> Dict:
        """Delete a container"""
        try:
            container = self.client.containers.get(container_name)
            container.stop()
            container.remove()
            logger.info(f"Container {container_name} deleted")
            return {"status": "success", "message": "Container deleted"}
        except Exception as e:
            logger.error(f"Failed to delete container: {e}")
            return {"status": "error", "message": str(e)}
    
    async def get_container_status(self, container_name: str) -> Dict:
        """Get container status"""
        try:
            container = self.client.containers.get(container_name)
            return {
                "status": "success",
                "container_status": container.status,
                "running": container.status == "running"
            }
        except docker.errors.NotFound:
            return {
                "status": "error",
                "message": "Container not found"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def list_user_containers(self, user_id: str) -> list:
        """List all containers for a user"""
        try:
            containers = self.client.containers.list(
                all=True,
                filters={'label': f'autowebiq.user_id={user_id}'}
            )
            
            result = []
            for container in containers:
                result.append({
                    "id": container.id,
                    "name": container.name,
                    "status": container.status,
                    "project_id": container.labels.get('autowebiq.project_id')
                })
            
            return result
        except Exception as e:
            logger.error(f"Failed to list containers: {e}")
            return []
    
    async def build_image(self) -> Dict:
        """Build the workspace Docker image"""
        try:
            logger.info("Building Docker image...")
            image, build_logs = self.client.images.build(
                path="/app/docker",
                tag=f"{self.image_name}:{self.image_tag}",
                rm=True,
                pull=True
            )
            
            # Log build output
            for log in build_logs:
                if 'stream' in log:
                    logger.info(log['stream'].strip())
            
            logger.info("Docker image built successfully")
            return {
                "status": "success",
                "image_id": image.id,
                "message": "Image built successfully"
            }
        except Exception as e:
            logger.error(f"Failed to build image: {e}")
            return {
                "status": "error",
                "message": f"Image build failed: {str(e)}"
            }
    
    async def push_image(self) -> Dict:
        """Push image to Docker Hub"""
        try:
            logger.info("Pushing image to Docker Hub...")
            
            # Login to Docker Hub
            self.client.login(
                username=os.environ.get('DOCKER_HUB_USERNAME'),
                password=os.environ.get('DOCKER_HUB_TOKEN')
            )
            
            # Push image
            push_logs = self.client.images.push(
                repository=self.image_name,
                tag=self.image_tag,
                stream=True,
                decode=True
            )
            
            # Log push output
            for log in push_logs:
                if 'status' in log:
                    logger.info(f"{log['status']}: {log.get('progress', '')}")
            
            logger.info("Image pushed successfully")
            return {
                "status": "success",
                "message": "Image pushed to Docker Hub"
            }
        except Exception as e:
            logger.error(f"Failed to push image: {e}")
            return {
                "status": "error",
                "message": f"Image push failed: {str(e)}"
            }

# Global instance
docker_manager = DockerManager()
