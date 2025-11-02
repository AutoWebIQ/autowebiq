# Full-Stack Orchestrator for AutoWebIQ
# Coordinates Planning, Frontend, Backend, Database, and Testing agents

import asyncio
from typing import Dict, List, Optional, Callable
from datetime import datetime
import json

from fullstack_agents import (
    PlanningAgent,
    FrontendAgent,
    BackendAgent,
    DatabaseAgent,
    TestingAgent,
    AgentMessage
)


class FullStackOrchestrator:
    """
    Orchestrates the complete full-stack application generation process.
    
    Flow:
    1. Planning Agent → Analyzes requirements, creates architecture
    2. Frontend Agent → Generates React components
    3. Backend Agent → Generates FastAPI endpoints
    4. Database Agent → Creates migrations
    5. Testing Agent → Generates automated tests
    6. Package → Creates deployable project structure
    """
    
    def __init__(self):
        self.planning_agent = PlanningAgent()
        self.frontend_agent = FrontendAgent()
        self.backend_agent = BackendAgent()
        self.database_agent = DatabaseAgent()
        self.testing_agent = TestingAgent()
        
        self.message_callback: Optional[Callable] = None
        self.current_session_id: Optional[str] = None
    
    def set_message_callback(self, callback: Callable):
        """Set callback for real-time agent messages"""
        self.message_callback = callback
    
    async def build_fullstack_app(
        self, 
        user_prompt: str, 
        project_id: str
    ) -> Dict:
        """
        Build complete full-stack application from user prompt.
        
        Args:
            user_prompt: User's application requirements
            project_id: Unique project identifier
        
        Returns:
            {
                "plan": Dict,  # Architecture plan
                "files": Dict[str, str],  # All generated files
                "structure": Dict,  # Project structure
                "deployment": Dict,  # Deployment instructions
                "status": str
            }
        """
        session_id = f"fullstack_{project_id}_{datetime.utcnow().timestamp()}"
        self.current_session_id = session_id
        
        try:
            print(f"\n🚀 Starting full-stack build for: {user_prompt[:50]}...")
            
            # Send initialization message
            await self._send_message(AgentMessage(
                agent_type="system",
                status="working",
                message="🚀 Initializing Full-Stack AI System...\n\n**Models ready:**\n• Claude Sonnet 4 → Frontend (React)\n• GPT-4o → Backend (FastAPI)\n• Gemini 2.5 Pro → Planning\n• gpt-image-1 → Images",
                progress=0,
                timestamp=datetime.utcnow()
            ))
            
            await asyncio.sleep(1)
            
            # PHASE 1: Planning (Gemini)
            print("📋 Phase 1: Planning & Architecture...")
            plan = await self.planning_agent.analyze_requirements(
                user_prompt=user_prompt,
                callback=self._send_message
            )
            
            await asyncio.sleep(0.5)
            
            # PHASE 2: Frontend Generation (Claude Sonnet 4)
            print("🎨 Phase 2: Generating React Frontend...")
            frontend_files = await self.frontend_agent.generate_react_app(
                plan=plan,
                callback=self._send_message
            )
            
            await asyncio.sleep(0.5)
            
            # PHASE 3: Backend Generation (GPT-4o)
            print("⚙️ Phase 3: Generating FastAPI Backend...")
            backend_files = await self.backend_agent.generate_fastapi_backend(
                plan=plan,
                callback=self._send_message
            )
            
            await asyncio.sleep(0.5)
            
            # PHASE 4: Database Setup (GPT-4o)
            print("🗄️ Phase 4: Creating Database Migrations...")
            database_files = await self.database_agent.generate_migrations(
                plan=plan,
                callback=self._send_message
            )
            
            await asyncio.sleep(0.5)
            
            # PHASE 5: Testing (GPT-4o)
            print("🧪 Phase 5: Generating Automated Tests...")
            test_files = await self.testing_agent.generate_tests(
                plan=plan,
                callback=self._send_message
            )
            
            # Combine all files
            all_files = {}
            
            # Frontend files
            for path, content in frontend_files.items():
                all_files[f"frontend/{path}"] = content
            
            # Backend files
            for path, content in backend_files.items():
                all_files[f"backend/{path}"] = content
            
            # Database files
            for path, content in database_files.items():
                all_files[f"backend/{path}"] = content
            
            # Test files
            for path, content in test_files.items():
                all_files[f"backend/{path}"] = content
            
            # Add project files
            all_files["README.md"] = self._generate_readme(plan, user_prompt)
            all_files["docker-compose.yml"] = self._generate_docker_compose(plan)
            all_files[".gitignore"] = self._generate_gitignore()
            
            # Create project structure
            structure = self._create_project_structure(all_files)
            
            # Generate deployment instructions
            deployment = self._generate_deployment_instructions(plan)
            
            # Send completion message
            await self._send_message(AgentMessage(
                agent_type="system",
                status="completed",
                message=f"✅ **Full-Stack Application Complete!**\n\n📦 **Project Summary:**\n• Frontend: React + Vite + TailwindCSS ({len(frontend_files)} files)\n• Backend: FastAPI + SQLAlchemy ({len(backend_files)} files)\n• Database: PostgreSQL with Alembic migrations\n• Tests: pytest + comprehensive test suite\n• Total Files: {len(all_files)}\n\n🚀 **Ready to Deploy:**\n• Vercel (Frontend)\n• Railway/Render (Backend)\n• Neon/Supabase (Database)",
                progress=100,
                timestamp=datetime.utcnow()
            ))
            
            print(f"✅ Successfully generated {len(all_files)} files")
            
            return {
                "plan": plan,
                "files": all_files,
                "structure": structure,
                "deployment": deployment,
                "status": "completed",
                "fullstack": True,
                "tech_stack": plan.get("tech_stack", {}),
                "total_files": len(all_files)
            }
            
        except Exception as e:
            print(f"❌ Full-stack orchestrator error: {str(e)}")
            import traceback
            traceback.print_exc()
            
            await self._send_message(AgentMessage(
                agent_type="system",
                status="error",
                message=f"❌ Build failed: {str(e)}",
                progress=0,
                timestamp=datetime.utcnow()
            ))
            
            return {
                "status": "failed",
                "error": str(e),
                "files": {}
            }
    
    async def _send_message(self, message: AgentMessage):
        """Send message through callback if available"""
        if self.message_callback:
            try:
                await self.message_callback(message)
            except Exception as e:
                print(f"Error in message callback: {e}")
    
    def _create_project_structure(self, files: Dict[str, str]) -> Dict:
        """Create project structure from files"""
        structure = {
            "root": {
                "type": "directory",
                "children": {}
            }
        }
        
        for file_path in files.keys():
            parts = file_path.split("/")
            current = structure["root"]["children"]
            
            for i, part in enumerate(parts):
                if i == len(parts) - 1:
                    # File
                    current[part] = {
                        "type": "file",
                        "path": file_path
                    }
                else:
                    # Directory
                    if part not in current:
                        current[part] = {
                            "type": "directory",
                            "children": {}
                        }
                    current = current[part]["children"]
        
        return structure
    
    def _generate_readme(self, plan: Dict, user_prompt: str) -> str:
        """Generate comprehensive README.md"""
        project_name = plan.get("project_name", "Full-Stack Application")
        app_type = plan.get("app_type", "web application")
        
        return f"""# {project_name}

> {plan.get("description", user_prompt)}

A modern full-stack {app_type} built with React, FastAPI, and PostgreSQL.

## 🚀 Tech Stack

### Frontend
- **React 18** - Modern UI library
- **Vite** - Lightning-fast build tool
- **TailwindCSS** - Utility-first CSS framework
- **React Router v6** - Client-side routing
- **Axios** - HTTP client

### Backend
- **FastAPI** - High-performance Python API framework
- **SQLAlchemy** - Python SQL toolkit and ORM
- **PostgreSQL** - Powerful relational database
- **JWT Authentication** - Secure user authentication
- **Alembic** - Database migrations

### Testing
- **pytest** - Python testing framework
- **Jest** - JavaScript testing framework

## 📦 Project Structure

```
{project_name.lower().replace(' ', '-')}/
├── frontend/           # React application
│   ├── src/
│   │   ├── pages/     # Page components
│   │   ├── components/ # Reusable components
│   │   ├── App.jsx    # Main app component
│   │   └── main.jsx   # Entry point
│   ├── package.json
│   └── vite.config.js
├── backend/            # FastAPI application
│   ├── routes/        # API endpoints
│   ├── models.py      # Database models
│   ├── database.py    # Database configuration
│   ├── auth.py        # Authentication logic
│   ├── main.py        # FastAPI app
│   └── requirements.txt
├── docker-compose.yml
└── README.md
```

## 🛠️ Setup Instructions

### Prerequisites
- Node.js 18+ and npm/yarn
- Python 3.10+
- PostgreSQL 14+
- Docker (optional)

### Quick Start with Docker

```bash
# Start all services
docker-compose up -d

# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Manual Setup

#### 1. Database Setup

```bash
# Create PostgreSQL database
createdb {project_name.lower().replace(' ', '_')}

# Or use connection string in .env
DATABASE_URL=postgresql://user:password@localhost/{project_name.lower().replace(' ', '_')}
```

#### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
# Edit .env with your database credentials

# Run migrations
alembic upgrade head

# Start backend server
uvicorn main:app --reload --port 8000
```

Backend will be available at http://localhost:8000

API Documentation: http://localhost:8000/docs

#### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
# or
yarn install

# Start development server
npm run dev
# or
yarn dev
```

Frontend will be available at http://localhost:3000

## 🧪 Running Tests

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 🌐 Deployment

### Frontend (Vercel)
```bash
cd frontend
vercel --prod
```

### Backend (Railway/Render)
```bash
cd backend
# Push to GitHub and connect to Railway/Render
# Add environment variables in dashboard
```

### Database (Neon/Supabase)
- Create PostgreSQL database on Neon or Supabase
- Update `DATABASE_URL` in backend environment variables
- Run migrations: `alembic upgrade head`

## 📋 Features

{self._format_features_list(plan.get('features', []))}

## 🔐 Authentication

JWT-based authentication with access tokens.

### Endpoints:
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get access token
- `GET /api/auth/me` - Get current user (requires auth)

## 📚 API Documentation

Interactive API documentation available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 💡 Generated by AutoWebIQ

This full-stack application was generated by [AutoWebIQ](https://autowebiq.com) - AI-powered full-stack development platform.

---

**Happy Coding! 🚀**
"""
    
    def _format_features_list(self, features: List[str]) -> str:
        """Format features as markdown list"""
        if not features:
            return "- Modern full-stack application"
        return "\n".join([f"- {feature}" for feature in features])
    
    def _generate_docker_compose(self, plan: Dict) -> str:
        """Generate docker-compose.yml"""
        project_name = plan.get("project_name", "app").lower().replace(" ", "-")
        
        return f"""version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: {project_name}-db
    environment:
      POSTGRES_DB: {project_name}_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: {project_name}-backend
    environment:
      DATABASE_URL: postgresql://postgres:postgres@postgres:5432/{project_name}_db
      SECRET_KEY: dev-secret-key-change-in-production
      CORS_ORIGINS: http://localhost:3000
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - ./backend:/app
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: {project_name}-frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm run dev -- --host

volumes:
  postgres_data:
"""
    
    def _generate_gitignore(self) -> str:
        """Generate .gitignore"""
        return """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
.venv

# Node
node_modules/
dist/
build/
.env.local
.env.development.local
.env.test.local
.env.production.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Environment
.env
.env.local

# Database
*.db
*.sqlite
*.sqlite3

# Logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# OS
.DS_Store
Thumbs.db

# Testing
.coverage
htmlcov/
.pytest_cache/

# Misc
*.bak
*.tmp
"""
    
    def _generate_deployment_instructions(self, plan: Dict) -> Dict:
        """Generate deployment instructions"""
        return {
            "frontend": {
                "platform": "Vercel",
                "steps": [
                    "1. Push code to GitHub",
                    "2. Import project to Vercel",
                    "3. Set build command: npm run build",
                    "4. Set output directory: dist",
                    "5. Add environment variable: VITE_API_URL"
                ],
                "env_vars": [
                    "VITE_API_URL=https://your-backend.railway.app"
                ]
            },
            "backend": {
                "platform": "Railway",
                "steps": [
                    "1. Push code to GitHub",
                    "2. Create new Railway project",
                    "3. Add PostgreSQL service",
                    "4. Deploy backend service",
                    "5. Run migrations: railway run alembic upgrade head"
                ],
                "env_vars": [
                    "DATABASE_URL=[Provided by Railway]",
                    "SECRET_KEY=[Generate secure key]",
                    "CORS_ORIGINS=https://your-frontend.vercel.app"
                ]
            },
            "database": {
                "platform": "Neon",
                "steps": [
                    "1. Create account on neon.tech",
                    "2. Create new PostgreSQL database",
                    "3. Copy connection string",
                    "4. Update DATABASE_URL in backend",
                    "5. Run migrations"
                ]
            }
        }
