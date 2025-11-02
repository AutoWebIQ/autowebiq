# Terminal Manager for AutoWebIQ
# WebSocket-based terminal access to Docker containers

import asyncio
import docker
import pty
import os
import select
import subprocess
import struct
import fcntl
import termios
from typing import Dict, Optional
from fastapi import WebSocket
import json

class TerminalSession:
    """Manages a terminal session in a Docker container"""
    
    def __init__(self, container_id: str, websocket: WebSocket):
        self.container_id = container_id
        self.websocket = websocket
        self.exec_id = None
        self.socket = None
        self.running = False
    
    async def start(self):
        """Start terminal session"""
        try:
            client = docker.from_env()
            container = client.containers.get(self.container_id)
            
            # Create exec instance with PTY
            exec_instance = client.api.exec_create(
                container.id,
                cmd=["/bin/sh"],
                stdin=True,
                stdout=True,
                stderr=True,
                tty=True,
                environment={"TERM": "xterm-256color"}
            )
            
            self.exec_id = exec_instance['Id']
            
            # Start exec with socket
            exec_socket = client.api.exec_start(
                self.exec_id,
                socket=True,
                tty=True
            )
            
            self.socket = exec_socket
            self.running = True
            
            # Start bidirectional communication
            await asyncio.gather(
                self._read_from_docker(),
                self._write_to_docker()
            )
            
        except Exception as e:
            print(f"Terminal session error: {e}")
            await self.websocket.send_json({
                "type": "error",
                "data": f"Failed to start terminal: {str(e)}"
            })
    
    async def _read_from_docker(self):
        """Read output from Docker and send to WebSocket"""
        try:
            while self.running:
                # Read from Docker socket
                data = self.socket._sock.recv(4096)
                
                if not data:
                    break
                
                # Send to WebSocket
                await self.websocket.send_json({
                    "type": "output",
                    "data": data.decode('utf-8', errors='ignore')
                })
                
                await asyncio.sleep(0.01)
        
        except Exception as e:
            print(f"Read error: {e}")
        finally:
            self.running = False
    
    async def _write_to_docker(self):
        """Receive input from WebSocket and write to Docker"""
        try:
            while self.running:
                # Receive from WebSocket
                message = await self.websocket.receive_text()
                data = json.loads(message)
                
                if data.get("type") == "input":
                    # Write to Docker
                    input_data = data.get("data", "")
                    self.socket._sock.send(input_data.encode('utf-8'))
                
                elif data.get("type") == "resize":
                    # Handle terminal resize
                    rows = data.get("rows", 24)
                    cols = data.get("cols", 80)
                    await self._resize_terminal(rows, cols)
        
        except Exception as e:
            print(f"Write error: {e}")
        finally:
            self.running = False
    
    async def _resize_terminal(self, rows: int, cols: int):
        """Resize terminal"""
        try:
            client = docker.from_env()
            client.api.exec_resize(self.exec_id, height=rows, width=cols)
        except Exception as e:
            print(f"Resize error: {e}")
    
    async def stop(self):
        """Stop terminal session"""
        self.running = False
        if self.socket:
            self.socket.close()


class TerminalManager:
    """
    Manages WebSocket-based terminal sessions for Docker containers.
    Provides full terminal access with bi-directional communication.
    """
    
    def __init__(self):
        self.sessions: Dict[str, TerminalSession] = {}
        try:
            self.client = docker.from_env()
            print("✅ Terminal manager initialized")
        except Exception as e:
            print(f"⚠️ Docker not available for terminal: {e}")
            self.client = None
    
    async def create_session(
        self,
        container_id: str,
        websocket: WebSocket,
        session_id: str
    ) -> TerminalSession:
        """
        Create a new terminal session.
        
        Args:
            container_id: Docker container ID
            websocket: WebSocket connection
            session_id: Unique session identifier
        
        Returns:
            TerminalSession instance
        """
        if not self.client:
            raise Exception("Docker not available")
        
        session = TerminalSession(container_id, websocket)
        self.sessions[session_id] = session
        
        return session
    
    async def execute_command(
        self,
        container_id: str,
        command: str,
        working_dir: str = "/workspace"
    ) -> Dict:
        """
        Execute a single command in container.
        
        Args:
            container_id: Docker container ID
            command: Command to execute
            working_dir: Working directory
        
        Returns:
            {
                "status": "success" | "error",
                "output": str,
                "exit_code": int
            }
        """
        if not self.client:
            return {
                "status": "error",
                "message": "Docker not available"
            }
        
        try:
            container = self.client.containers.get(container_id)
            
            # Execute command
            exec_result = container.exec_run(
                cmd=command,
                workdir=working_dir,
                stdout=True,
                stderr=True
            )
            
            output = exec_result.output.decode('utf-8')
            exit_code = exec_result.exit_code
            
            return {
                "status": "success" if exit_code == 0 else "error",
                "output": output,
                "exit_code": exit_code
            }
        
        except Exception as e:
            return {
                "status": "error",
                "message": f"Command execution failed: {str(e)}"
            }
    
    async def install_packages(
        self,
        container_id: str,
        packages: list,
        package_manager: str = "npm"
    ) -> Dict:
        """
        Install packages in container.
        
        Args:
            container_id: Docker container ID
            packages: List of package names
            package_manager: "npm", "pip", "yarn"
        """
        commands = {
            "npm": f"npm install {' '.join(packages)}",
            "pip": f"pip install {' '.join(packages)}",
            "yarn": f"yarn add {' '.join(packages)}"
        }
        
        command = commands.get(package_manager)
        if not command:
            return {
                "status": "error",
                "message": f"Unknown package manager: {package_manager}"
            }
        
        return await self.execute_command(container_id, command)
    
    async def run_tests(
        self,
        container_id: str,
        test_command: str = "npm test"
    ) -> Dict:
        """Run tests in container"""
        return await self.execute_command(container_id, test_command)
    
    async def get_container_info(self, container_id: str) -> Dict:
        """Get container information"""
        if not self.client:
            return {
                "status": "error",
                "message": "Docker not available"
            }
        
        try:
            container = self.client.containers.get(container_id)
            
            return {
                "status": "success",
                "id": container.id,
                "name": container.name,
                "status": container.status,
                "image": container.image.tags[0] if container.image.tags else "unknown",
                "created": container.attrs['Created'],
                "ports": container.ports
            }
        
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get container info: {str(e)}"
            }
    
    def get_session(self, session_id: str) -> Optional[TerminalSession]:
        """Get existing session"""
        return self.sessions.get(session_id)
    
    async def close_session(self, session_id: str):
        """Close a terminal session"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            await session.stop()
            del self.sessions[session_id]


# Singleton instance
_terminal_manager = None

def get_terminal_manager() -> TerminalManager:
    """Get or create singleton terminal manager"""
    global _terminal_manager
    if _terminal_manager is None:
        _terminal_manager = TerminalManager()
    return _terminal_manager
