from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
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
import base64
from emergentintegrations.llm.chat import LlmChat, UserMessage
from emergentintegrations.llm.openai.image_generation import OpenAIImageGeneration

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key')
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION = timedelta(days=7)

# Create the main app
app = FastAPI()
api_router = APIRouter(prefix="/api")

# Models
class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    password_hash: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    username: str

class Conversation(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    title: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ConversationCreate(BaseModel):
    title: str = "New Conversation"

class ConversationUpdate(BaseModel):
    title: str

class Message(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: str
    role: str  # 'user' or 'assistant'
    content: str
    image_url: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class MessageSend(BaseModel):
    conversation_id: str
    content: str
    include_file_context: Optional[str] = None

class ImageGenerate(BaseModel):
    conversation_id: str
    prompt: str

class FileUpload(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: str
    filename: str
    content: str
    file_type: str
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

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

# Auth endpoints
@api_router.post("/auth/register", response_model=TokenResponse)
async def register(user_data: UserRegister):
    # Check if user exists
    existing_user = await db.users.find_one({"username": user_data.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Create user
    user = User(
        username=user_data.username,
        password_hash=hash_password(user_data.password)
    )
    
    user_dict = user.model_dump()
    user_dict['created_at'] = user_dict['created_at'].isoformat()
    await db.users.insert_one(user_dict)
    
    # Create token
    token = create_access_token({"user_id": user.id})
    
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        username=user.username
    )

@api_router.post("/auth/login", response_model=TokenResponse)
async def login(user_data: UserLogin):
    # Find user
    user_doc = await db.users.find_one({"username": user_data.username})
    if not user_doc:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Verify password
    if not verify_password(user_data.password, user_doc['password_hash']):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create token
    token = create_access_token({"user_id": user_doc['id']})
    
    return TokenResponse(
        access_token=token,
        user_id=user_doc['id'],
        username=user_doc['username']
    )

@api_router.get("/auth/me")
async def get_me(user_id: str = Depends(get_current_user)):
    user_doc = await db.users.find_one({"id": user_id}, {"_id": 0, "password_hash": 0})
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    return user_doc

# Conversation endpoints
@api_router.get("/conversations", response_model=List[Conversation])
async def get_conversations(user_id: str = Depends(get_current_user)):
    conversations = await db.conversations.find(
        {"user_id": user_id}, 
        {"_id": 0}
    ).sort("updated_at", -1).to_list(1000)
    
    for conv in conversations:
        if isinstance(conv.get('created_at'), str):
            conv['created_at'] = datetime.fromisoformat(conv['created_at'])
        if isinstance(conv.get('updated_at'), str):
            conv['updated_at'] = datetime.fromisoformat(conv['updated_at'])
    
    return conversations

@api_router.post("/conversations", response_model=Conversation)
async def create_conversation(conv_data: ConversationCreate, user_id: str = Depends(get_current_user)):
    conversation = Conversation(
        user_id=user_id,
        title=conv_data.title
    )
    
    conv_dict = conversation.model_dump()
    conv_dict['created_at'] = conv_dict['created_at'].isoformat()
    conv_dict['updated_at'] = conv_dict['updated_at'].isoformat()
    await db.conversations.insert_one(conv_dict)
    
    return conversation

@api_router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str, user_id: str = Depends(get_current_user)):
    conv = await db.conversations.find_one({"id": conversation_id, "user_id": user_id}, {"_id": 0})
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = await db.messages.find(
        {"conversation_id": conversation_id}, 
        {"_id": 0}
    ).sort("created_at", 1).to_list(1000)
    
    for msg in messages:
        if isinstance(msg.get('created_at'), str):
            msg['created_at'] = datetime.fromisoformat(msg['created_at'])
    
    return {"conversation": conv, "messages": messages}

@api_router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str, user_id: str = Depends(get_current_user)):
    result = await db.conversations.delete_one({"id": conversation_id, "user_id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Delete messages
    await db.messages.delete_many({"conversation_id": conversation_id})
    # Delete files
    await db.files.delete_many({"conversation_id": conversation_id})
    
    return {"message": "Conversation deleted"}

@api_router.put("/conversations/{conversation_id}", response_model=Conversation)
async def update_conversation(conversation_id: str, conv_data: ConversationUpdate, user_id: str = Depends(get_current_user)):
    result = await db.conversations.update_one(
        {"id": conversation_id, "user_id": user_id},
        {"$set": {"title": conv_data.title, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    conv = await db.conversations.find_one({"id": conversation_id}, {"_id": 0})
    if isinstance(conv.get('created_at'), str):
        conv['created_at'] = datetime.fromisoformat(conv['created_at'])
    if isinstance(conv.get('updated_at'), str):
        conv['updated_at'] = datetime.fromisoformat(conv['updated_at'])
    
    return Conversation(**conv)

# Message endpoints
@api_router.post("/messages")
async def send_message(msg_data: MessageSend, user_id: str = Depends(get_current_user)):
    # Verify conversation belongs to user
    conv = await db.conversations.find_one({"id": msg_data.conversation_id, "user_id": user_id})
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Save user message
    user_message = Message(
        conversation_id=msg_data.conversation_id,
        role="user",
        content=msg_data.content
    )
    
    user_msg_dict = user_message.model_dump()
    user_msg_dict['created_at'] = user_msg_dict['created_at'].isoformat()
    await db.messages.insert_one(user_msg_dict)
    
    # Get conversation history
    messages = await db.messages.find(
        {"conversation_id": msg_data.conversation_id}, 
        {"_id": 0}
    ).sort("created_at", 1).to_list(1000)
    
    # Prepare context for AI
    context = ""
    if msg_data.include_file_context:
        context = f"\n\nFile context: {msg_data.include_file_context}"
    
    # Get AI response using emergentintegrations
    try:
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        chat = LlmChat(
            api_key=api_key,
            session_id=msg_data.conversation_id,
            system_message="You are an advanced AI assistant with capabilities similar to me. You can help with text generation, code explanation, document analysis, and provide intelligent responses. Be helpful, accurate, and conversational."
        )
        chat.with_model("openai", "gpt-5")
        
        user_msg = UserMessage(text=msg_data.content + context)
        ai_response = await chat.send_message(user_msg)
        
        # Save AI response
        ai_message = Message(
            conversation_id=msg_data.conversation_id,
            role="assistant",
            content=ai_response
        )
        
        ai_msg_dict = ai_message.model_dump()
        ai_msg_dict['created_at'] = ai_msg_dict['created_at'].isoformat()
        await db.messages.insert_one(ai_msg_dict)
        
        # Update conversation timestamp
        await db.conversations.update_one(
            {"id": msg_data.conversation_id},
            {"$set": {"updated_at": datetime.now(timezone.utc).isoformat()}}
        )
        
        return {"user_message": user_message.model_dump(), "ai_message": ai_message.model_dump()}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI error: {str(e)}")

@api_router.post("/generate-image")
async def generate_image(img_data: ImageGenerate, user_id: str = Depends(get_current_user)):
    # Verify conversation belongs to user
    conv = await db.conversations.find_one({"id": img_data.conversation_id, "user_id": user_id})
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    try:
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        image_gen = OpenAIImageGeneration(api_key=api_key)
        
        images = await image_gen.generate_images(
            prompt=img_data.prompt,
            model="gpt-image-1",
            number_of_images=1
        )
        
        if images and len(images) > 0:
            image_base64 = base64.b64encode(images[0]).decode('utf-8')
            
            # Save user request
            user_message = Message(
                conversation_id=img_data.conversation_id,
                role="user",
                content=f"Generate image: {img_data.prompt}"
            )
            user_msg_dict = user_message.model_dump()
            user_msg_dict['created_at'] = user_msg_dict['created_at'].isoformat()
            await db.messages.insert_one(user_msg_dict)
            
            # Save AI response with image
            ai_message = Message(
                conversation_id=img_data.conversation_id,
                role="assistant",
                content="Here's your generated image:",
                image_url=f"data:image/png;base64,{image_base64}"
            )
            ai_msg_dict = ai_message.model_dump()
            ai_msg_dict['created_at'] = ai_msg_dict['created_at'].isoformat()
            await db.messages.insert_one(ai_msg_dict)
            
            # Update conversation
            await db.conversations.update_one(
                {"id": img_data.conversation_id},
                {"$set": {"updated_at": datetime.now(timezone.utc).isoformat()}}
            )
            
            return {"image_base64": image_base64, "message": ai_message.model_dump()}
        else:
            raise HTTPException(status_code=500, detail="No image was generated")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image generation error: {str(e)}")

@api_router.post("/upload-file")
async def upload_file(conversation_id: str, file: UploadFile = File(...), user_id: str = Depends(get_current_user)):
    # Verify conversation belongs to user
    conv = await db.conversations.find_one({"id": conversation_id, "user_id": user_id})
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    try:
        # Read file content
        content = await file.read()
        content_str = content.decode('utf-8', errors='ignore')
        
        # Save file info
        file_upload = FileUpload(
            conversation_id=conversation_id,
            filename=file.filename,
            content=content_str[:50000],  # Limit content size
            file_type=file.content_type or "text/plain"
        )
        
        file_dict = file_upload.model_dump()
        file_dict['uploaded_at'] = file_dict['uploaded_at'].isoformat()
        await db.files.insert_one(file_dict)
        
        # Create analysis prompt
        analysis_prompt = f"Analyze this file ({file.filename}):\n\n{content_str[:10000]}"
        
        # Get AI analysis
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        chat = LlmChat(
            api_key=api_key,
            session_id=conversation_id,
            system_message="You are an AI assistant that analyzes files and documents. Provide detailed analysis and insights."
        )
        chat.with_model("openai", "gpt-5")
        
        user_msg = UserMessage(text=analysis_prompt)
        ai_response = await chat.send_message(user_msg)
        
        # Save messages
        user_message = Message(
            conversation_id=conversation_id,
            role="user",
            content=f"Uploaded file: {file.filename}"
        )
        user_msg_dict = user_message.model_dump()
        user_msg_dict['created_at'] = user_msg_dict['created_at'].isoformat()
        await db.messages.insert_one(user_msg_dict)
        
        ai_message = Message(
            conversation_id=conversation_id,
            role="assistant",
            content=ai_response
        )
        ai_msg_dict = ai_message.model_dump()
        ai_msg_dict['created_at'] = ai_msg_dict['created_at'].isoformat()
        await db.messages.insert_one(ai_msg_dict)
        
        return {
            "file": file_upload.model_dump(),
            "analysis": ai_response
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload error: {str(e)}")

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