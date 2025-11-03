# AutoWebIQ 2.0 - Clean Configuration
import os
from motor.motor_asyncio import AsyncIOMotorClient

# MongoDB Connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'autowebiq_v2')

# Initialize MongoDB
mongo_client = AsyncIOMotorClient(MONGO_URL)
db = mongo_client[DB_NAME]

# JWT Secret
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 168  # 7 days

# API Keys
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
GOOGLE_AI_API_KEY = os.environ.get('GOOGLE_AI_API_KEY')

# Credits Configuration
INITIAL_CREDITS = 10  # Like Emergent
CREDIT_COSTS = {
    'planning': 2,
    'design': 3,
    'code_generation': 5,
    'testing': 2,
    'message': 2  # Per chat message like Emergent
}

# CORS Configuration
ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'https://autowebiq.com',
    'https://www.autowebiq.com',
    os.environ.get('FRONTEND_URL', 'http://localhost:3000')
]
