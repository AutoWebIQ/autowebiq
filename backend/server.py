from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse, FileResponse
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
from emergentintegrations.llm.chat import LlmChat, UserMessage

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()
JWT_SECRET = os.environ.get('JWT_SECRET')
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION = timedelta(days=30)

# Razorpay
razorpay_client = razorpay.Client(auth=(os.environ['RAZORPAY_KEY_ID'], os.environ['RAZORPAY_KEY_SECRET']))

# Create the main app
app = FastAPI()
api_router = APIRouter(prefix="/api")

# Models
class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: str
    password_hash: str
    credits: int = 10  # Free credits on signup
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserRegister(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

class CreditPackage(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    name: str
    credits: int
    price: int  # in paise
    currency: str = "INR"

class Transaction(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    order_id: str
    payment_id: Optional[str] = None
    amount: int
    credits: int
    status: str  # created, paid, failed
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Project(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    name: str
    prompt: str
    generated_code: dict  # {"html": "", "css": "", "js": ""}
    status: str  # generating, completed, failed
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ProjectCreate(BaseModel):
    name: str
    prompt: str

class CreateOrderRequest(BaseModel):
    package_id: str

class VerifyPaymentRequest(BaseModel):
    order_id: str
    payment_id: str
    signature: str

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
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Credit packages
CREDIT_PACKAGES = [
    {"id": "pkg_10", "name": "Starter Pack", "credits": 10, "price": 9900, "currency": "INR"},
    {"id": "pkg_100", "name": "Professional Pack", "credits": 100, "price": 49900, "currency": "INR"},
    {"id": "pkg_250", "name": "Enterprise Pack", "credits": 250, "price": 99900, "currency": "INR"},
]

# Auth endpoints
@api_router.post("/auth/register", response_model=TokenResponse)
async def register(user_data: UserRegister):
    # Check if user exists
    existing = await db.users.find_one({"$or": [{"username": user_data.username}, {"email": user_data.email}]})
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    
    # Create user with 10 free credits
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
        user={
            "id": user_doc['id'],
            "username": user_doc['username'],
            "email": user_doc['email'],
            "credits": user_doc['credits']
        }
    )

@api_router.get("/auth/me")
async def get_me(user_id: str = Depends(get_current_user)):
    user_doc = await db.users.find_one({"id": user_id}, {"_id": 0, "password_hash": 0})
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    return user_doc

# Credits endpoints
@api_router.get("/credits/balance")
async def get_credits(user_id: str = Depends(get_current_user)):
    user_doc = await db.users.find_one({"id": user_id}, {"_id": 0, "credits": 1})
    return {"credits": user_doc['credits']}

@api_router.get("/credits/packages")
async def get_packages():
    return CREDIT_PACKAGES

@api_router.post("/credits/create-order")
async def create_order(request: CreateOrderRequest, user_id: str = Depends(get_current_user)):
    # Find package
    package = next((p for p in CREDIT_PACKAGES if p["id"] == request.package_id), None)
    if not package:
        raise HTTPException(status_code=404, detail="Package not found")
    
    # Create Razorpay order
    try:
        razor_order = razorpay_client.order.create({
            "amount": package["price"],
            "currency": package["currency"],
            "payment_capture": 1
        })
        
        # Save transaction
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
        # Verify signature
        params_dict = {
            'razorpay_order_id': request.order_id,
            'razorpay_payment_id': request.payment_id,
            'razorpay_signature': request.signature
        }
        razorpay_client.utility.verify_payment_signature(params_dict)
        
        # Update transaction
        transaction = await db.transactions.find_one({"order_id": request.order_id, "user_id": user_id})
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        await db.transactions.update_one(
            {"order_id": request.order_id},
            {"$set": {"payment_id": request.payment_id, "status": "paid"}}
        )
        
        # Add credits to user
        await db.users.update_one(
            {"id": user_id},
            {"$inc": {"credits": transaction['credits']}}
        )
        
        user_doc = await db.users.find_one({"id": user_id}, {"_id": 0, "credits": 1})
        
        return {"success": True, "credits": user_doc['credits']}
    
    except razorpay.errors.SignatureVerificationError:
        await db.transactions.update_one(
            {"order_id": request.order_id},
            {"$set": {"status": "failed"}}
        )
        raise HTTPException(status_code=400, detail="Invalid payment signature")

# Projects endpoints
@api_router.post("/projects/create")
async def create_project(project_data: ProjectCreate, user_id: str = Depends(get_current_user)):
    # Check credits
    user_doc = await db.users.find_one({"id": user_id})
    if user_doc['credits'] < 1:
        raise HTTPException(status_code=402, detail="Insufficient credits. Please buy more credits.")
    
    # Create project
    project = Project(
        user_id=user_id,
        name=project_data.name,
        prompt=project_data.prompt,
        generated_code={"html": "", "css": "", "js": ""},
        status="generating"
    )
    
    proj_dict = project.model_dump()
    proj_dict['created_at'] = proj_dict['created_at'].isoformat()
    await db.projects.insert_one(proj_dict)
    
    # Deduct credit
    await db.users.update_one({"id": user_id}, {"$inc": {"credits": -1}})
    
    # Generate website using GPT-5
    try:
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        chat = LlmChat(
            api_key=api_key,
            session_id=project.id,
            system_message="You are an expert web developer. Generate complete, production-ready websites with HTML, CSS, and JavaScript. Always provide clean, modern, responsive code with proper structure. Include inline CSS in <style> tags and JavaScript in <script> tags within the HTML."
        )
        chat.with_model("openai", "gpt-5")
        
        generation_prompt = f"""Create a complete, modern, responsive website for: {project_data.prompt}

Requirements:
1. Generate a single, complete HTML file
2. Include beautiful, modern CSS with gradients and animations
3. Make it fully responsive and mobile-friendly
4. Add interactive JavaScript features
5. Use modern design principles
6. Include all CSS in <style> tags in the <head>
7. Include all JavaScript in <script> tags before </body>

Provide ONLY the complete HTML code, nothing else."""
        
        user_msg = UserMessage(text=generation_prompt)
        ai_response = await chat.send_message(user_msg)
        
        # Extract HTML from response
        html_code = ai_response.strip()
        if "```html" in html_code:
            html_code = html_code.split("```html")[1].split("```")[0].strip()
        elif "```" in html_code:
            html_code = html_code.split("```")[1].split("```")[0].strip()
        
        # Update project
        await db.projects.update_one(
            {"id": project.id},
            {"$set": {
                "generated_code": {"html": html_code, "css": "", "js": ""},
                "status": "completed"
            }}
        )
        
        project_doc = await db.projects.find_one({"id": project.id}, {"_id": 0})
        return project_doc
    
    except Exception as e:
        await db.projects.update_one(
            {"id": project.id},
            {"$set": {"status": "failed"}}
        )
        # Refund credit
        await db.users.update_one({"id": user_id}, {"$inc": {"credits": 1}})
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

@api_router.get("/projects")
async def get_projects(user_id: str = Depends(get_current_user)):
    projects = await db.projects.find(
        {"user_id": user_id},
        {"_id": 0}
    ).sort("created_at", -1).to_list(100)
    return projects

@api_router.get("/projects/{project_id}")
async def get_project(project_id: str, user_id: str = Depends(get_current_user)):
    project = await db.projects.find_one({"id": project_id, "user_id": user_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@api_router.delete("/projects/{project_id}")
async def delete_project(project_id: str, user_id: str = Depends(get_current_user)):
    result = await db.projects.delete_one({"id": project_id, "user_id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Project deleted"}

@api_router.get("/projects/{project_id}/download")
async def download_project(project_id: str, user_id: str = Depends(get_current_user)):
    project = await db.projects.find_one({"id": project_id, "user_id": user_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Create ZIP file
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr('index.html', project['generated_code']['html'])
        if project['generated_code'].get('css'):
            zip_file.writestr('styles.css', project['generated_code']['css'])
        if project['generated_code'].get('js'):
            zip_file.writestr('script.js', project['generated_code']['js'])
        zip_file.writestr('README.md', f"# {project['name']}\n\nGenerated by Optra AI\n\nPrompt: {project['prompt']}")
    
    zip_buffer.seek(0)
    
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={project['name'].replace(' ', '_')}.zip"}
    )

@api_router.get("/projects/{project_id}/preview")
async def preview_project(project_id: str, user_id: str = Depends(get_current_user)):
    project = await db.projects.find_one({"id": project_id, "user_id": user_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return {"html": project['generated_code']['html']}

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()