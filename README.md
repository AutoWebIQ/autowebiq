# AutoWebIQ

**AI-Powered Multi-Agent Website Builder**

AutoWebIQ is an advanced multi-agent AI platform for creating professional websites through conversational AI. Built with enterprise-grade architecture featuring PostgreSQL, Redis, Celery, and WebSockets for real-time collaboration.

---

## 🚀 Features

### Core Capabilities
- **Multi-Agent AI Generation**: Leveraging Claude 4.5 Sonnet, GPT-5, and Gemini for intelligent website creation
- **Template Library**: 24 production-ready templates + 50 reusable UI components
- **Real-Time Collaboration**: WebSocket-powered live preview and build progress tracking
- **Firebase Authentication**: Secure user authentication with Google OAuth
- **Credit System**: Transparent credit-based usage with PostgreSQL transaction tracking
- **Cloud Storage**: AWS S3 + CloudFront CDN for file storage and delivery

### Advanced Infrastructure
- **Asynchronous Processing**: Celery task queue for background website generation
- **Redis Caching**: High-performance caching for templates and user data
- **PostgreSQL Database**: Reliable relational data storage for users, projects, and transactions
- **MongoDB**: Document storage for templates and AI interactions
- **WebSocket Communication**: Real-time build progress updates

---

## 🏗️ Architecture

### Tech Stack

**Frontend**
- React 18 with hooks
- Tailwind CSS + Custom CSS
- Radix UI components
- Firebase Auth SDK
- WebSocket client for real-time updates

**Backend**
- FastAPI (Python 3.11+)
- SQLAlchemy (PostgreSQL ORM)
- Motor (MongoDB async driver)
- Celery (async task processing)
- Redis (caching + message broker)
- WebSocket (Socket.IO)

**Databases**
- PostgreSQL: User accounts, projects, credit transactions
- MongoDB: Templates, components, AI interactions
- Redis: Session cache, task results, real-time data

**Cloud Services**
- AWS S3: File storage
- CloudFront: CDN
- Cloudinary: Image optimization
- GCP: Container orchestration (GKE)
- Vercel: Deployment platform

---

## 📋 Prerequisites

- Python 3.11+
- Node.js 18+ & Yarn
- PostgreSQL 14+
- MongoDB 6+
- Redis 7+
- Docker (optional, for containerized deployment)

---

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/AutoWebIQ/autowebiq.git
cd autowebiq
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your credentials
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
yarn install

# Configure environment variables
cp .env.example .env
# Edit .env with your backend URL
```

### 4. Database Setup

**PostgreSQL:**
```bash
# Create database
createdb autowebiq_db

# Run migrations (if applicable)
cd backend
python migrate_data.py
```

**MongoDB:**
```bash
# Start MongoDB service
mongod

# Load templates and components
cd backend
python load_templates.py
```

**Redis:**
```bash
# Start Redis service
redis-server
```

---

## 🚀 Running the Application

### Development Mode

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn server:app --reload --host 0.0.0.0 --port 8001
```

**Terminal 2 - Celery Worker:**
```bash
cd backend
source venv/bin/activate
celery -A celery_app worker --loglevel=info
```

**Terminal 3 - Celery Flower (Monitoring):**
```bash
cd backend
source venv/bin/activate
celery -A celery_app flower --port=5555
```

**Terminal 4 - Frontend:**
```bash
cd frontend
yarn start
```

Access the application at `http://localhost:3000`

### Production Mode

Use supervisor or systemd to manage services. See `supervisor.conf` for configuration.

---

## 📁 Project Structure

```
/app/
├── backend/
│   ├── server.py              # Main FastAPI app
│   ├── routes_v2.py           # V2 API endpoints (PostgreSQL/Celery/WebSocket)
│   ├── database.py            # SQLAlchemy models
│   ├── celery_app.py          # Celery configuration
│   ├── celery_tasks.py        # Background tasks
│   ├── websocket_manager.py   # WebSocket handler
│   ├── redis_cache.py         # Redis caching
│   ├── credit_system_v2.py    # Credit management
│   ├── storage_service.py     # AWS S3 integration
│   ├── template_system.py     # Template engine
│   ├── template_data.py       # Template definitions
│   ├── agents.py              # AI agent orchestration
│   └── .env                   # Environment variables
│
├── frontend/
│   ├── src/
│   │   ├── App.js             # Main React app
│   │   ├── pages/
│   │   │   ├── WorkspaceV2.js # Main workspace (V2)
│   │   │   ├── CreditsPage.js # Credit management UI
│   │   │   └── ProjectView.js # Project viewer
│   │   ├── hooks/
│   │   │   └── useBuildWebSocket.js # WebSocket hook
│   │   ├── services/
│   │   │   └── apiV2.js       # API client (V2)
│   │   └── firebaseAuth.js    # Firebase auth
│   └── .env                   # Frontend config
│
└── README.md
```

---

## 🔑 Environment Variables

### Backend (.env)

```env
# Database URLs
MONGO_URL=mongodb://localhost:27017
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/autowebiq_db
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# AI API Keys
EMERGENT_LLM_KEY=your_emergent_llm_key
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_AI_API_KEY=your_google_ai_key

# Authentication
JWT_SECRET=your_secret_key

# AWS S3
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
S3_BUCKET_NAME=your_bucket_name
CLOUDFRONT_DOMAIN=your_cloudfront_domain

# Deployment
VERCEL_TOKEN=your_vercel_token
GITHUB_PAT=your_github_pat
```

### Frontend (.env)

```env
REACT_APP_BACKEND_URL=http://localhost:8001
REACT_APP_FIREBASE_API_KEY=your_firebase_api_key
REACT_APP_FIREBASE_AUTH_DOMAIN=your_domain
REACT_APP_FIREBASE_PROJECT_ID=your_project_id
```

---

## 🔗 API Documentation

### V2 API Endpoints

**Authentication:**
- `POST /api/v2/auth/login` - User login
- `POST /api/v2/auth/register` - User registration
- `GET /api/v2/users/me` - Get current user

**Projects:**
- `GET /api/v2/projects` - List user projects
- `POST /api/v2/projects/create` - Create new project
- `GET /api/v2/projects/{project_id}` - Get project details

**Build System:**
- `POST /api/v2/build-with-agents` - Start async website build
- `GET /api/v2/build/{task_id}/status` - Check build status
- `WS /api/v2/ws/build/{project_id}` - WebSocket for real-time updates

**Credits:**
- `GET /api/v2/credits/balance` - Check credit balance
- `POST /api/v2/credits/purchase` - Purchase credits

**Templates:**
- `GET /api/templates` - List all templates
- `GET /api/templates/{id}` - Get specific template
- `GET /api/components` - List UI components

---

## 🧪 Testing

### Backend Testing
```bash
cd backend
pytest tests/
```

### Manual API Testing
```bash
# Health check
curl http://localhost:8001/api/health

# Test authentication
curl -X POST http://localhost:8001/api/v2/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password"}'
```

---

## 📊 Monitoring

- **Celery Flower**: http://localhost:5555 - Monitor async tasks
- **Backend Health**: http://localhost:8001/api/health
- **Service Status**: Check all services status

---

## 🚢 Deployment

### Vercel Deployment (Frontend)
```bash
cd frontend
vercel --prod
```

### Docker Deployment (Backend)
```bash
docker build -t autowebiq-backend .
docker run -p 8001:8001 autowebiq-backend
```

### Kubernetes (GKE)
See `k8s/` directory for Kubernetes manifests.

---

## 🗺️ Roadmap

### Phase 1: Core Platform ✅
- [x] Template library (24 templates, 50 components)
- [x] AI agent orchestration
- [x] Firebase authentication
- [x] Credit system

### Phase 2: Infrastructure Upgrade ✅
- [x] PostgreSQL integration
- [x] Redis caching
- [x] Celery async processing
- [x] WebSocket real-time updates

### Phase 3: Current Development
- [ ] GitHub integration (save/fork)
- [ ] Vercel/Netlify one-click deploy
- [ ] 9-point validation system
- [ ] Voice commands
- [ ] Buy credits flow

### Phase 4: Advanced Features
- [ ] Inline editing
- [ ] Admin dashboard
- [ ] Persistent preview URLs
- [ ] Help center/Discord integration
- [ ] CI/CD automation

---

## 📝 License

[Add your license here]

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📧 Support

For issues and questions:
- GitHub Issues: [Your Issues URL]
- Email: [Your Email]
- Discord: [Your Discord]

---

## 🙏 Acknowledgments

- OpenAI for GPT-5
- Anthropic for Claude 4.5 Sonnet
- Google for Gemini
- Firebase for authentication
- Vercel for hosting platform

---

**Built with ❤️ by the AutoWebIQ Team**
