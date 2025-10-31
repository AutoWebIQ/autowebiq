# Server Routes v2 - PostgreSQL + Celery + WebSocket
# New endpoints using PostgreSQL models and async Celery tasks

from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db, User, Project, ProjectMessage, CreditTransaction
from credit_system_v2 import get_credit_manager_v2, TransactionType, TransactionStatus
from websocket_manager import ws_manager
from celery_tasks import build_website_task
from pydantic import BaseModel
from typing import List, Optional
import jwt
from datetime import datetime, timezone
import uuid
from passlib.context import CryptContext
import os

router_v2 = APIRouter(prefix="/api/v2")

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()
JWT_SECRET = os.environ.get('JWT_SECRET', 'autowebiq-secret-key-2025')
JWT_ALGORITHM = "HS256"

# ==================== Helper Functions ====================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get('user_id')
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# ==================== Models ====================

class BuildRequest(BaseModel):
    prompt: str
    uploaded_images: List[str] = []

class ProjectResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    status: str
    template_id: Optional[str]
    build_time: Optional[float]
    created_at: str
    updated_at: str

class CreditBalance(BaseModel):
    credits: int
    user_id: str


# ==================== WebSocket Endpoint ====================

@router_v2.websocket("/ws/build/{project_id}")
async def websocket_build_updates(
    websocket: WebSocket,
    project_id: str,
    token: str = None
):
    """
    WebSocket endpoint for real-time build updates
    
    Connect: ws://localhost:8001/api/v2/ws/build/{project_id}?token={jwt_token}
    """
    user_id = None
    
    # Authenticate user from token
    if token:
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            user_id = payload.get('user_id')
        except:
            pass
    
    # Connect WebSocket
    await ws_manager.connect(websocket, project_id, user_id)
    
    try:
        # Send initial connection message
        await ws_manager.send_personal_message(
            {
                'type': 'connection',
                'status': 'connected',
                'project_id': project_id,
                'message': 'WebSocket connected successfully'
            },
            websocket
        )
        
        # Keep connection alive and listen for messages
        while True:
            data = await websocket.receive_text()
            
            # Handle client messages (e.g., ping/pong)
            if data == "ping":
                await websocket.send_json({'type': 'pong'})
            
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, project_id, user_id)
        print(f"WebSocket disconnected: project_id={project_id}")
    except Exception as e:
        print(f"WebSocket error: {e}")
        ws_manager.disconnect(websocket, project_id, user_id)


# ==================== User Endpoints ====================

@router_v2.get("/user/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """Get current user information"""
    return {
        'id': current_user.id,
        'email': current_user.email,
        'name': current_user.name,
        'credits': current_user.credits,
        'created_at': current_user.created_at.isoformat(),
        'updated_at': current_user.updated_at.isoformat()
    }


@router_v2.get("/user/credits")
async def get_user_credits(
    current_user: User = Depends(get_current_user)
) -> CreditBalance:
    """Get user's credit balance"""
    return CreditBalance(
        credits=current_user.credits,
        user_id=current_user.id
    )


# ==================== Project Endpoints ====================

@router_v2.get("/projects")
async def list_projects(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
    limit: int = 50,
    offset: int = 0
):
    """List user's projects"""
    result = await session.execute(
        select(Project)
        .where(Project.user_id == current_user.id)
        .order_by(Project.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    
    projects = result.scalars().all()
    
    return [
        {
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'status': p.status,
            'template_id': p.template_id,
            'build_time': p.build_time,
            'created_at': p.created_at.isoformat(),
            'updated_at': p.updated_at.isoformat()
        }
        for p in projects
    ]


@router_v2.get("/projects/{project_id}")
async def get_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """Get project by ID"""
    result = await session.execute(
        select(Project)
        .where(Project.id == project_id)
        .where(Project.user_id == current_user.id)
    )
    
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return {
        'id': project.id,
        'name': project.name,
        'description': project.description,
        'status': project.status,
        'template_id': project.template_id,
        'generated_code': project.generated_code,
        'build_time': project.build_time,
        'created_at': project.created_at.isoformat(),
        'updated_at': project.updated_at.isoformat()
    }


@router_v2.post("/projects/{project_id}/build")
async def start_async_build(
    project_id: str,
    build_request: BuildRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Start async build with Celery
    Returns immediately with task_id
    """
    # Verify project ownership
    result = await session.execute(
        select(Project)
        .where(Project.id == project_id)
        .where(Project.user_id == current_user.id)
    )
    
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check credits (estimate 30-50 credits per build)
    estimated_cost = 40
    if current_user.credits < estimated_cost:
        raise HTTPException(
            status_code=402,
            detail=f"Insufficient credits. Need ~{estimated_cost}, have {current_user.credits}"
        )
    
    # Update project status to building
    await session.execute(
        update(Project)
        .where(Project.id == project_id)
        .values(status='building', updated_at=datetime.now(timezone.utc))
    )
    await session.commit()
    
    # Submit Celery task
    task = build_website_task.delay(
        user_prompt=build_request.prompt,
        project_id=project_id,
        user_id=current_user.id,
        uploaded_images=build_request.uploaded_images
    )
    
    return {
        'status': 'building',
        'task_id': task.id,
        'project_id': project_id,
        'message': 'Build started successfully. Connect to WebSocket for real-time updates.',
        'websocket_url': f'/api/v2/ws/build/{project_id}'
    }


@router_v2.get("/projects/{project_id}/build/status/{task_id}")
async def get_build_status(
    project_id: str,
    task_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """Get build task status"""
    from celery.result import AsyncResult
    
    # Verify project ownership
    result = await session.execute(
        select(Project)
        .where(Project.id == project_id)
        .where(Project.user_id == current_user.id)
    )
    
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get Celery task result
    task_result = AsyncResult(task_id)
    
    response = {
        'task_id': task_id,
        'project_id': project_id,
        'status': task_result.state,
    }
    
    if task_result.state == 'PENDING':
        response['message'] = 'Task is waiting to be processed'
    elif task_result.state == 'PROGRESS':
        response['progress'] = task_result.info
    elif task_result.state == 'SUCCESS':
        response['result'] = task_result.result
        response['message'] = 'Build completed successfully'
    elif task_result.state == 'FAILURE':
        response['error'] = str(task_result.info)
        response['message'] = 'Build failed'
    
    return response


# ==================== Credit Endpoints ====================

@router_v2.get("/credits/history")
async def get_credit_history(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
    limit: int = 50,
    offset: int = 0
):
    """Get user's credit transaction history"""
    credit_manager = get_credit_manager_v2(session)
    transactions = await credit_manager.get_transaction_history(
        user_id=current_user.id,
        limit=limit,
        offset=offset
    )
    
    return {
        'current_balance': current_user.credits,
        'transactions': transactions
    }


# ==================== Stats Endpoints ====================

@router_v2.get("/stats")
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """Get user statistics"""
    # Count projects
    project_count_result = await session.execute(
        select(func.count(Project.id))
        .where(Project.user_id == current_user.id)
    )
    project_count = project_count_result.scalar()
    
    # Count completed projects
    completed_count_result = await session.execute(
        select(func.count(Project.id))
        .where(Project.user_id == current_user.id)
        .where(Project.status == 'completed')
    )
    completed_count = completed_count_result.scalar()
    
    # Count total credits spent
    credits_spent_result = await session.execute(
        select(func.sum(CreditTransaction.amount))
        .where(CreditTransaction.user_id == current_user.id)
        .where(CreditTransaction.transaction_type == 'deduction')
    )
    credits_spent = abs(credits_spent_result.scalar() or 0)
    
    return {
        'user_id': current_user.id,
        'email': current_user.email,
        'credits': current_user.credits,
        'total_projects': project_count,
        'completed_projects': completed_count,
        'credits_spent': credits_spent,
        'member_since': current_user.created_at.isoformat()
    }
