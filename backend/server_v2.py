# AutoWebIQ 2.0 - Clean FastAPI Server
from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import asyncio
import json
import logging

from config import db, ALLOWED_ORIGINS
from auth import register_user, login_user, get_current_user
from credits import get_user_credits, deduct_credits, get_transactions, get_action_cost
from ai_agents import WebsiteBuilder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AutoWebIQ 2.0", version="2.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ProjectCreate(BaseModel):
    name: str
    description: str

class ChatMessage(BaseModel):
    message: str
    project_id: str

# Health Check
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    try:
        await db.command('ping')
        return {
            "status": "healthy",
            "service": "autowebiq-v2",
            "database": "mongodb-connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

# Authentication Endpoints
@app.post("/api/auth/register")
async def register(request: RegisterRequest):
    """Register new user"""
    return await register_user(request.email, request.password, request.name)

@app.post("/api/auth/login")
async def login(request: LoginRequest):
    """Login user"""
    return await login_user(request.email, request.password)

@app.get("/api/auth/me")
async def get_me(user_id: str = Depends(get_current_user)):
    """Get current user info"""
    user = await db.users.find_one({'id': user_id}, {'_id': 0, 'password': 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Credits Endpoints
@app.get("/api/credits/balance")
async def get_balance(user_id: str = Depends(get_current_user)):
    """Get credit balance"""
    credits = await get_user_credits(user_id)
    return {"credits": credits}

@app.get("/api/credits/transactions")
async def get_credit_transactions(user_id: str = Depends(get_current_user)):
    """Get credit transaction history"""
    transactions = await get_transactions(user_id)
    return {"transactions": transactions}

# Project Endpoints
@app.post("/api/projects")
async def create_project(project: ProjectCreate, user_id: str = Depends(get_current_user)):
    """Create new project"""
    import uuid
    from datetime import datetime, timezone
    
    project_id = str(uuid.uuid4())
    project_data = {
        'id': project_id,
        'user_id': user_id,
        'name': project.name,
        'description': project.description,
        'generated_code': None,
        'status': 'draft',
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    
    await db.projects.insert_one(project_data)
    
    return {
        'project_id': project_id,
        'name': project.name,
        'status': 'created'
    }

@app.get("/api/projects")
async def list_projects(user_id: str = Depends(get_current_user)):
    """List user's projects"""
    projects = await db.projects.find(
        {'user_id': user_id},
        {'_id': 0}
    ).sort('created_at', -1).to_list(length=100)
    
    return {"projects": projects}

@app.get("/api/projects/{project_id}")
async def get_project(project_id: str, user_id: str = Depends(get_current_user)):
    """Get project by ID"""
    project = await db.projects.find_one(
        {'id': project_id, 'user_id': user_id},
        {'_id': 0}
    )
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return project

# WebSocket for Real-time Updates (Emergent-style)
@app.websocket("/ws/{project_id}")
async def websocket_endpoint(websocket: WebSocket, project_id: str):
    """WebSocket for real-time agent status updates"""
    await websocket.accept()
    
    try:
        while True:
            # Wait for messages
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Get user from token
            token = message_data.get('token')
            if not token:
                await websocket.send_json({"error": "No token provided"})
                continue
            
            # Decode token to get user_id
            from auth import decode_token
            try:
                payload = decode_token(token)
                user_id = payload['user_id']
            except:
                await websocket.send_json({"error": "Invalid token"})
                continue
            
            # Get user message
            user_message = message_data.get('message', '')
            
            if not user_message:
                continue
            
            # Initialize builder
            builder = WebsiteBuilder(user_id, project_id, websocket)
            
            # Generate website with gradual updates
            await builder.build_website(user_message)
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for project {project_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        try:
            await websocket.send_json({"error": str(e)})
        except:
            pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
