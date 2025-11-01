# Project Endpoints - PostgreSQL Version
# Migrated from MongoDB to PostgreSQL

from fastapi import HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from db_helpers import (
    get_user_by_id, get_user_projects, get_project_by_id,
    create_project, update_project, get_project_messages,
    create_message, project_to_dict, message_to_dict
)


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = ""


class MessageCreate(BaseModel):
    role: str
    content: str


async def get_projects_endpoint(user_id: str, db: AsyncSession = Depends(get_db)):
    """Get all projects for authenticated user"""
    projects = await get_user_projects(db, user_id, limit=100)
    return [project_to_dict(p) for p in projects]


async def create_project_endpoint(
    project_data: ProjectCreate, 
    user_id: str, 
    db: AsyncSession = Depends(get_db)
):
    """Create a new project"""
    # Verify user exists
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create project
    project_dict = {
        'id': str(uuid.uuid4()),
        'user_id': user_id,
        'name': project_data.name,
        'description': project_data.description or '',
        'status': 'draft',
        'created_at': datetime.now(timezone.utc),
        'updated_at': datetime.now(timezone.utc)
    }
    
    project = await create_project(db, project_dict)
    
    # Create initial message
    message_dict = {
        'id': str(uuid.uuid4()),
        'project_id': project.id,
        'role': 'system',
        'content': f'Project "{project.name}" created',
        'created_at': datetime.now(timezone.utc)
    }
    await create_message(db, message_dict)
    
    return {
        "message": "Project created successfully",
        "project": project_to_dict(project)
    }


async def get_project_endpoint(
    project_id: str, 
    user_id: str, 
    db: AsyncSession = Depends(get_db)
):
    """Get a specific project"""
    project = await get_project_by_id(db, project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return project_to_dict(project)


async def get_project_messages_endpoint(
    project_id: str,
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get all messages for a project"""
    # Verify project exists and belongs to user
    project = await get_project_by_id(db, project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    messages = await get_project_messages(db, project_id)
    return [message_to_dict(m) for m in messages]


async def create_project_message_endpoint(
    project_id: str,
    message_data: MessageCreate,
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Create a new message in project"""
    # Verify project exists and belongs to user
    project = await get_project_by_id(db, project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Create message
    message_dict = {
        'id': str(uuid.uuid4()),
        'project_id': project_id,
        'role': message_data.role,
        'content': message_data.content,
        'created_at': datetime.now(timezone.utc)
    }
    
    message = await create_message(db, message_dict)
    
    return {
        "success": True,
        "message": message_to_dict(message)
    }


async def update_project_code_endpoint(
    project_id: str,
    generated_code: str,
    template_id: Optional[str],
    build_time: Optional[float],
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Update project with generated code"""
    # Verify project exists and belongs to user
    project = await get_project_by_id(db, project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Update project
    updates = {
        'generated_code': generated_code,
        'status': 'completed',
        'updated_at': datetime.now(timezone.utc)
    }
    
    if template_id:
        updates['template_id'] = template_id
    
    if build_time:
        updates['build_time'] = build_time
    
    await update_project(db, project_id, updates)
    
    return {"success": True}


async def delete_project_endpoint(
    project_id: str,
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a project"""
    # Verify project exists and belongs to user
    project = await get_project_by_id(db, project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Delete project (cascade will delete messages)
    from sqlalchemy import delete
    from database import Project
    await db.execute(delete(Project).where(Project.id == project_id))
    await db.commit()
    
    return {"message": "Project deleted successfully"}
