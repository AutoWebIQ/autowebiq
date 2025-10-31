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

class CreateProjectRequest(BaseModel):
    name: str
    description: Optional[str] = None

@router_v2.post("/projects")
async def create_project(
    project_data: CreateProjectRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """Create a new project"""
    project = Project(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        name=project_data.name,
        description=project_data.description,
        status='draft',
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    
    session.add(project)
    await session.commit()
    
    return {
        'id': project.id,
        'name': project.name,
        'description': project.description,
        'status': project.status,
        'created_at': project.created_at.isoformat(),
        'updated_at': project.updated_at.isoformat()
    }


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
    
    # Check and deduct credits using V2 credit system
    estimated_cost = 40
    credit_manager = get_credit_manager_v2(session)
    
    # Deduct credits upfront
    deduction_result = await credit_manager.deduct_credits(
        user_id=current_user.id,
        amount=estimated_cost,
        description=f"V2 Async build for project: {project.name}",
        extra_data={
            "project_id": project_id,
            "prompt": build_request.prompt[:100] + "..." if len(build_request.prompt) > 100 else build_request.prompt
        }
    )
    
    if deduction_result['status'] != 'success':
        raise HTTPException(
            status_code=402,
            detail=f"Insufficient credits. Need {estimated_cost}, have {deduction_result.get('balance', 0)}"
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



# ==================== Deployment Endpoints ====================

class VercelDeployRequest(BaseModel):
    """Request to deploy a website to Vercel"""
    project_id: str
    project_name: Optional[str] = None
    environment: str = "preview"  # preview or production


@router_v2.post("/deploy/vercel")
async def deploy_to_vercel(
    deploy_request: VercelDeployRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Deploy a project to Vercel.
    
    Deploys the generated website HTML/CSS/JS to Vercel and returns the live URL.
    """
    from vercel_service import VercelService, VercelDeploymentError
    
    # Verify project ownership
    result = await session.execute(
        select(Project)
        .where(Project.id == deploy_request.project_id)
        .where(Project.user_id == current_user.id)
    )
    
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if project has generated code
    if not project.generated_html:
        raise HTTPException(
            status_code=400,
            detail="Project has no generated code. Please build the website first."
        )
    
    # Determine project name for Vercel
    vercel_project_name = deploy_request.project_name or project.name or f"autowebiq-{project.id[:8]}"
    vercel_project_name = vercel_project_name.lower().replace(' ', '-').replace('_', '-')
    
    try:
        # Initialize Vercel service
        vercel = VercelService()
        
        # Deploy the website
        deployment_result = vercel.deploy_website(
            project_name=vercel_project_name,
            html_content=project.generated_html,
            css_content=project.generated_css,
            js_content=project.generated_js,
            environment=deploy_request.environment
        )
        
        # Update project with deployment URL
        await session.execute(
            update(Project)
            .where(Project.id == project.id)
            .values(
                deployment_url=deployment_result['deployment_url'],
                updated_at=datetime.now(timezone.utc)
            )
        )
        await session.commit()
        
        return {
            'success': True,
            'deployment_id': deployment_result['deployment_id'],
            'deployment_url': deployment_result['deployment_url'],
            'preview_url': deployment_result['preview_url'],
            'project_name': vercel_project_name,
            'environment': deploy_request.environment,
            'message': 'Website deployed successfully to Vercel!'
        }
        
    except VercelDeploymentError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Vercel deployment failed: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Deployment error: {str(e)}"
        )


@router_v2.get("/deploy/vercel/status/{deployment_id}")
async def check_deployment_status(
    deployment_id: str,
    current_user: User = Depends(get_current_user)
):
    """Check the status of a Vercel deployment"""
    from vercel_service import VercelService, VercelDeploymentError
    
    try:
        vercel = VercelService()
        status = vercel.get_deployment_status(deployment_id)
        
        return {
            'deployment_id': deployment_id,
            'state': status['state'],
            'ready': status['ready'],
            'url': status.get('url'),
            'error_message': status.get('error_message')
        }
        
    except VercelDeploymentError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check deployment status: {str(e)}"
        )



# ==================== Validation Endpoints ====================

class ValidationRequest(BaseModel):
    """Request to validate a website"""
    project_id: str
    url: Optional[str] = None  # Optional deployed URL for live checks


@router_v2.post("/validate/website")
async def validate_website(
    validation_request: ValidationRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Run 9-point validation on a generated website
    
    Validates:
    1. HTML - Syntax and structure
    2. CSS - Syntax and best practices
    3. JavaScript - Syntax and errors
    4. Accessibility - WCAG 2.1 compliance
    5. SEO - Meta tags, structure
    6. Performance - Load time, optimization
    7. Security - HTTPS, headers, vulnerabilities
    8. Browser Compatibility - Cross-browser support
    9. Mobile Responsiveness - Viewport, responsive design
    """
    from validation_service import WebsiteValidator
    
    # Verify project ownership
    result = await session.execute(
        select(Project)
        .where(Project.id == validation_request.project_id)
        .where(Project.user_id == current_user.id)
    )
    
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if project has generated code
    if not project.generated_html:
        raise HTTPException(
            status_code=400,
            detail="Project has no generated code. Please build the website first."
        )
    
    try:
        # Initialize validator
        validator = WebsiteValidator()
        
        # Run validation
        validation_results = await validator.validate_all(
            html_content=project.generated_html,
            css_content=project.generated_css or "",
            js_content=project.generated_js or "",
            url=validation_request.url
        )
        
        # Store validation results in project (optional)
        # You could add a validation_results JSON field to Project model
        
        return {
            'success': True,
            'project_id': project.id,
            'project_name': project.name,
            'overall_score': validation_results['overall_score'],
            'passed_checks': validation_results['passed_checks'],
            'total_checks': validation_results['total_checks'],
            'all_passed': validation_results['all_passed'],
            'results': validation_results['results'],
            'summary': validation_results['summary'],
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Validation error: {str(e)}"
        )


@router_v2.get("/validate/checks")
async def get_validation_checks():
    """Get information about available validation checks (public endpoint)"""
    
    return {
        'total_checks': 9,
        'checks': [
            {
                'id': 1,
                'name': 'HTML Validation',
                'description': 'Validates HTML5 syntax, structure, and semantic markup',
                'criteria': ['DOCTYPE', 'Semantic tags', 'Closed tags', 'Valid attributes']
            },
            {
                'id': 2,
                'name': 'CSS Validation',
                'description': 'Validates CSS syntax and best practices',
                'criteria': ['Valid syntax', 'Vendor prefixes', 'No duplicates', 'Proper usage']
            },
            {
                'id': 3,
                'name': 'JavaScript Validation',
                'description': 'Validates JavaScript syntax and modern practices',
                'criteria': ['No console statements', 'No eval', 'ES6+ syntax', 'Error handling']
            },
            {
                'id': 4,
                'name': 'Accessibility (WCAG 2.1)',
                'description': 'Validates WCAG 2.1 accessibility compliance',
                'criteria': ['Alt text', 'ARIA labels', 'Semantic HTML', 'Keyboard navigation', 'Color contrast']
            },
            {
                'id': 5,
                'name': 'SEO Optimization',
                'description': 'Validates SEO best practices',
                'criteria': ['Meta tags', 'Title', 'Description', 'Open Graph', 'Heading structure']
            },
            {
                'id': 6,
                'name': 'Performance',
                'description': 'Validates performance optimization',
                'criteria': ['File sizes', 'Minification', 'Image optimization', 'Lazy loading', 'Caching']
            },
            {
                'id': 7,
                'name': 'Security',
                'description': 'Validates security best practices',
                'criteria': ['HTTPS', 'CSP', 'XSS prevention', 'Secure headers', 'CSRF protection']
            },
            {
                'id': 8,
                'name': 'Browser Compatibility',
                'description': 'Validates cross-browser compatibility',
                'criteria': ['Vendor prefixes', 'Polyfills', 'Feature detection', 'IE11 support']
            },
            {
                'id': 9,
                'name': 'Mobile Responsiveness',
                'description': 'Validates mobile-first responsive design',
                'criteria': ['Viewport', 'Media queries', 'Touch targets', 'Responsive images']
            }
        ],
        'scoring': {
            'excellent': '90-100',
            'good': '75-89',
            'needs_improvement': '60-74',
            'poor': '0-59'
        }
    }
