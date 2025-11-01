# Database Helper Functions for PostgreSQL
# Common queries used across endpoints

from sqlalchemy import select, update as sql_update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Dict
from database import User, Project, ProjectMessage, CreditTransaction, UserSession
from datetime import datetime, timezone

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Get user by email"""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

async def get_user_by_id(db: AsyncSession, user_id: str) -> Optional[User]:
    """Get user by ID"""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()

async def get_user_by_firebase_uid(db: AsyncSession, firebase_uid: str) -> Optional[User]:
    """Get user by Firebase UID"""
    result = await db.execute(select(User).where(User.firebase_uid == firebase_uid))
    return result.scalar_one_or_none()

async def create_user(db: AsyncSession, user_data: Dict) -> User:
    """Create a new user"""
    user = User(**user_data)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def update_user_credits(db: AsyncSession, user_id: str, new_credits: int) -> bool:
    """Update user credits"""
    await db.execute(
        sql_update(User).where(User.id == user_id).values(credits=new_credits)
    )
    await db.commit()
    return True

async def get_user_projects(db: AsyncSession, user_id: str, limit: int = 50) -> List[Project]:
    """Get all projects for a user"""
    result = await db.execute(
        select(Project)
        .where(Project.user_id == user_id)
        .order_by(Project.created_at.desc())
        .limit(limit)
    )
    return result.scalars().all()

async def get_project_by_id(db: AsyncSession, project_id: str) -> Optional[Project]:
    """Get project by ID"""
    result = await db.execute(select(Project).where(Project.id == project_id))
    return result.scalar_one_or_none()

async def create_project(db: AsyncSession, project_data: Dict) -> Project:
    """Create a new project"""
    project = Project(**project_data)
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project

async def update_project(db: AsyncSession, project_id: str, updates: Dict) -> bool:
    """Update a project"""
    await db.execute(
        sql_update(Project).where(Project.id == project_id).values(**updates)
    )
    await db.commit()
    return True

async def get_project_messages(db: AsyncSession, project_id: str) -> List[ProjectMessage]:
    """Get all messages for a project"""
    result = await db.execute(
        select(ProjectMessage)
        .where(ProjectMessage.project_id == project_id)
        .order_by(ProjectMessage.created_at.asc())
    )
    return result.scalars().all()

async def create_message(db: AsyncSession, message_data: Dict) -> ProjectMessage:
    """Create a new message"""
    message = ProjectMessage(**message_data)
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message

async def get_user_transactions(db: AsyncSession, user_id: str, limit: int = 50) -> List[CreditTransaction]:
    """Get credit transactions for a user"""
    result = await db.execute(
        select(CreditTransaction)
        .where(CreditTransaction.user_id == user_id)
        .order_by(CreditTransaction.created_at.desc())
        .limit(limit)
    )
    return result.scalars().all()

async def create_transaction(db: AsyncSession, transaction_data: Dict) -> CreditTransaction:
    """Create a credit transaction"""
    transaction = CreditTransaction(**transaction_data)
    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)
    return transaction

def user_to_dict(user: User) -> Dict:
    """Convert User model to dict"""
    return {
        'id': user.id,
        'email': user.email,
        'name': user.name,
        'credits': user.credits,
        'firebase_uid': user.firebase_uid,
        'github_token': user.github_token,
        'created_at': user.created_at.isoformat() if user.created_at else None
    }

def project_to_dict(project: Project) -> Dict:
    """Convert Project model to dict"""
    return {
        'id': project.id,
        'user_id': project.user_id,
        'name': project.name,
        'description': project.description,
        'generated_code': project.generated_code,
        'status': project.status,
        'template_id': project.template_id,
        'build_time': project.build_time,
        'created_at': project.created_at.isoformat() if project.created_at else None,
        'updated_at': project.updated_at.isoformat() if project.updated_at else None
    }

def message_to_dict(message: ProjectMessage) -> Dict:
    """Convert ProjectMessage model to dict"""
    return {
        'id': message.id,
        'project_id': message.project_id,
        'role': message.role,
        'content': message.content,
        'agent_type': message.agent_type,
        'agent_status': message.agent_status,
        'progress': message.progress,
        'created_at': message.created_at.isoformat() if message.created_at else None
    }

def transaction_to_dict(transaction: CreditTransaction) -> Dict:
    """Convert CreditTransaction model to dict"""
    return {
        'id': transaction.id,
        'user_id': transaction.user_id,
        'transaction_type': transaction.transaction_type,
        'amount': transaction.amount,
        'balance_before': transaction.balance_before,
        'balance_after': transaction.balance_after,
        'status': transaction.status,
        'description': transaction.description,
        'extra_data': transaction.extra_data,
        'created_at': transaction.created_at.isoformat() if transaction.created_at else None
    }
