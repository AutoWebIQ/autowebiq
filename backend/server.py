from fastapi import FastAPI, APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect, UploadFile, File, Request, Response, Cookie
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse, JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
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

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key=os.environ.get('CLOUDINARY_API_KEY'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET')
)

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()
JWT_SECRET = os.environ.get('JWT_SECRET')
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION = timedelta(days=30)

razorpay_client = razorpay.Client(auth=(os.environ['RAZORPAY_KEY_ID'], os.environ['RAZORPAY_KEY_SECRET']))

# OpenAI client
openai_client = AsyncOpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

app = FastAPI()
api_router = APIRouter(prefix="/api")

# Models
class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    firebase_uid: Optional[str] = None  # Firebase UID for Firebase Auth users
    username: str
    email: str
    password_hash: str = ""  # Empty for Firebase Auth users
    credits: int = 10  # Give 10 free credits on signup
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
        user_id: str = payload.get("user_id")
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
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid authentication")
        return user_id
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

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
@api_router.post("/auth/register", response_model=TokenResponse)
async def register(user_data: UserRegister):
    existing = await db.users.find_one({"$or": [{"username": user_data.username}, {"email": user_data.email}]})
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    
    user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        credits=10
    )
    
    user_dict = user.model_dump()
    user_dict['created_at'] = user_dict['created_at'].isoformat()
    await db.users.insert_one(user_dict)
    
    token = create_access_token({"user_id": user.id})
    
    return TokenResponse(
        access_token=token,
        user={"id": user.id, "username": user.username, "email": user.email, "credits": user.credits}
    )

@api_router.post("/auth/login", response_model=TokenResponse)
async def login(user_data: UserLogin):
    user_doc = await db.users.find_one({"email": user_data.email})
    if not user_doc or not verify_password(user_data.password, user_doc['password_hash']):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"user_id": user_doc['id']})
    
    return TokenResponse(
        access_token=token,
        user={"id": user_doc['id'], "username": user_doc['username'], "email": user_doc['email'], "credits": user_doc['credits']}
    )

@api_router.get("/auth/me")
async def get_me(request: Request):
    """Get current user data (supports both JWT and session token)"""
    user_id = await get_current_user_flexible(request)
    
    user_doc = await db.users.find_one({"id": user_id}, {"_id": 0, "password_hash": 0})
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    return user_doc

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
                "credits": 10,  # Free credits
                "picture": user_data.photo_url,
                "auth_provider": provider_map.get(user_data.provider_id, "email"),
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            await db.users.insert_one(new_user)
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
            "credits": 50,  # Give 50 free credits
            "picture": user_picture,
            "auth_provider": "google",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.users.insert_one(user_data)
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
async def get_projects(user_id: str = Depends(get_current_user)):
    projects = await db.projects.find(
        {"user_id": user_id, "status": "active"},
        {"_id": 0}
    ).sort("updated_at", -1).to_list(100)
    return projects

@api_router.get("/projects/{project_id}")
async def get_project(project_id: str, user_id: str = Depends(get_current_user)):
    project = await db.projects.find_one({"id": project_id, "user_id": user_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@api_router.get("/projects/{project_id}/messages")
async def get_messages(project_id: str, user_id: str = Depends(get_current_user)):
    project = await db.projects.find_one({"id": project_id, "user_id": user_id})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    messages = await db.messages.find(
        {"project_id": project_id},
        {"_id": 0}
    ).sort("created_at", 1).to_list(1000)
    return messages

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

app.include_router(api_router)

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
async def shutdown_db_client():
    client.close()