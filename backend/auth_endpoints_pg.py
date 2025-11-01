# Auth Endpoints - PostgreSQL Version
# Migrated from MongoDB to PostgreSQL

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext
import jwt
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db, User
from db_helpers import (
    get_user_by_email, get_user_by_firebase_uid, 
    create_user, user_to_dict
)
from constants import INITIAL_FREE_CREDITS

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION = timedelta(days=30)

# Import JWT_SECRET from server.py after it loads .env
def get_jwt_secret():
    """Get JWT secret from server module"""
    import server
    return server.JWT_SECRET

# Pydantic models
class UserRegister(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class FirebaseSyncRequest(BaseModel):
    firebase_uid: str
    email: str
    display_name: Optional[str] = None

class GoogleAuthRequest(BaseModel):
    token: str
    email: str
    name: str
    picture: Optional[str] = None


async def register_endpoint(user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    existing = await get_user_by_email(db, user_data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user_dict = {
        'id': str(uuid.uuid4()),
        'email': user_data.email,
        'name': user_data.username,
        'password_hash': pwd_context.hash(user_data.password),
        'credits': INITIAL_FREE_CREDITS,
        'created_at': datetime.now(timezone.utc),
        'updated_at': datetime.now(timezone.utc)
    }
    
    user = await create_user(db, user_dict)
    
    # Generate JWT
    token = jwt.encode(
        {"user_id": user.id, "exp": datetime.now(timezone.utc) + JWT_EXPIRATION},
        get_jwt_secret(),
        algorithm=JWT_ALGORITHM
    )
    
    return {
        "message": f"Registration successful! You've been granted {INITIAL_FREE_CREDITS} free credits.",
        "token": token,
        "user": user_to_dict(user)
    }


async def login_endpoint(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    """Login user"""
    user = await get_user_by_email(db, user_data.email)
    
    if not user or not pwd_context.verify(user_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Generate JWT
    token = jwt.encode(
        {"user_id": user.id, "exp": datetime.now(timezone.utc) + JWT_EXPIRATION},
        get_jwt_secret(),
        algorithm=JWT_ALGORITHM
    )
    
    return {
        "message": "Login successful",
        "token": token,
        "user": user_to_dict(user)
    }


async def get_current_user_endpoint(user_id: str, db: AsyncSession = Depends(get_db)):
    """Get current user info"""
    from db_helpers import get_user_by_id
    user = await get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get projects count
    from db_helpers import get_user_projects
    projects = await get_user_projects(db, user_id)
    
    user_dict = user_to_dict(user)
    user_dict['projects_count'] = len(projects)
    
    return user_dict


async def google_auth_endpoint(auth_data: GoogleAuthRequest, db: AsyncSession = Depends(get_db)):
    """Google OAuth authentication"""
    # Check if user exists
    existing_user = await get_user_by_email(db, auth_data.email)
    
    if existing_user:
        # Update existing user
        from sqlalchemy import update as sql_update
        await db.execute(
            sql_update(User)
            .where(User.id == existing_user.id)
            .values(
                name=auth_data.name or existing_user.name,
                updated_at=datetime.now(timezone.utc)
            )
        )
        await db.commit()
        user = existing_user
    else:
        # Create new user
        user_dict = {
            'id': str(uuid.uuid4()),
            'email': auth_data.email,
            'name': auth_data.name,
            'password_hash': '',  # No password for OAuth users
            'credits': INITIAL_FREE_CREDITS,
            'created_at': datetime.now(timezone.utc),
            'updated_at': datetime.now(timezone.utc)
        }
        user = await create_user(db, user_dict)
    
    # Generate JWT
    token = jwt.encode(
        {"user_id": user.id, "exp": datetime.now(timezone.utc) + JWT_EXPIRATION},
        get_jwt_secret(),
        algorithm=JWT_ALGORITHM
    )
    
    return {
        "message": "Google authentication successful",
        "token": token,
        "user": user_to_dict(user)
    }


async def firebase_sync_endpoint(sync_data: FirebaseSyncRequest, db: AsyncSession = Depends(get_db)):
    """Sync Firebase user with backend"""
    # Check if user exists by Firebase UID
    existing_user = await get_user_by_firebase_uid(db, sync_data.firebase_uid)
    
    if existing_user:
        user = existing_user
    else:
        # Check by email
        user = await get_user_by_email(db, sync_data.email)
        
        if not user:
            # Create new user
            user_dict = {
                'id': str(uuid.uuid4()),
                'email': sync_data.email,
                'name': sync_data.display_name or sync_data.email.split('@')[0],
                'firebase_uid': sync_data.firebase_uid,
                'password_hash': '',
                'credits': INITIAL_FREE_CREDITS,
                'created_at': datetime.now(timezone.utc),
                'updated_at': datetime.now(timezone.utc)
            }
            user = await create_user(db, user_dict)
    
    # Generate JWT
    token = jwt.encode(
        {"user_id": user.id, "exp": datetime.now(timezone.utc) + JWT_EXPIRATION},
        get_jwt_secret(),
        algorithm=JWT_ALGORITHM
    )
    
    return {
        "success": True,
        "token": token,
        "user": user_to_dict(user)
    }
