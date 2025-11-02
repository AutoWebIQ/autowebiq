# Docker Workspace Manager for AutoWebIQ
# Creates isolated development environments for each project

import docker
import asyncio
import os
import json
import shutil
from typing import Dict, Optional, List
from datetime import datetime
from pathlib import Path
import random

class WorkspaceManager:
    """
    Manages Docker-based development workspaces for projects.
    Each workspace is an isolated container with Node.js, Python, and development tools.
    """
    
    def __init__(self):
        try:
            self.client = docker.from_env()
            self.base_port = 4000  # Starting port for workspaces
            self.max_port = 5000   # Max port range
            self.workspaces: Dict[str, Dict] = {}  # project_id -> workspace info
            print("✅ Docker client initialized")
        except Exception as e:
            print(f"⚠️ Docker not available: {e}")
            self.client = None
    
    async def create_workspace(
        self, 
        project_id: str, 
        user_id: str,
        files: Dict[str, str],
        project_name: str = "app"
    ) -> Dict:
        """
        Create a new Docker workspace with the generated code.
        
        Args:
            project_id: Unique project identifier
            user_id: User who owns the project
            files: Dictionary of file paths and contents
            project_name: Name of the project
        
        Returns:
            {
                "status": "success" | "error",
                "workspace_id": str,
                "container_id": str,
                "preview_url": str,
                "frontend_port": int,
                "backend_port": int,
                "message": str
            }
        """
        if not self.client:
            return {
                "status": "error",
                "message": "Docker is not available. Live preview requires Docker."
            }
        
        try:
            # Create workspace directory
            workspace_path = f"/tmp/workspaces/{user_id}/{project_id}"
            os.makedirs(workspace_path, exist_ok=True)
            
            # Write all files to workspace
            for file_path, content in files.items():
                full_path = os.path.join(workspace_path, file_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            print(f"✅ Created workspace at {workspace_path} with {len(files)} files")
            
            # Allocate ports
            frontend_port = await self._allocate_port()
            backend_port = await self._allocate_port()
            
            # Create Dockerfile for the workspace
            dockerfile_content = self._generate_dockerfile()
            with open(os.path.join(workspace_path, 'Dockerfile'), 'w') as f:
                f.write(dockerfile_content)
            
            # Create docker-compose.yml if not exists
            if 'docker-compose.yml' not in files:
                compose_content = self._generate_docker_compose(frontend_port, backend_port)
                with open(os.path.join(workspace_path, 'docker-compose.yml'), 'w') as f:
                    f.write(compose_content)
            
            # Create startup script
            startup_script = self._generate_startup_script()
            startup_path = os.path.join(workspace_path, 'start.sh')
            with open(startup_path, 'w') as f:
                f.write(startup_script)
            os.chmod(startup_path, 0o755)
            
            # Build and start container
            container_name = f"autowebiq-{project_id[:8]}"
            
            # Check if container already exists
            try:
                existing = self.client.containers.get(container_name)
                existing.stop()
                existing.remove()
                print(f"🗑️ Removed existing container {container_name}")
            except docker.errors.NotFound:
                pass
            
            # Create and start new container
            container = self.client.containers.run(
                "node:18-alpine",
                name=container_name,
                detach=True,
                ports={
                    '3000/tcp': frontend_port,
                    '8000/tcp': backend_port
                },
                volumes={
                    workspace_path: {'bind': '/workspace', 'mode': 'rw'}
                },
                working_dir='/workspace',
                command='sh -c "apk add --no-cache python3 py3-pip && ./start.sh"',
                environment={
                    'NODE_ENV': 'development',
                    'VITE_API_URL': f'http://localhost:{backend_port}'
                }
            )
            
            workspace_id = f"ws_{project_id[:12]}"
            
            # Store workspace info
            self.workspaces[project_id] = {
                "workspace_id": workspace_id,
                "container_id": container.id,
                "container_name": container_name,
                "frontend_port": frontend_port,
                "backend_port": backend_port,
                "workspace_path": workspace_path,
                "user_id": user_id,
                "created_at": datetime.utcnow().isoformat(),
                "status": "running"
            }
            
            preview_url = f"http://localhost:{frontend_port}"
            
            print(f"✅ Workspace created: {workspace_id}")
            print(f"   Container: {container_name}")
            print(f"   Frontend: {preview_url}")
            print(f"   Backend: http://localhost:{backend_port}")
            
            return {
                "status": "success",
                "workspace_id": workspace_id,
                "container_id": container.id,
                "container_name": container_name,
                "preview_url": preview_url,
                "frontend_port": frontend_port,
                "backend_port": backend_port,
                "workspace_path": workspace_path,
                "message": "Workspace created successfully. Starting services..."
            }
            
        except Exception as e:
            print(f"❌ Workspace creation failed: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                "status": "error",
                "message": f"Failed to create workspace: {str(e)}"
            }
    
    async def get_workspace_status(self, project_id: str) -> Dict:
        """Get status of a workspace"""
        if project_id not in self.workspaces:
            return {
                "status": "not_found",
                "message": "Workspace does not exist"
            }
        
        workspace = self.workspaces[project_id]
        
        try:
            container = self.client.containers.get(workspace["container_id"])
            container_status = container.status
            
            return {
                "status": "success",
                "workspace_id": workspace["workspace_id"],
                "container_status": container_status,
                "frontend_port": workspace["frontend_port"],
                "backend_port": workspace["backend_port"],
                "preview_url": f"http://localhost:{workspace['frontend_port']}",
                "created_at": workspace["created_at"]
            }
        except docker.errors.NotFound:
            return {
                "status": "error",
                "message": "Container not found"
            }
    
    async def stop_workspace(self, project_id: str) -> Dict:
        """Stop a running workspace"""
        if project_id not in self.workspaces:
            return {"status": "error", "message": "Workspace not found"}
        
        workspace = self.workspaces[project_id]
        
        try:
            container = self.client.containers.get(workspace["container_id"])
            container.stop()
            workspace["status"] = "stopped"
            
            return {
                "status": "success",
                "message": "Workspace stopped successfully"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to stop workspace: {str(e)}"
            }
    
    async def restart_workspace(self, project_id: str) -> Dict:
        """Restart a workspace"""
        if project_id not in self.workspaces:
            return {"status": "error", "message": "Workspace not found"}
        
        workspace = self.workspaces[project_id]
        
        try:
            container = self.client.containers.get(workspace["container_id"])
            container.restart()
            workspace["status"] = "running"
            
            return {
                "status": "success",
                "message": "Workspace restarted successfully"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to restart workspace: {str(e)}"
            }
    
    async def delete_workspace(self, project_id: str) -> Dict:
        """Delete a workspace and its container"""
        if project_id not in self.workspaces:
            return {"status": "error", "message": "Workspace not found"}
        
        workspace = self.workspaces[project_id]
        
        try:
            # Stop and remove container
            container = self.client.containers.get(workspace["container_id"])
            container.stop()
            container.remove()
            
            # Remove workspace directory
            if os.path.exists(workspace["workspace_path"]):
                shutil.rmtree(workspace["workspace_path"])
            
            # Remove from tracking
            del self.workspaces[project_id]
            
            return {
                "status": "success",
                "message": "Workspace deleted successfully"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to delete workspace: {str(e)}"
            }
    
    async def get_workspace_logs(self, project_id: str, tail: int = 100) -> Dict:
        """Get logs from workspace container"""
        if project_id not in self.workspaces:
            return {"status": "error", "message": "Workspace not found"}
        
        workspace = self.workspaces[project_id]
        
        try:
            container = self.client.containers.get(workspace["container_id"])
            logs = container.logs(tail=tail, timestamps=True).decode('utf-8')
            
            return {
                "status": "success",
                "logs": logs
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get logs: {str(e)}"
            }
    
    async def _allocate_port(self) -> int:
        """Allocate an available port"""
        used_ports = set()
        for ws in self.workspaces.values():
            used_ports.add(ws.get("frontend_port"))
            used_ports.add(ws.get("backend_port"))
        
        for port in range(self.base_port, self.max_port):
            if port not in used_ports:
                return port
        
        raise Exception("No available ports")
    
    def _generate_dockerfile(self) -> str:
        """Generate Dockerfile for workspace"""
        return """FROM node:18-alpine

# Install Python and system dependencies
RUN apk add --no-cache python3 py3-pip bash git

WORKDIR /workspace

# Install global npm packages
RUN npm install -g npm@latest

EXPOSE 3000 8000

CMD ["sh", "-c", "while true; do sleep 1000; done"]
"""
    
    def _generate_docker_compose(self, frontend_port: int, backend_port: int) -> str:
        """Generate docker-compose.yml"""
        return f"""version: '3.8'

services:
  app:
    build: .
    ports:
      - "{frontend_port}:3000"
      - "{backend_port}:8000"
    volumes:
      - .:/workspace
    working_dir: /workspace
    environment:
      - NODE_ENV=development
      - VITE_API_URL=http://localhost:{backend_port}
"""
    
    def _generate_startup_script(self) -> str:
        """Generate startup script for container"""
        return """#!/bin/sh

echo "🚀 Starting AutoWebIQ Workspace..."

# Install frontend dependencies if package.json exists
if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
    echo "📦 Installing frontend dependencies..."
    cd frontend
    npm install
    echo "✅ Frontend dependencies installed"
    
    echo "🎨 Starting frontend server..."
    npm run dev &
    cd ..
fi

# Install backend dependencies if requirements.txt exists
if [ -d "backend" ] && [ -f "backend/requirements.txt" ]; then
    echo "📦 Installing backend dependencies..."
    cd backend
    pip3 install -r requirements.txt
    echo "✅ Backend dependencies installed"
    
    echo "⚙️ Starting backend server..."
    python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
    cd ..
fi

echo "✅ Workspace ready!"
echo "Frontend: http://localhost:3000"
echo "Backend: http://localhost:8000"

# Keep container running
tail -f /dev/null
"""


# Singleton instance
_workspace_manager = None

def get_workspace_manager() -> WorkspaceManager:
    """Get or create singleton workspace manager"""
    global _workspace_manager
    if _workspace_manager is None:
        _workspace_manager = WorkspaceManager()
    return _workspace_manager
