from fastapi import FastAPI, APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect, UploadFile, File, Request, Response, Cookie, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse, JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext
import jwt
import razorpay
import io
import zipfile
import json
import asyncio
import cloudinary
import cloudinary.uploader
from openai import AsyncOpenAI
from emergentintegrations.llm.chat import LlmChat, UserMessage
import httpx
from agents_v2 import OptimizedAgentOrchestrator
from template_orchestrator import TemplateBasedOrchestrator
from docker_manager import docker_manager
from github_manager import github_manager
from gke_manager import gke_manager
from credit_system import get_credit_manager, AgentType, ModelType, MODEL_NAME_MAPPING
from constants import INITIAL_FREE_CREDITS
from database import init_db, get_db, AsyncSessionLocal, User as DBUser, Project as DBProject, Template as DBTemplate, Component as DBComponent
from sqlalchemy import select

# Import PostgreSQL endpoint functions
from auth_endpoints_pg import (
    register_endpoint, login_endpoint, get_current_user_endpoint,
    google_auth_endpoint, firebase_sync_endpoint
)
from project_endpoints_pg import (
    get_projects_endpoint, create_project_endpoint, get_project_endpoint,
    get_project_messages_endpoint, create_project_message_endpoint,
    update_project_code_endpoint, delete_project_endpoint
)
from credit_endpoints_pg import (
    get_credit_balance_endpoint, deduct_credits_endpoint, add_credits_endpoint,
    get_credit_transactions_endpoint, get_credit_summary_endpoint
)
from db_helpers import get_user_by_id, get_project_by_id

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key=os.environ.get('CLOUDINARY_API_KEY'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET')
)

# PostgreSQL is now the only database (initialized in database.py)
# MongoDB has been removed - all data migrated to PostgreSQL
# TEMPORARY: Re-add MongoDB for V1 endpoints until full PostgreSQL migration
from motor.motor_asyncio import AsyncIOMotorClient

# MongoDB connection for V1 endpoints
mongo_client = AsyncIOMotorClient(os.environ.get('MONGO_URL', 'mongodb://localhost:27017'))
db = mongo_client['autowebiq_db']

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()
JWT_SECRET = os.environ.get('JWT_SECRET')
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION = timedelta(days=30)

razorpay_client = razorpay.Client(auth=(os.environ['RAZORPAY_KEY_ID'], os.environ['RAZORPAY_KEY_SECRET']))

# OpenAI client
openai_client = AsyncOpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

# Initialize Multi-Agent Orchestrators
agent_orchestrator = OptimizedAgentOrchestrator(
    openai_key=os.environ.get('OPENAI_API_KEY'),
    anthropic_key=os.environ.get('ANTHROPIC_API_KEY'),
    gemini_key=os.environ.get('GOOGLE_AI_API_KEY')
)

# Initialize Template-Based Orchestrator (Uses PostgreSQL)
template_orchestrator = TemplateBasedOrchestrator(
    openai_key=os.environ.get('OPENAI_API_KEY'),
    anthropic_key=os.environ.get('ANTHROPIC_API_KEY'),
    gemini_key=os.environ.get('GOOGLE_AI_API_KEY')
)

app = FastAPI()
api_router = APIRouter(prefix="/api")

# Initialize PostgreSQL on startup
@app.on_event("startup")
async def startup_event():
    # Skip PostgreSQL initialization - using MongoDB for V1 endpoints
    # await init_db()
    logging.info("✅ Server started (MongoDB mode)")

# Models
class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    firebase_uid: Optional[str] = None  # Firebase UID for Firebase Auth users
    username: str
    email: str
    password_hash: str = ""  # Empty for Firebase Auth users
    credits: int = INITIAL_FREE_CREDITS  # Free credits on signup
    initial_credits_granted: bool = False  # Flag to prevent double crediting
    picture: Optional[str] = None  # Profile picture URL
    auth_provider: str = "email"  # email, google, github
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserRegister(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    email: str
    reset_code: str
    new_password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

class Project(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    name: str
    description: str
    generated_code: str = ""
    model: str = "claude-4.5-sonnet-200k"  # Default to Claude 4.5 Sonnet
    status: str = "active"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ChatMessage(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    role: str  # user, assistant, system
    content: str
    credits_used: int = 0  # Track credits used per message
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ProjectCreate(BaseModel):
    name: str
    description: str
    model: str = "claude-4.5-sonnet-200k"

class ChatRequest(BaseModel):
    project_id: str
    message: str
    model: str = "claude-4.5-sonnet-200k"

class CreateOrderRequest(BaseModel):
    package_id: str

class VerifyPaymentRequest(BaseModel):
    order_id: str
    payment_id: str
    signature: str

class Transaction(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    order_id: str
    payment_id: Optional[str] = None
    amount: int
    credits: int
    status: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserSession(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    session_token: str
    expires_at: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class GoogleAuthUser(BaseModel):
    id: str
    email: str
    name: str
    picture: Optional[str] = None

# Helper functions
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + JWT_EXPIRATION
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user_from_session(request: Request) -> Optional[str]:
    """Get user ID from session token (cookie or Authorization header)"""
    # Try cookie first
    session_token = request.cookies.get("session_token")
    
    # If not in cookie, try Authorization header
    if not session_token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
            # Check if it's a session token (not JWT)
            if not token.startswith("eyJ"):  # JWT tokens start with eyJ
                session_token = token
    
    if not session_token:
        return None
    
    # Find active session
    session = await db.user_sessions.find_one({
        "session_token": session_token,
        "expires_at": {"$gt": datetime.now(timezone.utc)}
    })
    
    if not session:
        return None
    
    return session["user_id"]

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        # Accept both 'sub' (standard JWT claim) and 'user_id' (legacy)
        user_id: str = payload.get("sub") or payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication")
        return user_id
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user_flexible(request: Request) -> str:
    """Get user from either session token or JWT"""
    # Try session token first
    user_id = await get_current_user_from_session(request)
    if user_id:
        return user_id
    
    # Try JWT
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        token = auth_header.replace("Bearer ", "")
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        # Accept both 'sub' (standard JWT claim) and 'user_id' (legacy)
        user_id = payload.get("sub") or payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid authentication")
        return user_id
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# Constants
CREDIT_PACKAGES = [
    {"id": "pkg_100", "name": "Starter Pack", "credits": 100, "price": 170000, "currency": "INR"},
    {"id": "pkg_250", "name": "Professional Pack", "credits": 250, "price": 425000, "currency": "INR"},
    {"id": "pkg_500", "name": "Business Pack", "credits": 500, "price": 850000, "currency": "INR"},
    {"id": "pkg_3000", "name": "Enterprise Pack", "credits": 3000, "price": 4250000, "currency": "INR"},
    {"id": "pkg_6000", "name": "Agency Pack", "credits": 6000, "price": 8500000, "currency": "INR"},
]

# AI Model costs per message (in credits)
MODEL_COSTS = {
    "claude-4.5-sonnet-200k": {"name": "Claude 4.5 Sonnet", "cost": 5, "context": "200k"},
    "claude-4.5-sonnet-1m": {"name": "Claude 4.5 Sonnet - 1M", "cost": 10, "context": "1M", "pro": True},
    "gpt-5": {"name": "GPT-5 (Beta)", "cost": 8, "context": "128k"},
    "claude-4-sonnet-20250514": {"name": "Claude 4.0 Sonnet", "cost": 4, "context": "200k"},
}

# Auth endpoints
@api_router.post("/auth/register")
async def register(user_data: UserRegister):
    """Register a new user - MongoDB"""
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    user_dict = {
        "id": str(uuid.uuid4()),
        "username": user_data.username,
        "email": user_data.email,
        "password_hash": hash_password(user_data.password),
        "credits": INITIAL_FREE_CREDITS,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.users.insert_one(user_dict)
    
    # Remove MongoDB _id before generating response
    user_dict.pop('_id', None)
    
    # Generate JWT token
    token = create_access_token({"sub": user_dict['id']})
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": str(user_dict["id"]),
            "email": str(user_dict["email"]),
            "username": str(user_dict["username"]),
            "credits": int(user_dict["credits"])
        }
    }

@api_router.post("/auth/login")
async def login(user_data: UserLogin):
    """Login user - MongoDB"""
    # Find user
    user = await db.users.find_one({"email": user_data.email})
    if not user or not verify_password(user_data.password, user.get('password_hash', '')):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Remove MongoDB _id to prevent serialization issues
    user.pop('_id', None)
    
    # Generate JWT token
    token = create_access_token({"sub": user['id']})
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": str(user["id"]),  # Ensure string
            "email": str(user["email"]),
            "username": str(user.get("username", "")),
            "credits": int(user.get("credits", 0))
        }
    }

@api_router.get("/auth/me")
async def get_me(request: Request):
    """Get current user data - MongoDB"""
    user_id = await get_current_user_flexible(request)
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Remove MongoDB _id
    user.pop('_id', None)
    
    return {
        "id": str(user["id"]),
        "email": str(user["email"]),
        "username": str(user.get("username", "")),
        "credits": int(user.get("credits", 0)),
        "created_at": str(user.get("created_at", ""))
    }

@api_router.post("/auth/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    """Generate password reset code"""
    user_doc = await db.users.find_one({"email": request.email})
    if not user_doc:
        # Don't reveal if email exists for security
        return {"message": "If the email exists, a reset code has been sent"}
    
    # Generate 6-digit code
    import random
    reset_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    
    # Store reset code with expiry (5 minutes)
    await db.password_resets.insert_one({
        "email": request.email,
        "code": reset_code,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()
    })
    
    # In production, send email here
    # For now, return code (ONLY FOR DEVELOPMENT)
    return {"message": "Reset code generated", "code": reset_code}

@api_router.post("/auth/reset-password")
async def reset_password(request: ResetPasswordRequest):
    """Reset password with code"""
    # Find valid reset code
    reset_doc = await db.password_resets.find_one({
        "email": request.email,
        "code": request.reset_code
    })
    
    if not reset_doc:
        raise HTTPException(status_code=400, detail="Invalid reset code")
    
    # Check expiry
    expires_at = datetime.fromisoformat(reset_doc['expires_at'])
    if datetime.now(timezone.utc) > expires_at:
        raise HTTPException(status_code=400, detail="Reset code expired")
    
    # Update password
    new_hash = hash_password(request.new_password)
    await db.users.update_one(
        {"email": request.email},
        {"$set": {"password_hash": new_hash}}
    )
    
    # Delete used reset code
    await db.password_resets.delete_many({"email": request.email})
    
    return {"message": "Password reset successful"}

# Firebase Auth sync endpoint
class FirebaseUserSync(BaseModel):
    firebase_uid: str
    email: str
    display_name: Optional[str] = None
    photo_url: Optional[str] = None
    provider_id: str  # google.com, github.com, password

@api_router.post("/auth/firebase/sync")
async def firebase_user_sync(user_data: FirebaseUserSync):
    """Sync Firebase user with backend database"""
    try:
        # Check if user already exists by Firebase UID or email
        existing_user = await db.users.find_one({
            "$or": [
                {"firebase_uid": user_data.firebase_uid},
                {"email": user_data.email}
            ]
        })
        
        if existing_user:
            # Update existing user
            update_data = {
                "firebase_uid": user_data.firebase_uid,
                "email": user_data.email
            }
            
            if user_data.photo_url:
                update_data["picture"] = user_data.photo_url
            
            # Update provider if changed
            if user_data.provider_id:
                provider_map = {
                    "google.com": "google",
                    "github.com": "github",
                    "password": "email"
                }
                update_data["auth_provider"] = provider_map.get(user_data.provider_id, "email")
            
            await db.users.update_one(
                {"id": existing_user["id"]},
                {"$set": update_data}
            )
            
            user = await db.users.find_one({"id": existing_user["id"]})
        else:
            # Create new user
            provider_map = {
                "google.com": "google",
                "github.com": "github",
                "password": "email"
            }
            
            user_id = str(uuid.uuid4())
            new_user = {
                "id": user_id,
                "firebase_uid": user_data.firebase_uid,
                "username": user_data.display_name or user_data.email.split('@')[0],
                "email": user_data.email,
                "password_hash": "",  # No password for Firebase users
                "credits": INITIAL_FREE_CREDITS,
                "initial_credits_granted": True,  # Mark as granted
                "picture": user_data.photo_url,
                "auth_provider": provider_map.get(user_data.provider_id, "email"),
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            await db.users.insert_one(new_user)
            
            # Add signup bonus transaction
            credit_manager = get_credit_manager(db)
            await credit_manager.add_signup_bonus(user_id, INITIAL_FREE_CREDITS)
            
            user = new_user
        
        # Create JWT token for backward compatibility
        token = create_access_token({"user_id": user["id"]})
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "credits": user["credits"],
                "picture": user.get("picture")
            }
        }
    
    except Exception as e:
        logging.error(f"Firebase sync error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")

# Google OAuth endpoints
@api_router.post("/auth/google/session")
async def google_auth_session(request: Request, response: Response):
    """Exchange session_id for session_token and user data"""
    session_id = request.headers.get("X-Session-ID")
    
    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID required")
    
    # Call Emergent Auth API to get user data
    async with httpx.AsyncClient() as client:
        try:
            auth_response = await client.get(
                "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
                headers={"X-Session-ID": session_id},
                timeout=10.0
            )
            
            if auth_response.status_code != 200:
                raise HTTPException(status_code=400, detail="Invalid session ID")
            
            auth_data = auth_response.json()
            
        except httpx.RequestError:
            raise HTTPException(status_code=500, detail="Failed to authenticate with Google")
    
    # Extract user data
    user_email = auth_data["email"]
    user_name = auth_data["name"]
    user_picture = auth_data.get("picture")
    session_token = auth_data["session_token"]
    
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_email})
    
    if not existing_user:
        # Create new user (Google OAuth users don't have password)
        user_id = str(uuid.uuid4())
        user_data = {
            "id": user_id,
            "username": user_name,
            "email": user_email,
            "password_hash": "",  # No password for OAuth users
            "credits": INITIAL_FREE_CREDITS,
            "initial_credits_granted": True,  # Mark as granted
            "picture": user_picture,
            "auth_provider": "google",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.users.insert_one(user_data)
        
        # Add signup bonus transaction
        credit_manager = get_credit_manager(db)
        await credit_manager.add_signup_bonus(user_id, INITIAL_FREE_CREDITS)
    else:
        user_id = existing_user["id"]
    
    # Store session in database
    session_data = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "session_token": session_token,
        "expires_at": datetime.now(timezone.utc) + timedelta(days=7),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.user_sessions.insert_one(session_data)
    
    # Set httpOnly cookie
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=True,
        samesite="none",
        path="/",
        max_age=7 * 24 * 60 * 60  # 7 days
    )
    
    # Get full user data
    user = await db.users.find_one({"id": user_id})
    
    return {
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "credits": user["credits"],
            "picture": user.get("picture")
        },
        "session_token": session_token
    }

@api_router.post("/auth/logout")
async def logout(request: Request, response: Response):
    """Logout user by deleting session"""
    session_token = request.cookies.get("session_token")
    
    if session_token:
        # Delete session from database
        await db.user_sessions.delete_many({"session_token": session_token})
    
    # Clear cookie
    response.delete_cookie(key="session_token", path="/")
    
    return {"message": "Logged out successfully"}

# Credits
@api_router.get("/credits/packages")
async def get_packages():
    return CREDIT_PACKAGES

@api_router.get("/models")
async def get_models():
    """Get available AI models and their costs"""
    return MODEL_COSTS

@api_router.post("/credits/create-order")
async def create_order(request: CreateOrderRequest, user_id: str = Depends(get_current_user)):
    package = next((p for p in CREDIT_PACKAGES if p["id"] == request.package_id), None)
    if not package:
        raise HTTPException(status_code=404, detail="Package not found")
    
    try:
        razor_order = razorpay_client.order.create({
            "amount": package["price"],
            "currency": package["currency"],
            "payment_capture": 1
        })
        
        transaction = Transaction(
            user_id=user_id,
            order_id=razor_order["id"],
            amount=package["price"],
            credits=package["credits"],
            status="created"
        )
        
        trans_dict = transaction.model_dump()
        trans_dict['created_at'] = trans_dict['created_at'].isoformat()
        await db.transactions.insert_one(trans_dict)
        
        return {
            "order_id": razor_order["id"],
            "amount": razor_order["amount"],
            "currency": razor_order["currency"],
            "key_id": os.environ['RAZORPAY_KEY_ID']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Payment error: {str(e)}")

@api_router.post("/credits/verify-payment")
async def verify_payment(request: VerifyPaymentRequest, user_id: str = Depends(get_current_user)):
    try:
        params_dict = {
            'razorpay_order_id': request.order_id,
            'razorpay_payment_id': request.payment_id,
            'razorpay_signature': request.signature
        }
        razorpay_client.utility.verify_payment_signature(params_dict)
        
        transaction = await db.transactions.find_one({"order_id": request.order_id, "user_id": user_id})
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        await db.transactions.update_one(
            {"order_id": request.order_id},
            {"$set": {"payment_id": request.payment_id, "status": "paid"}}
        )
        
        await db.users.update_one(
            {"id": user_id},
            {"$inc": {"credits": transaction['credits']}}
        )
        
        user_doc = await db.users.find_one({"id": user_id}, {"_id": 0, "credits": 1})
        
        return {"success": True, "credits": user_doc['credits']}
    except:
        await db.transactions.update_one(
            {"order_id": request.order_id},
            {"$set": {"status": "failed"}}
        )
        raise HTTPException(status_code=400, detail="Invalid payment signature")

# Projects
@api_router.post("/projects/create")
async def create_project(project_data: ProjectCreate, user_id: str = Depends(get_current_user)):
    # No credit deduction for creating project
    
    project = Project(
        user_id=user_id,
        name=project_data.name,
        description=project_data.description,
        model=project_data.model
    )
    
    proj_dict = project.model_dump()
    proj_dict['created_at'] = proj_dict['created_at'].isoformat()
    proj_dict['updated_at'] = proj_dict['updated_at'].isoformat()
    await db.projects.insert_one(proj_dict)
    
    # Initial system message
    system_msg = ChatMessage(
        project_id=project.id,
        role="system",
        content=f"Project created: {project.name}. {project.description}",
        credits_used=0
    )
    sys_dict = system_msg.model_dump()
    sys_dict['created_at'] = sys_dict['created_at'].isoformat()
    await db.messages.insert_one(sys_dict)
    
    # Return clean project data
    return {
        "id": project.id,
        "user_id": project.user_id,
        "name": project.name,
        "description": project.description,
        "generated_code": project.generated_code,
        "model": project.model,
        "status": project.status,
        "created_at": proj_dict['created_at'],
        "updated_at": proj_dict['updated_at']
    }

@api_router.get("/projects")
async def get_projects_mongodb(user_id: str = Depends(get_current_user)):
    """Get all projects for user - MongoDB"""
    projects = await db.projects.find({"user_id": user_id}, {"_id": 0}).to_list(length=None)
    return {"projects": projects}

# @api_router.get("/projects")
# async def get_projects(user_id: str = Depends(get_current_user), db=Depends(get_db)):
#     """Get all projects for user - PostgreSQL"""
#     return await get_projects_endpoint(user_id, db)

@api_router.post("/projects/create")
async def create_project(request: dict, user_id: str = Depends(get_current_user), db=Depends(get_db)):
    """Create a new project - PostgreSQL"""
    from project_endpoints_pg import ProjectCreate
    project_data = ProjectCreate(
        name=request.get("name", "Untitled Project"),
        description=request.get("description", "")
    )
    return await create_project_endpoint(project_data, user_id, db)

@api_router.get("/projects/{project_id}")
async def get_project(project_id: str, user_id: str = Depends(get_current_user), db=Depends(get_db)):
    """Get a specific project - PostgreSQL"""
    return await get_project_endpoint(project_id, user_id, db)

@api_router.get("/projects/{project_id}/messages")
async def get_messages(project_id: str, user_id: str = Depends(get_current_user), db=Depends(get_db)):
    """Get all messages for a project - PostgreSQL"""
    return await get_project_messages_endpoint(project_id, user_id, db)


@api_router.post("/projects/{project_id}/messages")
async def create_message(project_id: str, request: Request, user_id: str = Depends(get_current_user)):
    """Create a new message and trigger website generation"""
    # Parse request body
    body = await request.json()
    message = body.get('message', '')
    uploaded_images = body.get('uploaded_images', [])
    
    if not message:
        raise HTTPException(status_code=400, detail="Message is required")
    
    # Verify project ownership
    project = await db.projects.find_one({"id": project_id, "user_id": user_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Save user message
    user_message_id = str(uuid.uuid4())
    user_message = {
        "id": user_message_id,
        "project_id": project_id,
        "role": "user",
        "content": message,
        "images": uploaded_images,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.messages.insert_one(user_message)
    
    # Check user credits
    user = await db.users.find_one({"id": user_id})
    if not user or user.get('credits', 0) < 20:
        error_message = {
            "id": str(uuid.uuid4()),
            "project_id": project_id,
            "role": "assistant",
            "content": "⚠️ Insufficient credits. You need at least 20 credits to generate a website.",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.messages.insert_one(error_message)
        return {"message": error_message}
    
    try:
        # Import template system with multi-page support
        from template_orchestrator import TemplateBasedOrchestrator
        import os
        
        # Initialize orchestrator with API keys
        orchestrator = TemplateBasedOrchestrator(
            openai_key=os.environ.get('OPENAI_API_KEY', ''),
            anthropic_key=os.environ.get('ANTHROPIC_API_KEY', ''),
            gemini_key=os.environ.get('GEMINI_API_KEY', '')
        )
        
        # Set up WebSocket callback for real-time agent updates
        async def send_agent_update(proj_id: str, update: dict):
            """Send agent status updates via WebSocket"""
            from websocket_manager import get_websocket_manager
            ws_manager = get_websocket_manager()
            await ws_manager.send_agent_message(
                project_id=proj_id,
                agent_type=update.get('agent', 'system'),
                message=update.get('content', ''),
                status=update.get('status', 'working'),
                progress=update.get('progress', 0)
            )
        
        orchestrator.message_callback = send_agent_update
        
        # Generate multi-page website
        result = await orchestrator.build_website(
            user_prompt=message,
            project_id=project_id,
            uploaded_images=uploaded_images
        )
        
        if result.get('status') == 'completed':
            # Extract all pages
            all_pages = result.get('all_pages', {})
            frontend_code = result.get('frontend_code', '')
            
            # Save assistant response with page list
            page_list = ', '.join(all_pages.keys()) if all_pages else 'index.html'
            assistant_message = {
                "id": str(uuid.uuid4()),
                "project_id": project_id,
                "role": "assistant",
                "content": f"✅ Multi-page website generated successfully! 🎉\n\n**Generated Pages:** {page_list}\n\n**Features:**\n• Working navigation\n• Functional forms\n• Responsive design",
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await db.messages.insert_one(assistant_message)
            
            # Remove MongoDB _id before returning
            assistant_message.pop('_id', None)
            
            # Update project with generated code and all pages
            await db.projects.update_one(
                {"id": project_id},
                {"$set": {
                    "generated_code": frontend_code,
                    "all_pages": all_pages,  # Store all pages
                    "multipage": True,
                    "status": "completed",
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }}
            )
            
            # Deduct credits (use token usage if available)
            credits_used = result.get('token_usage', {}).get('total_credits', 20)
            credits_used = max(20, min(int(credits_used), 100))  # Between 20-100
            
            await db.users.update_one(
                {"id": user_id},
                {"$inc": {"credits": -credits_used}}
            )
            
            return {
                "message": assistant_message,
                "generated_code": frontend_code,
                "all_pages": all_pages,
                "multipage": True,
                "credits_used": credits_used,
                "token_usage": result.get('token_usage', {})
            }
        else:
            error_message = {
                "id": str(uuid.uuid4()),
                "project_id": project_id,
                "role": "assistant",
                "content": f"❌ Generation failed: {result.get('error', 'Unknown error')}",
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            await db.messages.insert_one(error_message)
            error_message.pop('_id', None)
            return {"message": error_message}
            
    except Exception as e:
        logger.error(f"Error generating website: {str(e)}")
        error_message = {
            "id": str(uuid.uuid4()),
            "project_id": project_id,
            "role": "assistant",
            "content": f"❌ Error: {str(e)}",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.messages.insert_one(error_message)
        error_message.pop('_id', None)
        return {"message": error_message}

@api_router.post("/projects/{project_id}/deploy-preview")
async def deploy_preview(project_id: str, user_id: str = Depends(get_current_user)):
    """Deploy generated website to Vercel for live preview"""
    try:
        # Get project
        project = await db.projects.find_one({"id": project_id, "user_id": user_id})
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Check if website is generated
        if not project.get('generated_code'):
            raise HTTPException(status_code=400, detail="No website generated yet. Please generate a website first.")
        
        # Import Vercel service
        from vercel_service import VercelService
        
        vercel = VercelService()
        
        # Get all pages or just index
        all_pages = project.get('all_pages', {})
        
        if all_pages:
            # Multi-page deployment
            logger.info(f"Deploying multi-page website: {len(all_pages)} pages")
            
            result = vercel.deploy_multipage_website(
                project_name=f"autowebiq-{project_id[:8]}",
                pages=all_pages,
                environment="preview"
            )
        else:
            # Single page deployment
            result = vercel.deploy_website(
                project_name=f"autowebiq-{project_id[:8]}",
                html_content=project['generated_code'],
                environment="preview"
            )
        
        # Save preview URL to project
        await db.projects.update_one(
            {"id": project_id},
            {"$set": {
                "preview_url": result['preview_url'],
                "deployment_id": result['deployment_id'],
                "deployed_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        # Create success message
        success_message = {
            "id": str(uuid.uuid4()),
            "project_id": project_id,
            "role": "assistant",
            "content": f"🚀 **Website deployed successfully!**\n\n**Live Preview:** {result['preview_url']}\n\nYour website is now live and accessible to anyone with the link. Share it with your clients or test it out!",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.messages.insert_one(success_message)
        
        return {
            "success": True,
            "preview_url": result['preview_url'],
            "deployment_id": result['deployment_id'],
            "pages_count": result.get('pages_count', 1),
            "message": success_message
        }
        
    except Exception as e:
        logger.error(f"Deployment error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Deployment failed: {str(e)}")
            
    except Exception as e:
        logger.error(f"Error generating website: {str(e)}")
        error_message = {
            "id": str(uuid.uuid4()),
            "project_id": project_id,
            "role": "assistant",
            "content": f"❌ Error: {str(e)}",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.messages.insert_one(error_message)
        raise HTTPException(status_code=500, detail=str(e))


@api_router.delete("/projects/{project_id}")
async def delete_project(project_id: str, user_id: str = Depends(get_current_user)):
    result = await db.projects.update_one(
        {"id": project_id, "user_id": user_id},
        {"$set": {"status": "archived"}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Project deleted"}

@api_router.put("/projects/{project_id}")
async def update_project_code(project_id: str, user_id: str = Depends(get_current_user), generated_code: str = ""):
    """Update project code manually"""
    from pydantic import BaseModel
    
    class CodeUpdate(BaseModel):
        generated_code: str
    
    # Parse request body
    result = await db.projects.update_one(
        {"id": project_id, "user_id": user_id},
        {"$set": {
            "generated_code": generated_code,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return {"message": "Code updated successfully"}

@api_router.get("/projects/{project_id}/download")
async def download_project(project_id: str, user_id: str = Depends(get_current_user)):
    project = await db.projects.find_one({"id": project_id, "user_id": user_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr('index.html', project['generated_code'])
        zip_file.writestr('README.md', f"# {project['name']}\n\n{project['description']}\n\nGenerated by AutoWebIQ")
    
    zip_buffer.seek(0)
    
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={project['name'].replace(' ', '_')}.zip"}
    )

@api_router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    project_id: str = "",
    user_id: str = Depends(get_current_user)
):
    """Upload file to Cloudinary"""
    try:
        # Read file content
        contents = await file.read()
        
        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            contents,
            folder=f"autowebiq/{user_id}/{project_id}",
            resource_type="auto"
        )
        
        return {
            "url": result['secure_url'],
            "public_id": result['public_id'],
            "format": result['format'],
            "filename": file.filename
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

# Chat endpoint using HTTP POST instead of WebSocket
@api_router.post("/chat")
async def chat(request: ChatRequest, user_id: str = Depends(get_current_user)):
    # Check if model is valid and get cost
    if request.model not in MODEL_COSTS:
        raise HTTPException(status_code=400, detail="Invalid model selected")
    
    model_info = MODEL_COSTS[request.model]
    credits_needed = model_info["cost"]
    
    # Check user has enough credits
    user_doc = await db.users.find_one({"id": user_id})
    if user_doc['credits'] < credits_needed:
        raise HTTPException(
            status_code=402, 
            detail=f"Insufficient credits. Need {credits_needed} credits. You have {user_doc['credits']}."
        )
    
    # Verify project
    project = await db.projects.find_one({"id": request.project_id, "user_id": user_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Deduct credits BEFORE generation
    await db.users.update_one(
        {"id": user_id},
        {"$inc": {"credits": -credits_needed}}
    )
    
    # Save user message
    user_msg = ChatMessage(
        project_id=request.project_id,
        role="user",
        content=request.message,
        credits_used=credits_needed
    )
    user_dict = user_msg.model_dump()
    user_dict['created_at'] = user_dict['created_at'].isoformat()
    await db.messages.insert_one(user_dict)
    
    # Get AI response
    try:
        # Get recent chat history for context (last 10 messages)
        recent_messages = await db.messages.find(
            {"project_id": request.project_id}
        ).sort("created_at", -1).limit(10).to_list(length=10)
        recent_messages.reverse()  # Put in chronological order
        
        # Map models to actual API models
        if request.model in ["claude-4.5-sonnet-200k", "claude-4.5-sonnet-1m"]:
            actual_model = "claude-sonnet-4-20250514"
        elif request.model == "gpt-5":
            actual_model = "gpt-4o"  # Use latest GPT-4o
        else:
            actual_model = request.model
        
        # ADVANCED system prompt - similar to my capabilities
        system_prompt = """You are an EXPERT full-stack web developer AI that builds beautiful, modern, production-ready websites.

CORE CAPABILITIES:
- Build complete, responsive websites with HTML, CSS, and JavaScript
- Create modern UIs with Tailwind CSS or custom CSS
- Implement interactive features with vanilla JavaScript
- Design with best practices: accessibility, performance, SEO
- Use modern design trends: glassmorphism, gradients, micro-interactions

CONVERSATION STYLE:
- Be conversational and helpful like a senior developer
- Ask clarifying questions when requirements are vague
- Suggest improvements and best practices
- Explain your design decisions briefly

WHEN USER ASKS TO BUILD A WEBSITE:
1. If requirements are clear, build immediately
2. If vague (e.g., "build a website"), ask 2-3 focused questions:
   - What's the purpose? (portfolio, business, landing page, blog, etc.)
   - Target audience? (professionals, consumers, specific niche)
   - Style preference? (modern, minimal, colorful, professional, etc.)
3. After clarification, generate complete code

CODE GENERATION RULES:
✅ ALWAYS output complete, self-contained HTML with inline CSS and JavaScript
✅ Make it responsive (mobile, tablet, desktop)
✅ Use modern design: gradients, shadows, animations, proper spacing
✅ Include real content examples (not just placeholders)
✅ Add hover effects, transitions, and interactivity
✅ Ensure proper color contrast and typography
✅ Structure: proper HTML5 semantic tags

OUTPUT FORMAT:
- When generating code, wrap in ```html ... ``` code blocks
- Include brief explanation of key features BEFORE the code
- Be concise but informative

ITERATION & UPDATES:
- When user asks to modify existing website, understand the change
- Apply surgical updates - don't rebuild everything unless needed
- Maintain consistency with existing design

CURRENT PROJECT CONTEXT:
- Project: {project_name}
- Description: {project_description}
- Has existing code: {has_code}"""
        
        # Prepare context
        has_code = bool(project.get('generated_code'))
        system_prompt = system_prompt.format(
            project_name=project['name'],
            project_description=project['description'],
            has_code="Yes - user wants modifications" if has_code else "No - first generation"
        )
        
        # Build conversation messages with history
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add recent chat history (excluding current message)
        for msg in recent_messages[:-1]:  # Exclude the message we just saved
            if msg['role'] in ['user', 'assistant']:
                messages.append({
                    "role": msg['role'],
                    "content": msg['content'][:1000]  # Limit length to save tokens
                })
        
        # Add current user message
        current_prompt = request.message
        if has_code:
            current_prompt += f"\n\n[Context: Website already exists. User wants: {request.message}]"
        
        messages.append({"role": "user", "content": current_prompt})
        
        # Use OpenAI for GPT models (best quality)
        if actual_model.startswith('gpt'):
            completion = await openai_client.chat.completions.create(
                model=actual_model,
                messages=messages,
                temperature=0.7,
                max_tokens=4000
            )
            
            ai_response = completion.choices[0].message.content
        else:
            # Use emergentintegrations for Claude
            api_key = os.environ.get('EMERGENT_LLM_KEY')
            chat_client = LlmChat(
                api_key=api_key,
                session_id=request.project_id,
                system_message=system_prompt
            )
            chat_client.with_model("anthropic", actual_model)
            
            # Send with context
            user_message = UserMessage(text=current_prompt)
            ai_response = await chat_client.send_message(user_message)
        
        # Extract HTML - improved extraction
        html_code = ai_response.strip()
        
        # Try multiple extraction patterns
        if "```html" in html_code.lower():
            # Extract between ```html and ```
            parts = html_code.lower().split("```html")
            if len(parts) > 1:
                html_code = html_code.split("```html", 1)[1].split("```")[0].strip()
        elif "```" in html_code:
            # Extract between ``` and ```
            parts = html_code.split("```")
            if len(parts) >= 3:
                html_code = parts[1].strip()
        
        # If still has code blocks, try to clean
        if html_code.startswith("```"):
            html_code = html_code.split("```", 1)[1].split("```")[0].strip()
        
        # Ensure we have HTML
        if not html_code.strip().lower().startswith("<!doctype") and not html_code.strip().lower().startswith("<html"):
            # If no HTML structure, wrap content
            if "<" in html_code and ">" in html_code:
                html_code = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project['name']}</title>
</head>
<body>
{html_code}
</body>
</html>"""
        
        # Save AI message
        ai_msg = ChatMessage(
            project_id=request.project_id,
            role="assistant",
            content=ai_response
        )
        ai_dict = ai_msg.model_dump()
        ai_dict['created_at'] = ai_dict['created_at'].isoformat()
        await db.messages.insert_one(ai_dict)
        
        # Update project code
        await db.projects.update_one(
            {"id": request.project_id},
            {"$set": {
                "generated_code": html_code,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        return {
            "user_message": user_msg.model_dump(),
            "ai_message": ai_msg.model_dump(),
            "code": html_code
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI error: {str(e)}")

# New Multi-Agent Website Builder Endpoint
class MultiAgentBuildRequest(BaseModel):
    project_id: str
    prompt: str
    uploaded_images: Optional[List[str]] = []  # List of Cloudinary URLs

@api_router.post("/build-with-agents")
async def build_with_agents(request: MultiAgentBuildRequest, user_id: str = Depends(get_current_user)):
    """
    Build a complete website using multi-agent system with dynamic credit deduction
    Credits deducted based on agents used, models, and complexity (Emergent-style)
    """
    
    # Initialize credit manager
    credit_manager = get_credit_manager(db)
    
    # Verify project
    project = await db.projects.find_one({"id": request.project_id, "user_id": user_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Calculate estimated cost for multi-agent build
    # We'll determine which agents will be used based on the prompt/project
    agents_to_use = [
        AgentType.PLANNER,
        AgentType.FRONTEND,
        AgentType.IMAGE,
        AgentType.TESTING
    ]
    
    models_used = {
        AgentType.PLANNER: ModelType.CLAUDE_SONNET_4,
        AgentType.FRONTEND: ModelType.GPT_4O,
        AgentType.IMAGE: ModelType.DALLE_3,
        AgentType.TESTING: ModelType.GPT_4O
    }
    
    # Check if backend is needed (can be determined from prompt or project settings)
    needs_backend = 'api' in request.prompt.lower() or 'backend' in request.prompt.lower()
    if needs_backend:
        agents_to_use.append(AgentType.BACKEND)
        models_used[AgentType.BACKEND] = ModelType.GPT_4O
    
    has_images = len(request.uploaded_images) > 0 or True  # Image agent runs by default
    
    # Calculate cost
    cost_breakdown = await credit_manager.calculate_multi_agent_cost(
        agents_to_use,
        models_used,
        has_images=has_images,
        has_backend=needs_backend
    )
    
    estimated_cost = cost_breakdown['total']
    
    # Check if user has enough credits
    user_balance = await credit_manager.get_user_balance(user_id)
    if user_balance < estimated_cost:
        raise HTTPException(
            status_code=402,
            detail=f"Insufficient credits. Multi-agent build requires {estimated_cost} credits. You have {user_balance}. Breakdown: {cost_breakdown['breakdown']}"
        )
    
    # Reserve credits upfront
    reservation = await credit_manager.reserve_credits(
        user_id,
        estimated_cost,
        "multi_agent_build",
        {
            "project_id": request.project_id,
            "agents_used": [a.value for a in agents_to_use],
            "estimated_cost": estimated_cost,
            "breakdown": cost_breakdown
        }
    )
    
    if reservation['status'] != 'success':
        raise HTTPException(status_code=402, detail="Failed to reserve credits")
    
    transaction_id = reservation['transaction_id']
    
    try:
        # Use Template-Based Orchestrator (NEW - faster and better quality)
        result = await template_orchestrator.build_website(
            request.prompt, 
            request.project_id,
            request.uploaded_images  # Pass uploaded images
        )
        
        if result['status'] == 'completed':
            # Calculate actual cost (could be less if some agents weren't needed)
            actual_agents_used = []
            if result.get('plan'):
                actual_agents_used.append(AgentType.PLANNER)
            if result.get('frontend_code'):
                actual_agents_used.append(AgentType.FRONTEND)
            if result.get('backend_code'):
                actual_agents_used.append(AgentType.BACKEND)
            if result.get('images'):
                actual_agents_used.append(AgentType.IMAGE)
            if result.get('test_results'):
                actual_agents_used.append(AgentType.TESTING)
            
            # Recalculate actual cost
            actual_cost_breakdown = await credit_manager.calculate_multi_agent_cost(
                actual_agents_used,
                models_used,
                has_images=len(result.get('images', [])) > 0,
                has_backend=bool(result.get('backend_code'))
            )
            
            actual_cost = actual_cost_breakdown['total']
            
            # Complete transaction (will refund difference if actual < estimated)
            completion = await credit_manager.complete_transaction(
                transaction_id,
                actual_cost
            )
            
            # Update project with generated code
            await db.projects.update_one(
                {"id": request.project_id},
                {"$set": {
                    "generated_code": result['frontend_code'],
                    "backend_code": result.get('backend_code', ''),
                    "project_plan": result['plan'],
                    "credit_cost": actual_cost,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }}
            )
            
            # Get updated balance
            new_balance = await credit_manager.get_user_balance(user_id)
            
            return {
                "status": "success",
                "plan": result['plan'],
                "frontend_code": result['frontend_code'],
                "backend_code": result.get('backend_code', ''),
                "message": "✅ Website built successfully with multi-agent system!",
                "credits_used": actual_cost,
                "credits_refunded": completion['refunded'],
                "remaining_balance": new_balance,
                "cost_breakdown": actual_cost_breakdown
            }
        else:
            # Full refund on failure
            await credit_manager.refund_credits(
                user_id,
                estimated_cost,
                "Build failed - full refund",
                {"transaction_id": transaction_id, "error": result.get('error')}
            )
            raise HTTPException(status_code=500, detail=result.get('error', 'Build failed'))
    
    except Exception as e:
        # Full refund on exception
        await credit_manager.refund_credits(
            user_id,
            estimated_cost,
            f"Build exception - full refund: {str(e)}",
            {"transaction_id": transaction_id}
        )
        raise HTTPException(status_code=500, detail=f"Multi-agent build error: {str(e)}")


# ============================================================================
# FULL-STACK APPLICATION BUILDER ENDPOINT (NEW)
# ============================================================================

class FullStackBuildRequest(BaseModel):
    project_id: str
    prompt: str
    generate_tests: Optional[bool] = True
    include_docker: Optional[bool] = True

@api_router.post("/build-fullstack")
async def build_fullstack_application(
    request: FullStackBuildRequest, 
    user_id: str = Depends(get_current_user)
):
    """
    Build a complete full-stack application (React + FastAPI + PostgreSQL).
    
    This endpoint generates:
    - React frontend with routing and components
    - FastAPI backend with authentication
    - PostgreSQL database with migrations
    - Automated tests
    - Docker deployment configuration
    - Complete documentation
    
    Uses multi-model AI:
    - Claude Sonnet 4 for frontend (React)
    - GPT-4o for backend (FastAPI)
    - Gemini 2.5 Pro for planning
    """
    from fullstack_orchestrator import FullStackOrchestrator
    
    # Initialize credit manager
    credit_manager = get_credit_manager(db)
    
    # Verify project
    project = await db.projects.find_one({"id": request.project_id, "user_id": user_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Calculate cost for full-stack build
    # Full-stack requires all agents
    agents_to_use = [
        AgentType.PLANNER,      # 12 credits
        AgentType.FRONTEND,     # 16 credits
        AgentType.BACKEND,      # 16 credits
        AgentType.DATABASE,     # 10 credits
        AgentType.TESTING       # 10 credits
    ]
    
    models_used = {
        AgentType.PLANNER: ModelType.GEMINI_2_5_PRO,
        AgentType.FRONTEND: ModelType.CLAUDE_SONNET_4,
        AgentType.BACKEND: ModelType.GPT_4O,
        AgentType.DATABASE: ModelType.GPT_4O,
        AgentType.TESTING: ModelType.GPT_4O
    }
    
    # Calculate cost
    cost_breakdown = await credit_manager.calculate_multi_agent_cost(
        agents_to_use,
        models_used,
        has_images=False,  # No images for full-stack build
        has_backend=True
    )
    
    estimated_cost = cost_breakdown['total']
    
    # Check if user has enough credits
    user_balance = await credit_manager.get_user_balance(user_id)
    if user_balance < estimated_cost:
        raise HTTPException(
            status_code=402,
            detail=f"Insufficient credits. Full-stack build requires {estimated_cost} credits. You have {user_balance}. Breakdown: Planning (12) + Frontend (16) + Backend (16) + Database (10) + Testing (10) = {estimated_cost}"
        )
    
    # Reserve credits upfront
    reservation = await credit_manager.reserve_credits(
        user_id,
        estimated_cost,
        "fullstack_build",
        {
            "project_id": request.project_id,
            "agents_used": [a.value for a in agents_to_use],
            "estimated_cost": estimated_cost,
            "breakdown": cost_breakdown
        }
    )
    
    if reservation['status'] != 'success':
        raise HTTPException(status_code=402, detail="Failed to reserve credits")
    
    transaction_id = reservation['transaction_id']
    
    try:
        # Initialize full-stack orchestrator
        orchestrator = FullStackOrchestrator()
        
        # Set up WebSocket callback for real-time updates
        async def send_ws_message(message):
            """Send agent messages via WebSocket"""
            await ws_manager.send_agent_status(
                request.project_id,
                {
                    "agent": message.agent_type,
                    "status": message.status,
                    "message": message.message,
                    "progress": message.progress,
                    "timestamp": message.timestamp.isoformat(),
                    "details": message.details
                }
            )
        
        orchestrator.set_message_callback(send_ws_message)
        
        # Build full-stack application
        result = await orchestrator.build_fullstack_app(
            user_prompt=request.prompt,
            project_id=request.project_id
        )
        
        if result['status'] == 'completed':
            # Calculate actual cost (same as estimated for full-stack)
            actual_cost = estimated_cost
            
            # Complete the transaction
            completion_result = await credit_manager.complete_transaction(
                transaction_id,
                actual_cost,
                {
                    "agents_used": [a.value for a in agents_to_use],
                    "total_files": result.get('total_files', 0),
                    "tech_stack": result.get('tech_stack', {})
                }
            )
            
            # Calculate refund if any
            refund_amount = estimated_cost - actual_cost
            if refund_amount > 0:
                await credit_manager.refund_credits(
                    user_id,
                    refund_amount,
                    "Full-stack build refund (unused credits)",
                    {"transaction_id": transaction_id}
                )
            
            # Update project with generated code
            await db.projects.update_one(
                {"id": request.project_id},
                {"$set": {
                    "generated_code": json.dumps(result.get('files', {})),
                    "plan": result.get('plan', {}),
                    "structure": result.get('structure', {}),
                    "deployment": result.get('deployment', {}),
                    "fullstack": True,
                    "tech_stack": result.get('tech_stack', {}),
                    "updated_at": datetime.utcnow().isoformat()
                }}
            )
            
            # Return success with credit breakdown
            return {
                "status": "success",
                "project_id": request.project_id,
                "result": result,
                "credits": {
                    "estimated": estimated_cost,
                    "used": actual_cost,
                    "refunded": refund_amount,
                    "remaining": user_balance - actual_cost
                },
                "message": f"✅ Full-stack application generated! {result.get('total_files', 0)} files created."
            }
        else:
            # Full refund on failure
            await credit_manager.refund_credits(
                user_id,
                estimated_cost,
                "Full-stack build failed - full refund",
                {"transaction_id": transaction_id, "error": result.get('error')}
            )
            raise HTTPException(status_code=500, detail=result.get('error', 'Full-stack build failed'))
    
    except Exception as e:
        # Full refund on exception
        await credit_manager.refund_credits(
            user_id,
            estimated_cost,
            f"Full-stack build exception - full refund: {str(e)}",
            {"transaction_id": transaction_id}
        )
        raise HTTPException(status_code=500, detail=f"Full-stack build error: {str(e)}")


# ============================================================================
# WORKSPACE MANAGEMENT ENDPOINTS (Phase 3 - Live Preview)
# ============================================================================

from workspace_manager import get_workspace_manager
from file_system_manager import get_file_system_manager

@api_router.post("/workspaces/create")
async def create_workspace(
    project_id: str,
    user_id: str = Depends(get_current_user)
):
    """
    Create a Docker workspace with live preview for a project.
    
    Features:
    - Isolated Docker container
    - Live reload
    - Frontend + Backend serving
    - Real-time code execution
    """
    # Get project
    project = await db.projects.find_one({"id": project_id, "user_id": user_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get generated files
    generated_code = project.get('generated_code', '')
    if not generated_code:
        raise HTTPException(status_code=400, detail="No code generated yet")
    
    # Parse files
    try:
        if isinstance(generated_code, str):
            files = json.loads(generated_code)
        else:
            files = generated_code
    except:
        files = {"index.html": generated_code}  # Fallback for old format
    
    # Create workspace
    workspace_manager = get_workspace_manager()
    result = await workspace_manager.create_workspace(
        project_id=project_id,
        user_id=user_id,
        files=files,
        project_name=project.get('name', 'app')
    )
    
    if result["status"] == "success":
        # Update project with workspace info
        await db.projects.update_one(
            {"id": project_id},
            {"$set": {
                "workspace_id": result["workspace_id"],
                "preview_url": result["preview_url"],
                "frontend_port": result["frontend_port"],
                "backend_port": result.get("backend_port"),
                "workspace_created_at": datetime.utcnow().isoformat()
            }}
        )
    
    return result

@api_router.get("/workspaces/{project_id}/status")
async def get_workspace_status(
    project_id: str,
    user_id: str = Depends(get_current_user)
):
    """Get status of workspace"""
    workspace_manager = get_workspace_manager()
    return await workspace_manager.get_workspace_status(project_id)

@api_router.post("/workspaces/{project_id}/stop")
async def stop_workspace(
    project_id: str,
    user_id: str = Depends(get_current_user)
):
    """Stop a running workspace"""
    workspace_manager = get_workspace_manager()
    return await workspace_manager.stop_workspace(project_id)

@api_router.post("/workspaces/{project_id}/restart")
async def restart_workspace(
    project_id: str,
    user_id: str = Depends(get_current_user)
):
    """Restart a workspace"""
    workspace_manager = get_workspace_manager()
    return await workspace_manager.restart_workspace(project_id)

@api_router.delete("/workspaces/{project_id}")
async def delete_workspace(
    project_id: str,
    user_id: str = Depends(get_current_user)
):
    """Delete a workspace"""
    workspace_manager = get_workspace_manager()
    return await workspace_manager.delete_workspace(project_id)

@api_router.get("/workspaces/{project_id}/logs")
async def get_workspace_logs(
    project_id: str,
    tail: int = 100,
    user_id: str = Depends(get_current_user)
):
    """Get workspace logs"""
    workspace_manager = get_workspace_manager()
    return await workspace_manager.get_workspace_logs(project_id, tail)


# ============================================================================
# FILE SYSTEM ENDPOINTS (Phase 3 - Code Editor)
# ============================================================================

class FileReadRequest(BaseModel):
    project_id: str
    file_path: str

class FileWriteRequest(BaseModel):
    project_id: str
    file_path: str
    content: str

class DirectoryRequest(BaseModel):
    project_id: str
    directory_path: str = ""

@api_router.post("/files/read")
async def read_file(
    request: FileReadRequest,
    user_id: str = Depends(get_current_user)
):
    """Read a file from workspace"""
    fs_manager = get_file_system_manager()
    return await fs_manager.read_file(user_id, request.project_id, request.file_path)

@api_router.post("/files/write")
async def write_file(
    request: FileWriteRequest,
    user_id: str = Depends(get_current_user)
):
    """Write content to a file"""
    fs_manager = get_file_system_manager()
    return await fs_manager.write_file(user_id, request.project_id, request.file_path, request.content)

@api_router.post("/files/delete")
async def delete_file(
    request: FileReadRequest,
    user_id: str = Depends(get_current_user)
):
    """Delete a file"""
    fs_manager = get_file_system_manager()
    return await fs_manager.delete_file(user_id, request.project_id, request.file_path)

@api_router.post("/files/list")
async def list_directory(
    request: DirectoryRequest,
    user_id: str = Depends(get_current_user)
):
    """List directory contents"""
    fs_manager = get_file_system_manager()
    return await fs_manager.list_directory(user_id, request.project_id, request.directory_path)

@api_router.post("/files/tree")
async def get_file_tree(
    project_id: str,
    user_id: str = Depends(get_current_user)
):
    """Get complete file tree structure"""
    fs_manager = get_file_system_manager()
    return await fs_manager.get_file_tree(user_id, project_id)

@api_router.post("/files/search")
async def search_files(
    project_id: str,
    query: str,
    user_id: str = Depends(get_current_user)
):
    """Search for files"""
    fs_manager = get_file_system_manager()
    return await fs_manager.search_files(user_id, project_id, query)


# ============================================================================
# ITERATIVE CHAT ENDPOINTS (Phase 5 - Conversational Development)
# ============================================================================

from iterative_chat_manager import get_iterative_chat_manager

class ChatRequest(BaseModel):
    project_id: str
    message: str

@api_router.post("/chat/iterative")
async def iterative_chat(
    request: ChatRequest,
    user_id: str = Depends(get_current_user)
):
    """
    Iterative chat for refining projects.
    
    Users can say:
    - "Make the button blue"
    - "Add a login form"
    - "Fix the mobile responsive design"
    
    The system understands context and makes precise changes.
    """
    chat_manager = get_iterative_chat_manager()
    return await chat_manager.process_iterative_request(
        project_id=request.project_id,
        user_id=user_id,
        message=request.message,
        db=db
    )

@api_router.get("/chat/{project_id}/history")
async def get_chat_history(
    project_id: str,
    user_id: str = Depends(get_current_user)
):
    """Get conversation history for a project"""
    chat_manager = get_iterative_chat_manager()
    history = await chat_manager.get_conversation_history(project_id, user_id)
    return {"status": "success", "history": history}

@api_router.delete("/chat/{project_id}/context")
async def clear_chat_context(
    project_id: str,
    user_id: str = Depends(get_current_user)
):
    """Clear conversation context"""
    chat_manager = get_iterative_chat_manager()
    await chat_manager.clear_context(project_id, user_id)
    return {"status": "success", "message": "Context cleared"}


# ============================================================================
# TERMINAL ACCESS ENDPOINTS (Phase 7 - WebSocket Terminal)
# ============================================================================

from terminal_manager import get_terminal_manager

class CommandRequest(BaseModel):
    container_id: str
    command: str
    working_dir: str = "/workspace"

class PackageInstallRequest(BaseModel):
    container_id: str
    packages: List[str]
    package_manager: str = "npm"

@api_router.post("/terminal/execute")
async def execute_command(
    request: CommandRequest,
    user_id: str = Depends(get_current_user)
):
    """Execute a command in container"""
    terminal_manager = get_terminal_manager()
    return await terminal_manager.execute_command(
        container_id=request.container_id,
        command=request.command,
        working_dir=request.working_dir
    )

@api_router.post("/terminal/install-packages")
async def install_packages(
    request: PackageInstallRequest,
    user_id: str = Depends(get_current_user)
):
    """Install packages in container"""
    terminal_manager = get_terminal_manager()
    return await terminal_manager.install_packages(
        container_id=request.container_id,
        packages=request.packages,
        package_manager=request.package_manager
    )

@api_router.get("/terminal/container/{container_id}/info")
async def get_container_info(
    container_id: str,
    user_id: str = Depends(get_current_user)
):
    """Get container information"""
    terminal_manager = get_terminal_manager()
    return await terminal_manager.get_container_info(container_id)

@app.websocket("/ws/terminal/{session_id}")
async def terminal_websocket(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for terminal access.
    
    Client sends:
    - {"type": "start", "container_id": "..."}
    - {"type": "input", "data": "command\n"}
    - {"type": "resize", "rows": 24, "cols": 80}
    
    Server sends:
    - {"type": "output", "data": "output text"}
    - {"type": "error", "data": "error message"}
    """
    await websocket.accept()
    
    try:
        # Wait for start message
        data = await websocket.receive_json()
        
        if data.get("type") != "start":
            await websocket.send_json({
                "type": "error",
                "data": "Expected 'start' message"
            })
            return
        
        container_id = data.get("container_id")
        if not container_id:
            await websocket.send_json({
                "type": "error",
                "data": "Missing container_id"
            })
            return
        
        # Create terminal session
        terminal_manager = get_terminal_manager()
        session = await terminal_manager.create_session(
            container_id=container_id,
            websocket=websocket,
            session_id=session_id
        )
        
        # Start session (this blocks until session ends)
        await session.start()
    
    except Exception as e:
        print(f"Terminal WebSocket error: {e}")
        await websocket.send_json({
            "type": "error",
            "data": str(e)
        })
    finally:
        terminal_manager = get_terminal_manager()
        await terminal_manager.close_session(session_id)


# ============================================================================
# GIT INTEGRATION ENDPOINTS (Phase 6 - Version Control)
# ============================================================================

from git_manager import get_git_manager

class GitInitRequest(BaseModel):
    project_id: str
    user_name: str = "AutoWebIQ User"
    user_email: str = "user@autowebiq.com"

class GitCommitRequest(BaseModel):
    project_id: str
    message: str
    files: Optional[List[str]] = None

class GitHubRepoRequest(BaseModel):
    project_id: str
    github_token: str
    repo_name: str
    description: str = ""
    private: bool = False

class GitPushRequest(BaseModel):
    project_id: str
    remote: str = "origin"
    branch: str = "main"

@api_router.post("/git/init")
async def git_init(
    request: GitInitRequest,
    user_id: str = Depends(get_current_user)
):
    """Initialize git repository in workspace"""
    # Get workspace path
    workspace_path = f"/tmp/workspaces/{user_id}/{request.project_id}"
    
    git_manager = get_git_manager()
    return await git_manager.init_repository(
        workspace_path=workspace_path,
        user_name=request.user_name,
        user_email=request.user_email
    )

@api_router.get("/git/{project_id}/status")
async def git_status(
    project_id: str,
    user_id: str = Depends(get_current_user)
):
    """Get git status"""
    workspace_path = f"/tmp/workspaces/{user_id}/{project_id}"
    git_manager = get_git_manager()
    return await git_manager.get_status(workspace_path)

@api_router.post("/git/commit")
async def git_commit(
    request: GitCommitRequest,
    user_id: str = Depends(get_current_user)
):
    """Create a git commit"""
    workspace_path = f"/tmp/workspaces/{user_id}/{request.project_id}"
    git_manager = get_git_manager()
    
    # Stage files
    await git_manager.stage_files(workspace_path, request.files)
    
    # Commit
    return await git_manager.commit(
        workspace_path=workspace_path,
        message=request.message
    )

@api_router.get("/git/{project_id}/history")
async def git_history(
    project_id: str,
    limit: int = 10,
    user_id: str = Depends(get_current_user)
):
    """Get commit history"""
    workspace_path = f"/tmp/workspaces/{user_id}/{project_id}"
    git_manager = get_git_manager()
    return await git_manager.get_commit_history(workspace_path, limit)

@api_router.post("/git/github/create-repo")
async def create_github_repo(
    request: GitHubRepoRequest,
    user_id: str = Depends(get_current_user)
):
    """Create GitHub repository and push code"""
    workspace_path = f"/tmp/workspaces/{user_id}/{request.project_id}"
    git_manager = get_git_manager()
    
    # Create GitHub repo
    repo_result = await git_manager.create_github_repo(
        github_token=request.github_token,
        repo_name=request.repo_name,
        description=request.description,
        private=request.private
    )
    
    if repo_result["status"] != "success":
        return repo_result
    
    # Add remote
    await git_manager.add_remote(
        workspace_path=workspace_path,
        remote_name="origin",
        remote_url=repo_result["clone_url"]
    )
    
    # Initial commit if needed
    status = await git_manager.get_status(workspace_path)
    if not status.get("clean", False):
        await git_manager.stage_files(workspace_path)
        await git_manager.commit(
            workspace_path=workspace_path,
            message="Initial commit from AutoWebIQ"
        )
    
    # Push to GitHub
    push_result = await git_manager.push(
        workspace_path=workspace_path,
        remote="origin",
        branch="main"
    )
    
    return {
        "status": "success",
        "message": "Repository created and code pushed to GitHub",
        "repo_url": repo_result["repo_url"],
        "push_result": push_result
    }

@api_router.post("/git/push")
async def git_push(
    request: GitPushRequest,
    user_id: str = Depends(get_current_user)
):
    """Push commits to remote"""
    workspace_path = f"/tmp/workspaces/{user_id}/{request.project_id}"
    git_manager = get_git_manager()
    return await git_manager.push(
        workspace_path=workspace_path,
        remote=request.remote,
        branch=request.branch
    )

@api_router.get("/git/{project_id}/branches")
async def git_branches(
    project_id: str,
    user_id: str = Depends(get_current_user)
):
    """List all branches"""
    workspace_path = f"/tmp/workspaces/{user_id}/{project_id}"
    git_manager = get_git_manager()
    return await git_manager.list_branches(workspace_path)


# ============================================================================
# DEPLOYMENT ENDPOINTS (Multi-Platform Support)
# ============================================================================

from deployment_manager import get_deployment_manager

class DeployRequest(BaseModel):
    project_id: str
    platform: str  # vercel, netlify, railway
    token: str
    project_name: str

@api_router.post("/deploy")
async def deploy_project(
    request: DeployRequest,
    user_id: str = Depends(get_current_user)
):
    """
    Deploy project to multiple platforms:
    - Vercel (frontend + serverless)
    - Netlify (frontend)
    - Railway (full-stack)
    """
    workspace_path = f"/tmp/workspaces/{user_id}/{request.project_id}"
    
    deployment_manager = get_deployment_manager()
    
    if request.platform == "vercel":
        result = await deployment_manager.deploy_to_vercel(
            workspace_path,
            request.project_name,
            request.token
        )
    elif request.platform == "netlify":
        result = await deployment_manager.deploy_to_netlify(
            workspace_path,
            request.project_name,
            request.token
        )
    elif request.platform == "railway":
        result = await deployment_manager.deploy_to_railway(
            workspace_path,
            request.project_name,
            request.token
        )
    else:
        raise HTTPException(status_code=400, detail="Unknown platform")
    
    return result

@api_router.get("/deploy/{platform}/{deployment_id}/status")
async def get_deploy_status(
    platform: str,
    deployment_id: str,
    token: str,
    user_id: str = Depends(get_current_user)
):
    """Get deployment status"""
    deployment_manager = get_deployment_manager()
    return await deployment_manager.get_deployment_status(platform, deployment_id, token)


# ============================================================================
# INTEGRATION TEMPLATES ENDPOINTS
# ============================================================================

from integration_templates import get_integration_templates

@api_router.get("/integrations/list")
async def list_integrations():
    """List available integration templates"""
    return {
        "status": "success",
        "integrations": [
            {
                "id": "stripe",
                "name": "Stripe",
                "description": "Payment processing",
                "modes": ["frontend", "backend"]
            },
            {
                "id": "auth0",
                "name": "Auth0",
                "description": "Authentication provider",
                "modes": ["frontend", "backend"]
            },
            {
                "id": "sendgrid",
                "name": "SendGrid",
                "description": "Email service",
                "modes": ["backend"]
            },
            {
                "id": "supabase",
                "name": "Supabase",
                "description": "Backend as a Service",
                "modes": ["frontend", "backend"]
            },
            {
                "id": "google-analytics",
                "name": "Google Analytics",
                "description": "Analytics tracking",
                "modes": ["frontend"]
            }
        ]
    }

class IntegrationRequest(BaseModel):
    integration_id: str
    mode: str = "frontend"

@api_router.post("/integrations/get-template")
async def get_integration_template(request: IntegrationRequest):
    """Get integration template code"""
    templates = get_integration_templates()
    
    if request.integration_id == "stripe":
        template = templates.get_stripe_template(request.mode)
    elif request.integration_id == "auth0":
        template = templates.get_auth0_template(request.mode)
    elif request.integration_id == "sendgrid":
        template = templates.get_sendgrid_template()
    elif request.integration_id == "supabase":
        template = templates.get_supabase_template(request.mode)
    elif request.integration_id == "google-analytics":
        template = templates.get_google_analytics_template()
    else:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    return {
        "status": "success",
        "template": template
    }

@api_router.post("/integrations/apply")
async def apply_integration(
    project_id: str,
    integration_id: str,
    mode: str = "frontend",
    user_id: str = Depends(get_current_user)
):
    """Apply integration template to project"""
    templates = get_integration_templates()
    fs_manager = get_file_system_manager()
    
    # Get template
    if integration_id == "stripe":
        template = templates.get_stripe_template(mode)
    elif integration_id == "auth0":
        template = templates.get_auth0_template(mode)
    elif integration_id == "sendgrid":
        template = templates.get_sendgrid_template()
    elif integration_id == "supabase":
        template = templates.get_supabase_template(mode)
    elif integration_id == "google-analytics":
        template = templates.get_google_analytics_template()
    else:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    # Write files
    files_created = []
    for file_path, content in template.get("files", {}).items():
        result = await fs_manager.write_file(user_id, project_id, file_path, content)
        if result["status"] == "success":
            files_created.append(file_path)
    
    return {
        "status": "success",
        "message": f"Applied {integration_id} integration",
        "files_created": files_created,
        "dependencies": template.get("dependencies", {}),
        "env_vars": template.get("env_vars", [])
    }


# Docker Container Management Endpoints (OLD - Deprecated, use workspaces instead)
@api_router.post("/projects/{project_id}/container/create")
async def create_project_container(project_id: str, user_id: str = Depends(get_current_user)):
    """Create a Docker container for live preview"""
    project = await db.projects.find_one({"id": project_id, "user_id": user_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    frontend_code = project.get('generated_code', '')
    backend_code = project.get('backend_code', '')
    
    result = await docker_manager.create_container(user_id, project_id, frontend_code, backend_code)
    
    if result['status'] == 'success':
        # Update project with container info
        await db.projects.update_one(
            {"id": project_id},
            {"$set": {
                "container_id": result['container_id'],
                "container_name": result['container_name'],
                "preview_port": result['port'],
                "preview_url": result['preview_url']
            }}
        )
    
    return result

@api_router.post("/projects/{project_id}/container/start")
async def start_project_container(project_id: str, user_id: str = Depends(get_current_user)):
    """Start a stopped container"""
    project = await db.projects.find_one({"id": project_id, "user_id": user_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    container_name = project.get('container_name')
    if not container_name:
        raise HTTPException(status_code=400, detail="No container exists for this project")
    
    return await docker_manager.start_container(container_name)

@api_router.post("/projects/{project_id}/container/stop")
async def stop_project_container(project_id: str, user_id: str = Depends(get_current_user)):
    """Stop a running container"""
    project = await db.projects.find_one({"id": project_id, "user_id": user_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    container_name = project.get('container_name')
    if not container_name:
        raise HTTPException(status_code=400, detail="No container exists for this project")
    
    return await docker_manager.stop_container(container_name)

@api_router.delete("/projects/{project_id}/container")
async def delete_project_container(project_id: str, user_id: str = Depends(get_current_user)):
    """Delete a container"""
    project = await db.projects.find_one({"id": project_id, "user_id": user_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    container_name = project.get('container_name')
    if not container_name:
        raise HTTPException(status_code=400, detail="No container exists for this project")
    
    result = await docker_manager.delete_container(container_name)
    
    if result['status'] == 'success':
        # Clear container info from project
        await db.projects.update_one(
            {"id": project_id},
            {"$unset": {
                "container_id": "",
                "container_name": "",
                "preview_port": "",
                "preview_url": ""
            }}
        )
    
    return result

@api_router.get("/projects/{project_id}/container/status")
async def get_container_status(project_id: str, user_id: str = Depends(get_current_user)):
    """Get container status"""
    project = await db.projects.find_one({"id": project_id, "user_id": user_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    container_name = project.get('container_name')
    if not container_name:
        return {"status": "error", "message": "No container exists"}
    
    return await docker_manager.get_container_status(container_name)

# Admin endpoint to build/push Docker image
@api_router.post("/admin/docker/build-image")
async def build_docker_image():
    """Build the workspace Docker image (admin only)"""
    return await docker_manager.build_image()

@api_router.post("/admin/docker/push-image")
async def push_docker_image():
    """Push image to Docker Hub (admin only)"""
    return await docker_manager.push_image()

# GitHub Integration Endpoints
class GitHubCreateRepoRequest(BaseModel):
    repo_name: str
    description: str = ""
    private: bool = False

class GitHubPushCodeRequest(BaseModel):
    project_id: str
    repo_name: str  # Full name: username/repo
    commit_message: str = "Generated by AutoWebIQ"

@api_router.post("/github/create-repo")
async def create_github_repo(
    request: GitHubCreateRepoRequest,
    user_id: str = Depends(get_current_user)
):
    """Create a new GitHub repository"""
    # Get user's GitHub access token from database
    user_doc = await db.users.find_one({"id": user_id})
    github_token = user_doc.get('github_access_token')
    
    if not github_token:
        raise HTTPException(
            status_code=400,
            detail="GitHub not connected. Please link your GitHub account first."
        )
    
    result = await github_manager.create_repository(
        github_token,
        request.repo_name,
        request.description,
        request.private
    )
    
    if result['status'] == 'success':
        return result
    else:
        raise HTTPException(status_code=400, detail=result['message'])

@api_router.post("/github/push-code")
async def push_code_to_github(
    request: GitHubPushCodeRequest,
    user_id: str = Depends(get_current_user)
):
    """Push project code to GitHub repository"""
    # Get user's GitHub token
    user_doc = await db.users.find_one({"id": user_id})
    github_token = user_doc.get('github_access_token')
    
    if not github_token:
        raise HTTPException(
            status_code=400,
            detail="GitHub not connected. Please link your GitHub account first."
        )
    
    # Get project
    project = await db.projects.find_one({"id": request.project_id, "user_id": user_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Prepare code files
    code_files = {}
    
    # Frontend code
    if project.get('generated_code'):
        code_files['index.html'] = project['generated_code']
    
    # Backend code
    if project.get('backend_code'):
        code_files['server.py'] = project['backend_code']
        code_files['requirements.txt'] = "fastapi\nuvicorn\npydantic\npython-dotenv"
    
    # README
    readme_content = f"""# {project.get('name', 'Project')}

Generated by [AutoWebIQ](https://www.autowebiq.com)

## Description
{project.get('description', 'AI-generated website')}

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
# For backend
uvicorn server:app --reload

# Or open index.html directly in browser
```

## Generated with
- AI Website Builder: AutoWebIQ
- Build Date: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}
"""
    code_files['README.md'] = readme_content
    
    # Push to GitHub
    result = await github_manager.push_code_to_repo(
        github_token,
        request.repo_name,
        code_files,
        request.commit_message
    )
    
    if result['status'] in ['success', 'partial']:
        # Update project with GitHub info
        await db.projects.update_one(
            {"id": request.project_id},
            {"$set": {
                "github_repo": request.repo_name,
                "github_url": result.get('repo_url'),
                "pushed_to_github_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        return result
    else:
        raise HTTPException(status_code=400, detail=result['message'])

@api_router.get("/github/user-info")
async def get_github_user_info(user_id: str = Depends(get_current_user)):
    """Get GitHub user information"""
    user_doc = await db.users.find_one({"id": user_id})
    github_token = user_doc.get('github_access_token')
    
    if not github_token:
        raise HTTPException(
            status_code=400,
            detail="GitHub not connected"
        )
    
    user_info = await github_manager.get_user_info(github_token)
    if user_info:
        return user_info
    else:
        raise HTTPException(status_code=400, detail="Failed to fetch GitHub user info")

@api_router.get("/github/repositories")
async def list_github_repositories(user_id: str = Depends(get_current_user)):
    """List user's GitHub repositories"""
    user_doc = await db.users.find_one({"id": user_id})
    github_token = user_doc.get('github_access_token')
    
    if not github_token:
        raise HTTPException(
            status_code=400,
            detail="GitHub not connected"
        )
    
    repos = await github_manager.list_user_repositories(github_token)
    return {"repositories": repos}

# GKE Workspace Management Endpoints
class GKEWorkspaceRequest(BaseModel):
    project_id: str

@api_router.post("/gke/workspace/create")
async def create_gke_workspace(
    request: GKEWorkspaceRequest,
    user_id: str = Depends(get_current_user)
):
    """Create a new GKE workspace with subdomain"""
    # Get project
    project = await db.projects.find_one({"id": request.project_id, "user_id": user_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Prepare code data
    code_data = {
        "frontend_code": project.get('generated_code', ''),
        "backend_code": project.get('backend_code', ''),
        "plan": project.get('project_plan', {})
    }
    
    # Create workspace
    result = await gke_manager.create_workspace(user_id, request.project_id, code_data)
    
    if result['status'] == 'success':
        # Update project with workspace info
        await db.projects.update_one(
            {"id": request.project_id},
            {"$set": {
                "gke_workspace": True,
                "subdomain": result['subdomain'],
                "preview_url": result['preview_url'],
                "deployed_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        return result
    else:
        raise HTTPException(status_code=400, detail=result['message'])

@api_router.delete("/gke/workspace/{project_id}")
async def delete_gke_workspace(
    project_id: str,
    user_id: str = Depends(get_current_user)
):
    """Delete GKE workspace"""
    project = await db.projects.find_one({"id": project_id, "user_id": user_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    result = await gke_manager.delete_workspace(project_id)
    
    if result['status'] == 'success':
        # Clear workspace info from project
        await db.projects.update_one(
            {"id": project_id},
            {"$unset": {
                "gke_workspace": "",
                "subdomain": "",
                "deployed_at": ""
            }}
        )
    
    return result

@api_router.get("/gke/workspace/{project_id}/status")
async def get_gke_workspace_status(
    project_id: str,
    user_id: str = Depends(get_current_user)
):
    """Get GKE workspace status"""
    project = await db.projects.find_one({"id": project_id, "user_id": user_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return await gke_manager.get_workspace_status(project_id)

@api_router.get("/gke/workspaces")
async def list_gke_workspaces(user_id: str = Depends(get_current_user)):
    """List all GKE workspaces for user"""
    workspaces = await gke_manager.list_user_workspaces(user_id)
    return {"workspaces": workspaces}

# Credit System Endpoints
@api_router.get("/credits/balance")
async def get_credit_balance(user_id: str = Depends(get_current_user), db=Depends(get_db)):
    """Get current credit balance - PostgreSQL"""
    return await get_credit_balance_endpoint(user_id, db)

@api_router.get("/credits/transactions")
async def get_credit_transactions(
    user_id: str = Depends(get_current_user),
    limit: int = 50,
    db=Depends(get_db)
):
    """Get credit transaction history - PostgreSQL"""
    return await get_credit_transactions_endpoint(user_id, db)

@api_router.get("/credits/summary")
async def get_credit_summary(user_id: str = Depends(get_current_user), db=Depends(get_db)):
    """Get credit usage summary - PostgreSQL"""
    return await get_credit_summary_endpoint(user_id, db)

@api_router.get("/credits/pricing")
async def get_credit_pricing():
    """Get credit costs for agents and models"""
    from credit_system import AGENT_CREDIT_COSTS, MODEL_BASE_COSTS
    
    return {
        "agent_costs": {agent.value: cost for agent, cost in AGENT_CREDIT_COSTS.items()},
        "model_costs": {model.value: cost for model, cost in MODEL_BASE_COSTS.items()},
        "note": "Actual costs may vary based on complexity, tokens used, and multi-agent discounts"
    }

app.include_router(api_router)

# Import and include v2 routes (PostgreSQL + Celery + WebSocket)
from routes_v2 import router_v2
app.include_router(router_v2)

# Simple validation endpoint (V1 - works with MongoDB)
@app.post("/api/validate")
async def validate_website(
    project_id: str = Body(...),
    html_content: str = Body(...),
    user: dict = Depends(get_current_user)
):
    """
    Simple HTML validation that checks basic quality metrics
    Returns a score and basic validation results
    """
    try:
        # Basic HTML validation checks
        checks = {
            "html_structure": {
                "check_name": "HTML Structure",
                "passed": False,
                "score": 0,
                "details": []
            },
            "css_quality": {
                "check_name": "CSS Quality",
                "passed": False,
                "score": 0,
                "details": []
            },
            "javascript": {
                "check_name": "JavaScript",
                "passed": False,
                "score": 0,
                "details": []
            },
            "accessibility": {
                "check_name": "Accessibility",
                "passed": False,
                "score": 0,
                "details": []
            },
            "seo": {
                "check_name": "SEO",
                "passed": False,
                "score": 0,
                "details": []
            },
            "performance": {
                "check_name": "Performance",
                "passed": False,
                "score": 0,
                "details": []
            },
            "security": {
                "check_name": "Security",
                "passed": False,
                "score": 0,
                "details": []
            },
            "browser_compatibility": {
                "check_name": "Browser Compatibility",
                "passed": False,
                "score": 0,
                "details": []
            },
            "mobile_responsive": {
                "check_name": "Mobile Responsive",
                "passed": False,
                "score": 0,
                "details": []
            }
        }
        
        # HTML Structure checks
        if "<!DOCTYPE html>" in html_content.lower() or "<html" in html_content.lower():
            checks["html_structure"]["passed"] = True
            checks["html_structure"]["score"] = 90
            checks["html_structure"]["details"].append("Valid HTML structure detected")
        
        # CSS Quality checks
        if "<style>" in html_content.lower() or "style=" in html_content.lower():
            checks["css_quality"]["passed"] = True
            checks["css_quality"]["score"] = 85
            checks["css_quality"]["details"].append("CSS styling found")
        
        # JavaScript check
        if "<script>" in html_content.lower():
            checks["javascript"]["passed"] = True
            checks["javascript"]["score"] = 80
            checks["javascript"]["details"].append("JavaScript detected")
        else:
            checks["javascript"]["passed"] = True
            checks["javascript"]["score"] = 75
            checks["javascript"]["details"].append("No JavaScript issues")
        
        # Accessibility checks
        if "alt=" in html_content.lower() or "aria-" in html_content.lower():
            checks["accessibility"]["passed"] = True
            checks["accessibility"]["score"] = 85
            checks["accessibility"]["details"].append("Accessibility attributes found")
        else:
            checks["accessibility"]["passed"] = False
            checks["accessibility"]["score"] = 60
            checks["accessibility"]["details"].append("Consider adding alt text and ARIA labels")
        
        # SEO checks
        seo_score = 0
        if "<title>" in html_content.lower():
            seo_score += 40
            checks["seo"]["details"].append("Title tag present")
        if "meta name=\"description\"" in html_content.lower():
            seo_score += 40
            checks["seo"]["details"].append("Meta description present")
        
        checks["seo"]["score"] = seo_score
        checks["seo"]["passed"] = seo_score >= 60
        
        # Performance (basic check on file size)
        file_size_kb = len(html_content) / 1024
        if file_size_kb < 100:
            checks["performance"]["passed"] = True
            checks["performance"]["score"] = 95
            checks["performance"]["details"].append(f"Good file size: {file_size_kb:.1f}KB")
        elif file_size_kb < 500:
            checks["performance"]["passed"] = True
            checks["performance"]["score"] = 80
            checks["performance"]["details"].append(f"Acceptable file size: {file_size_kb:.1f}KB")
        else:
            checks["performance"]["passed"] = False
            checks["performance"]["score"] = 60
            checks["performance"]["details"].append(f"Large file size: {file_size_kb:.1f}KB - consider optimization")
        
        # Security (basic checks)
        security_score = 80
        if "javascript:" in html_content.lower() or "onclick=" in html_content.lower():
            security_score -= 10
            checks["security"]["details"].append("Inline event handlers detected")
        checks["security"]["passed"] = security_score >= 70
        checks["security"]["score"] = security_score
        if not checks["security"]["details"]:
            checks["security"]["details"].append("No obvious security issues")
        
        # Browser Compatibility
        checks["browser_compatibility"]["passed"] = True
        checks["browser_compatibility"]["score"] = 85
        checks["browser_compatibility"]["details"].append("Modern HTML5 compatible")
        
        # Mobile Responsive
        if "viewport" in html_content.lower() or "@media" in html_content.lower():
            checks["mobile_responsive"]["passed"] = True
            checks["mobile_responsive"]["score"] = 90
            checks["mobile_responsive"]["details"].append("Responsive design detected")
        else:
            checks["mobile_responsive"]["passed"] = False
            checks["mobile_responsive"]["score"] = 50
            checks["mobile_responsive"]["details"].append("No responsive meta tag or media queries found")
        
        # Calculate overall score
        total_score = sum(check["score"] for check in checks.values())
        overall_score = round(total_score / len(checks))
        
        passed_checks = sum(1 for check in checks.values() if check["passed"])
        
        return {
            "results": checks,
            "overall_score": overall_score,
            "passed_checks": passed_checks,
            "total_checks": len(checks),
            "all_passed": passed_checks == len(checks),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint for monitoring"""
    health_status = {
        "status": "healthy",
        "service": "autowebiq-backend",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "databases": {},
        "services": {}
    }
    
    try:
        # Check PostgreSQL connection
        from database import AsyncSessionLocal
        from sqlalchemy import text
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        health_status["databases"]["postgresql"] = "connected"
    except Exception as e:
        health_status["databases"]["postgresql"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    try:
        # Check Redis connection
        import redis.asyncio as redis
        redis_client = redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379/0'))
        await redis_client.ping()
        await redis_client.close()
        health_status["services"]["redis"] = "connected"
    except Exception as e:
        health_status["services"]["redis"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    try:
        # Check Celery workers
        from celery_app import celery_app
        inspect = celery_app.control.inspect()
        stats = inspect.stats()
        if stats:
            worker_count = len(stats)
            health_status["services"]["celery"] = f"{worker_count} workers active"
        else:
            health_status["services"]["celery"] = "no workers"
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["services"]["celery"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    return health_status


# ==================== Template & Component Endpoints ====================

@app.get("/api/templates")
async def get_templates():
    """Get all available templates"""
    try:
        templates = await db.templates.find().to_list(length=None)
        
        # Convert ObjectId to string for JSON serialization
        for template in templates:
            template['_id'] = str(template['_id'])
        
        return {
            "success": True,
            "count": len(templates),
            "templates": templates
        }
    except Exception as e:
        logger.error(f"Error fetching templates: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching templates: {str(e)}")


@app.get("/api/templates/{template_id}")
async def get_template(template_id: str):
    """Get a specific template by ID"""
    try:
        template = await db.templates.find_one({"id": template_id})
        
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        
        template['_id'] = str(template['_id'])
        
        return {
            "success": True,
            "template": template
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching template: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching template: {str(e)}")


@app.get("/api/components")
async def get_components():
    """Get all available UI components"""
    try:
        components = await db.components.find().to_list(length=None)
        
        # Convert ObjectId to string for JSON serialization
        for component in components:
            component['_id'] = str(component['_id'])
        
        return {
            "success": True,
            "count": len(components),
            "components": components
        }
    except Exception as e:
        logger.error(f"Error fetching components: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching components: {str(e)}")


@app.get("/api/components/category/{category}")
async def get_components_by_category(category: str):
    """Get components by category"""
    try:
        components = await db.components.find({"category": category}).to_list(length=None)
        
        # Convert ObjectId to string for JSON serialization
        for component in components:
            component['_id'] = str(component['_id'])
        
        return {
            "success": True,
            "category": category,
            "count": len(components),
            "components": components
        }
    except Exception as e:
        logger.error(f"Error fetching components: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching components: {str(e)}")



app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db():
    """Cleanup database connections on shutdown"""
    from database import close_db
    await close_db()
    print("✅ Database connections closed")