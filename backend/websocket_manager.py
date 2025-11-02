# WebSocket Connection Manager
# Handles real-time updates for build progress and agent messages

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Set
import json
import asyncio
from datetime import datetime, timezone

class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        # Store connections by project_id
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Store user connections
        self.user_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, project_id: str, user_id: str = None):
        """Accept and register a new WebSocket connection"""
        await websocket.accept()
        
        # Add to project connections
        if project_id not in self.active_connections:
            self.active_connections[project_id] = set()
        self.active_connections[project_id].add(websocket)
        
        # Add to user connections
        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = set()
            self.user_connections[user_id].add(websocket)
        
        print(f"✅ WebSocket connected: project={project_id}, connections={len(self.active_connections[project_id])}")
    
    def disconnect(self, websocket: WebSocket, project_id: str, user_id: str = None):
        """Remove a WebSocket connection"""
        # Remove from project connections
        if project_id in self.active_connections:
            self.active_connections[project_id].discard(websocket)
            if not self.active_connections[project_id]:
                del self.active_connections[project_id]
        
        # Remove from user connections
        if user_id and user_id in self.user_connections:
            self.user_connections[user_id].discard(websocket)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        print(f"🔌 WebSocket disconnected: project={project_id}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send message to a specific connection"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"Error sending personal message: {e}")
    
    async def broadcast_to_project(self, project_id: str, message: dict):
        """Broadcast message to all connections for a specific project"""
        if project_id not in self.active_connections:
            return
        
        # Add timestamp
        message['timestamp'] = datetime.now(timezone.utc).isoformat()
        
        # Send to all connections
        disconnected = []
        for connection in self.active_connections[project_id].copy():
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error broadcasting to connection: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected connections
        for conn in disconnected:
            self.active_connections[project_id].discard(conn)
    
    async def broadcast_to_user(self, user_id: str, message: dict):
        """Broadcast message to all connections for a specific user"""
        if user_id not in self.user_connections:
            return
        
        # Add timestamp
        message['timestamp'] = datetime.now(timezone.utc).isoformat()
        
        # Send to all user connections
        disconnected = []
        for connection in self.user_connections[user_id].copy():
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error broadcasting to user: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected connections
        for conn in disconnected:
            self.user_connections[user_id].discard(conn)
    
    async def send_build_progress(self, project_id: str, data: dict):
        """Send build progress update"""
        message = {
            'type': 'build_progress',
            'project_id': project_id,
            'data': data
        }
        await self.broadcast_to_project(project_id, message)
    
    async def send_agent_message(self, project_id: str, agent_type: str, message: str, status: str = "working", progress: int = 0, **kwargs):
        """
        Send agent status update (Emergent-style)
        
        Args:
            project_id: Project identifier
            agent_type: Type of agent (planner, frontend, backend, image, testing)
            message: Status message
            status: Agent status (thinking, waiting, working, completed, warning, error)
            progress: Progress percentage (0-100)
            **kwargs: Additional metadata (tokens_used, credits_used, etc.)
        """
        message_data = {
            'type': 'agent_message',
            'project_id': project_id,
            'agent_type': agent_type,
            'message': message,
            'status': status,
            'progress': progress,
            **kwargs  # Include any additional data
        }
        await self.broadcast_to_project(project_id, message_data)
    
    async def send_build_complete(self, project_id: str, result: dict):
        """Send build completion notification"""
        message = {
            'type': 'build_complete',
            'project_id': project_id,
            'result': result
        }
        await self.broadcast_to_project(project_id, message)
    
    async def send_build_error(self, project_id: str, error: str):
        """Send build error notification"""
        message = {
            'type': 'build_error',
            'project_id': project_id,
            'error': error
        }
        await self.broadcast_to_project(project_id, message)
    
    async def send_credits_update(self, user_id: str, credits: int, transaction: dict = None):
        """Send credits update to user"""
        message = {
            'type': 'credits_update',
            'credits': credits,
            'transaction': transaction
        }
        await self.broadcast_to_user(user_id, message)
    
    def get_project_connections_count(self, project_id: str) -> int:
        """Get number of active connections for a project"""
        return len(self.active_connections.get(project_id, []))
    
    def get_user_connections_count(self, user_id: str) -> int:
        """Get number of active connections for a user"""
        return len(self.user_connections.get(user_id, []))
    
    async def heartbeat(self, websocket: WebSocket, interval: int = 30):
        """Send periodic heartbeat to keep connection alive"""
        try:
            while True:
                await asyncio.sleep(interval)
                await websocket.send_json({'type': 'heartbeat', 'timestamp': datetime.now(timezone.utc).isoformat()})
        except Exception:
            pass


# Global connection manager instance
ws_manager = ConnectionManager()

def get_websocket_manager() -> ConnectionManager:
    """Get the global WebSocket manager instance"""
    return ws_manager
