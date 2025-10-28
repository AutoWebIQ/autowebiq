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
    username: str
    email: str
    password_hash: str
    credits: int = 50  # Give 50 free credits (10 messages) on signup
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
async def get_me(user_id: str = Depends(get_current_user)):
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
        # Map models to actual API models
        if request.model in ["claude-4.5-sonnet-200k", "claude-4.5-sonnet-1m"]:
            actual_model = "claude-4-sonnet-20250514"
        else:
            actual_model = request.model
        
        # Better system prompt for conversational AI
        system_prompt = """You are AutoWebIQ, an expert web development AI assistant. You build beautiful, modern, responsive websites.

IMPORTANT INSTRUCTIONS:
1. If the user's request is vague, ask 2-3 clarifying questions to understand their needs better
2. When you have enough info, generate complete HTML with inline CSS and JavaScript
3. Make websites modern, responsive, and production-ready
4. Use modern design trends: gradients, animations, clean layouts
5. Always provide ONLY the HTML code when generating (no explanations before/after)

If user asks to "build a website for X", first ask:
- What's the main purpose? (e.g., showcase, sell, inform)
- Who's the target audience?
- Any specific colors or style preferences?

Then generate the complete website."""
        
        # Use OpenAI for GPT models
        if actual_model.startswith('gpt'):
            prompt = f"{request.message}\n\nProject: {project['name']}\nDescription: {project['description']}"
            if project['generated_code']:
                prompt += f"\n\nCurrent website code exists. User wants modifications."
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
            
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
            
            prompt = f"{request.message}\n\nProject: {project['name']}\nDescription: {project['description']}"
            if project['generated_code']:
                prompt += f"\n\nCurrent website exists. User wants: {request.message}"
            
            user_message = UserMessage(text=prompt)
            ai_response = await chat_client.send_message(user_message)
        
        # Extract HTML
        html_code = ai_response.strip()
        if "```html" in html_code:
            html_code = html_code.split("```html")[1].split("```")[0].strip()
        elif "```" in html_code:
            html_code = html_code.split("```")[1].split("```")[0].strip()
        
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