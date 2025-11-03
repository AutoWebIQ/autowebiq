# Simple, Stable JWT Authentication
from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from passlib.hash import bcrypt
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRATION_HOURS, db, INITIAL_CREDITS
import uuid

security = HTTPBearer()

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return bcrypt.verify(plain_password, hashed_password)

def create_access_token(user_id: str) -> str:
    """Create JWT token"""
    expire = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    payload = {
        'user_id': user_id,
        'exp': expire
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_token(token: str) -> dict:
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='Token expired')
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail='Invalid token')

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Get current user from token"""
    token = credentials.credentials
    payload = decode_token(token)
    user_id = payload.get('user_id')
    
    if not user_id:
        raise HTTPException(status_code=401, detail='Invalid token')
    
    # Verify user exists
    user = await db.users.find_one({'id': user_id}, {'_id': 0})
    if not user:
        raise HTTPException(status_code=401, detail='User not found')
    
    return user_id

async def register_user(email: str, password: str, name: str = None) -> dict:
    """Register new user"""
    # Check if user exists
    existing = await db.users.find_one({'email': email}, {'_id': 0})
    if existing:
        raise HTTPException(status_code=400, detail='Email already registered')
    
    # Create user
    user_id = str(uuid.uuid4())
    user = {
        'id': user_id,
        'email': email,
        'password': hash_password(password),
        'name': name or email.split('@')[0],
        'credits': INITIAL_CREDITS,
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    
    await db.users.insert_one(user)
    
    # Create token
    token = create_access_token(user_id)
    
    return {
        'access_token': token,
        'token_type': 'bearer',
        'user': {
            'id': user_id,
            'email': email,
            'name': user['name'],
            'credits': INITIAL_CREDITS
        }
    }

async def login_user(email: str, password: str) -> dict:
    """Login user"""
    # Find user
    user = await db.users.find_one({'email': email}, {'_id': 0})
    if not user:
        raise HTTPException(status_code=401, detail='Invalid credentials')
    
    # Verify password
    if not verify_password(password, user['password']):
        raise HTTPException(status_code=401, detail='Invalid credentials')
    
    # Create token
    token = create_access_token(user['id'])
    
    return {
        'access_token': token,
        'token_type': 'bearer',
        'user': {
            'id': user['id'],
            'email': user['email'],
            'name': user['name'],
            'credits': user.get('credits', 0)
        }
    }
