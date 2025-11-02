# Full-Stack Development Agents for AutoWebIQ
# Multi-Agent System for generating complete React + FastAPI + PostgreSQL applications

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from model_router import get_model_router
from dataclasses import dataclass
import json
import re

@dataclass
class AgentMessage:
    """Message from an agent during execution"""
    agent_type: str
    status: str  # thinking, working, completed, error
    message: str
    progress: int
    timestamp: datetime
    details: Optional[Dict] = None


class PlanningAgent:
    """
    Analyzes requirements and creates full-stack architecture plan.
    Uses Gemini 2.5 Pro for requirement analysis and planning.
    """
    
    def __init__(self):
        self.router = get_model_router()
        self.agent_type = "planner"
    
    async def analyze_requirements(self, user_prompt: str, callback=None) -> Dict:
        """
        Analyze user requirements and create detailed project plan.
        
        Returns:
            {
                "project_name": str,
                "description": str,
                "app_type": str,  # saas, ecommerce, portfolio, etc.
                "features": List[str],
                "pages": List[Dict],  # Frontend pages
                "api_endpoints": List[Dict],  # Backend APIs
                "database_models": List[Dict],  # DB schema
                "tech_stack": Dict,
                "deployment": Dict
            }
        """
        if callback:
            await callback(AgentMessage(
                agent_type=self.agent_type,
                status="thinking",
                message="🤔 Analyzing your requirements...",
                progress=10,
                timestamp=datetime.utcnow()
            ))
        
        # Use Gemini for content/planning analysis
        system_message = """You are an expert software architect specializing in full-stack web applications.
Analyze the user's requirements and create a detailed technical plan.

Return ONLY a JSON object with this structure:
{
  "project_name": "descriptive name",
  "description": "detailed description",
  "app_type": "saas|ecommerce|portfolio|blog|dashboard|marketplace",
  "features": ["feature1", "feature2"],
  "pages": [
    {
      "name": "Home",
      "route": "/",
      "components": ["Navbar", "Hero", "Features", "Footer"],
      "auth_required": false
    }
  ],
  "api_endpoints": [
    {
      "path": "/api/users",
      "method": "GET",
      "description": "Get all users",
      "auth_required": true
    }
  ],
  "database_models": [
    {
      "name": "User",
      "fields": [
        {"name": "id", "type": "Integer", "primary_key": true},
        {"name": "email", "type": "String", "unique": true}
      ]
    }
  ],
  "tech_stack": {
    "frontend": "React + Vite + TailwindCSS",
    "backend": "FastAPI + SQLAlchemy",
    "database": "PostgreSQL",
    "auth": "JWT"
  },
  "deployment": {
    "frontend": "Vercel",
    "backend": "Railway",
    "database": "Neon PostgreSQL"
  }
}"""

        prompt = f"""Analyze this application requirement and create a complete technical plan:

"{user_prompt}"

Create a comprehensive architecture including:
1. All frontend pages needed
2. All backend API endpoints required
3. Complete database schema
4. Authentication/authorization strategy
5. Deployment approach

Return the plan as a JSON object."""

        try:
            response = await self.router.generate_completion(
                task_type="content",  # Gemini for planning
                prompt=prompt,
                system_message=system_message,
                session_id=f"planning_{datetime.utcnow().timestamp()}"
            )
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                plan = json.loads(json_match.group())
                
                if callback:
                    await callback(AgentMessage(
                        agent_type=self.agent_type,
                        status="completed",
                        message=f"✅ Project Plan Created\n**Type**: {plan.get('app_type', 'web app')}\n**Pages**: {len(plan.get('pages', []))}\n**API Endpoints**: {len(plan.get('api_endpoints', []))}\n**Database Models**: {len(plan.get('database_models', []))}",
                        progress=25,
                        timestamp=datetime.utcnow(),
                        details=plan
                    ))
                
                return plan
            else:
                raise ValueError("No valid JSON found in planning response")
                
        except Exception as e:
            if callback:
                await callback(AgentMessage(
                    agent_type=self.agent_type,
                    status="error",
                    message=f"❌ Planning failed: {str(e)}",
                    progress=0,
                    timestamp=datetime.utcnow()
                ))
            raise


class FrontendAgent:
    """
    Generates React components and frontend code.
    Uses Claude Sonnet 4 for superior UI/UX generation.
    """
    
    def __init__(self):
        self.router = get_model_router()
        self.agent_type = "frontend"
    
    async def generate_react_app(self, plan: Dict, callback=None) -> Dict[str, str]:
        """
        Generate complete React application with components.
        
        Returns:
            {
                "src/App.jsx": "code",
                "src/pages/Home.jsx": "code",
                "src/components/Navbar.jsx": "code",
                "src/index.css": "code",
                "package.json": "code",
                ...
            }
        """
        if callback:
            await callback(AgentMessage(
                agent_type=self.agent_type,
                status="working",
                message="🎨 Claude Sonnet 4 generating React components...",
                progress=30,
                timestamp=datetime.utcnow()
            ))
        
        files = {}
        
        # Generate main App.jsx
        app_jsx = await self._generate_app_jsx(plan)
        files["src/App.jsx"] = app_jsx
        
        # Generate pages
        for page in plan.get("pages", []):
            page_code = await self._generate_page(page, plan)
            page_name = page.get("name", "Page").replace(" ", "")
            files[f"src/pages/{page_name}.jsx"] = page_code
        
        # Generate components
        components = self._extract_unique_components(plan)
        for component in components:
            comp_code = await self._generate_component(component, plan)
            files[f"src/components/{component}.jsx"] = comp_code
        
        # Generate CSS
        files["src/index.css"] = self._generate_tailwind_css()
        
        # Generate package.json
        files["package.json"] = self._generate_package_json(plan)
        
        # Generate vite.config.js
        files["vite.config.js"] = self._generate_vite_config()
        
        # Generate index.html
        files["index.html"] = self._generate_index_html(plan)
        
        if callback:
            await callback(AgentMessage(
                agent_type=self.agent_type,
                status="completed",
                message=f"✅ React App Generated\n**Files**: {len(files)}\n**Components**: {len(components)}\n**Pages**: {len(plan.get('pages', []))}",
                progress=50,
                timestamp=datetime.utcnow()
            ))
        
        return files
    
    async def _generate_app_jsx(self, plan: Dict) -> str:
        """Generate main App.jsx with routing"""
        system_message = """You are an expert React developer. Generate clean, modern React code using React Router v6.
Use functional components, hooks, and best practices. Include proper prop-types and JSX."""

        prompt = f"""Generate the main App.jsx for a {plan.get('app_type', 'web')} application.

Project: {plan.get('project_name', 'App')}
Pages: {', '.join([p.get('name', '') for p in plan.get('pages', [])])}

Requirements:
1. Use React Router v6 for routing
2. Include all pages from the plan
3. Add proper navigation
4. Use TailwindCSS for styling
5. Include authentication guard for protected routes

Return ONLY the complete App.jsx code, no explanations."""

        response = await self.router.generate_completion(
            task_type="frontend",  # Claude Sonnet 4
            prompt=prompt,
            system_message=system_message,
            session_id=f"frontend_app_{datetime.utcnow().timestamp()}"
        )
        
        return self._extract_code(response)
    
    async def _generate_page(self, page: Dict, plan: Dict) -> str:
        """Generate individual page component"""
        system_message = """You are an expert React developer. Generate modern, responsive page components.
Use TailwindCSS for styling. Include proper hooks and state management."""

        components_list = ', '.join(page.get('components', []))
        
        prompt = f"""Generate a React page component for: {page.get('name', 'Page')}

Route: {page.get('route', '/')}
Components needed: {components_list}
Auth required: {page.get('auth_required', False)}
App type: {plan.get('app_type', 'web')}

Requirements:
1. Use functional component with hooks
2. Include all required sub-components
3. Use TailwindCSS for responsive design
4. Add proper error handling
5. Include loading states

Return ONLY the complete page component code."""

        response = await self.router.generate_completion(
            task_type="frontend",
            prompt=prompt,
            system_message=system_message,
            session_id=f"frontend_page_{datetime.utcnow().timestamp()}"
        )
        
        return self._extract_code(response)
    
    async def _generate_component(self, component_name: str, plan: Dict) -> str:
        """Generate reusable component"""
        system_message = """You are an expert React developer. Create reusable, well-documented components.
Use TypeScript-style prop validation with PropTypes. Include accessibility features."""

        prompt = f"""Generate a React component: {component_name}

App type: {plan.get('app_type', 'web')}
Project: {plan.get('project_name', 'App')}

Requirements:
1. Make it reusable and configurable via props
2. Use TailwindCSS for styling
3. Include PropTypes validation
4. Add proper accessibility (ARIA)
5. Include responsive design

Return ONLY the component code."""

        response = await self.router.generate_completion(
            task_type="frontend",
            prompt=prompt,
            system_message=system_message,
            session_id=f"frontend_comp_{datetime.utcnow().timestamp()}"
        )
        
        return self._extract_code(response)
    
    def _extract_unique_components(self, plan: Dict) -> List[str]:
        """Extract unique component names from plan"""
        components = set()
        for page in plan.get("pages", []):
            for comp in page.get("components", []):
                components.add(comp)
        return list(components)
    
    def _extract_code(self, response: str) -> str:
        """Extract code from AI response, removing markdown"""
        # Remove markdown code blocks
        code = re.sub(r'^```[a-z]*\n', '', response, flags=re.MULTILINE)
        code = re.sub(r'\n```$', '', code, flags=re.MULTILINE)
        return code.strip()
    
    def _generate_tailwind_css(self) -> str:
        """Generate base Tailwind CSS"""
        return """@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  body {
    @apply bg-gray-50 text-gray-900;
  }
}

@layer components {
  .btn-primary {
    @apply bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors;
  }
  
  .btn-secondary {
    @apply bg-gray-200 text-gray-800 px-6 py-3 rounded-lg hover:bg-gray-300 transition-colors;
  }
  
  .card {
    @apply bg-white rounded-xl shadow-lg p-6;
  }
}"""
    
    def _generate_package_json(self, plan: Dict) -> str:
        """Generate package.json"""
        return json.dumps({
            "name": plan.get("project_name", "app").lower().replace(" ", "-"),
            "version": "1.0.0",
            "type": "module",
            "scripts": {
                "dev": "vite",
                "build": "vite build",
                "preview": "vite preview",
                "lint": "eslint . --ext js,jsx"
            },
            "dependencies": {
                "react": "^18.3.1",
                "react-dom": "^18.3.1",
                "react-router-dom": "^6.22.0",
                "axios": "^1.6.7"
            },
            "devDependencies": {
                "@vitejs/plugin-react": "^4.2.1",
                "vite": "^5.1.0",
                "tailwindcss": "^3.4.1",
                "postcss": "^8.4.35",
                "autoprefixer": "^10.4.17",
                "eslint": "^8.56.0"
            }
        }, indent=2)
    
    def _generate_vite_config(self) -> str:
        """Generate vite.config.js"""
        return """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})"""
    
    def _generate_index_html(self, plan: Dict) -> str:
        """Generate index.html"""
        project_name = plan.get("project_name", "App")
        return f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{project_name}</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>"""


class BackendAgent:
    """
    Generates FastAPI backend code with authentication and database integration.
    Uses GPT-4o for technical backend logic.
    """
    
    def __init__(self):
        self.router = get_model_router()
        self.agent_type = "backend"
    
    async def generate_fastapi_backend(self, plan: Dict, callback=None) -> Dict[str, str]:
        """
        Generate complete FastAPI backend.
        
        Returns dictionary of files:
            {
                "main.py": "code",
                "models.py": "code",
                "database.py": "code",
                "routes/users.py": "code",
                "requirements.txt": "deps"
            }
        """
        if callback:
            await callback(AgentMessage(
                agent_type=self.agent_type,
                status="working",
                message="⚙️ GPT-4o generating FastAPI backend...",
                progress=55,
                timestamp=datetime.utcnow()
            ))
        
        files = {}
        
        # Generate main.py
        files["main.py"] = await self._generate_main_py(plan)
        
        # Generate database.py
        files["database.py"] = self._generate_database_py()
        
        # Generate models.py
        files["models.py"] = await self._generate_models_py(plan)
        
        # Generate API routes
        for endpoint_group in self._group_endpoints(plan):
            route_file = await self._generate_route_file(endpoint_group, plan)
            files[f"routes/{endpoint_group['name']}.py"] = route_file
        
        # Generate auth.py
        files["auth.py"] = self._generate_auth_py()
        
        # Generate requirements.txt
        files["requirements.txt"] = self._generate_requirements_txt()
        
        # Generate .env.example
        files[".env.example"] = self._generate_env_example()
        
        if callback:
            await callback(AgentMessage(
                agent_type=self.agent_type,
                status="completed",
                message=f"✅ FastAPI Backend Generated\n**Files**: {len(files)}\n**Endpoints**: {len(plan.get('api_endpoints', []))}\n**Models**: {len(plan.get('database_models', []))}",
                progress=75,
                timestamp=datetime.utcnow()
            ))
        
        return files
    
    async def _generate_main_py(self, plan: Dict) -> str:
        """Generate main FastAPI application"""
        system_message = """You are an expert FastAPI developer. Generate production-ready FastAPI applications.
Include proper error handling, CORS, middleware, and documentation."""

        endpoints_count = len(plan.get('api_endpoints', []))
        
        prompt = f"""Generate main.py for a FastAPI application.

Project: {plan.get('project_name', 'API')}
Type: {plan.get('app_type', 'web')}
Endpoints: {endpoints_count}
Authentication: JWT

Requirements:
1. FastAPI app with proper configuration
2. CORS middleware
3. Database session management
4. JWT authentication integration
5. API documentation
6. Error handlers
7. Health check endpoint

Return ONLY the complete main.py code."""

        response = await self.router.generate_completion(
            task_type="backend",  # GPT-4o
            prompt=prompt,
            system_message=system_message,
            session_id=f"backend_main_{datetime.utcnow().timestamp()}"
        )
        
        return self._extract_code(response)
    
    async def _generate_models_py(self, plan: Dict) -> str:
        """Generate SQLAlchemy models"""
        system_message = """You are an expert in SQLAlchemy and database modeling.
Generate well-structured models with proper relationships and constraints."""

        models_json = json.dumps(plan.get('database_models', []), indent=2)
        
        prompt = f"""Generate SQLAlchemy models for this schema:

{models_json}

Requirements:
1. Use SQLAlchemy ORM with proper typing
2. Include relationships between models
3. Add indexes for performance
4. Include timestamps (created_at, updated_at)
5. Add proper constraints and validations

Return ONLY the complete models.py code."""

        response = await self.router.generate_completion(
            task_type="backend",
            prompt=prompt,
            system_message=system_message,
            session_id=f"backend_models_{datetime.utcnow().timestamp()}"
        )
        
        return self._extract_code(response)
    
    async def _generate_route_file(self, endpoint_group: Dict, plan: Dict) -> str:
        """Generate route file for endpoint group"""
        system_message = """You are an expert FastAPI developer. Generate RESTful API routes.
Include proper validation, error handling, and documentation."""

        endpoints_json = json.dumps(endpoint_group['endpoints'], indent=2)
        
        prompt = f"""Generate FastAPI routes for {endpoint_group['name']}:

Endpoints:
{endpoints_json}

Requirements:
1. Use FastAPI APIRouter
2. Include Pydantic models for request/response
3. Add proper status codes
4. Include authentication where needed
5. Add comprehensive docstrings
6. Handle errors gracefully

Return ONLY the complete route file code."""

        response = await self.router.generate_completion(
            task_type="backend",
            prompt=prompt,
            system_message=system_message,
            session_id=f"backend_routes_{datetime.utcnow().timestamp()}"
        )
        
        return self._extract_code(response)
    
    def _group_endpoints(self, plan: Dict) -> List[Dict]:
        """Group API endpoints by resource"""
        groups = {}
        for endpoint in plan.get('api_endpoints', []):
            path = endpoint.get('path', '/api/items')
            resource = path.split('/')[2] if len(path.split('/')) > 2 else 'main'
            
            if resource not in groups:
                groups[resource] = {
                    'name': resource,
                    'endpoints': []
                }
            groups[resource]['endpoints'].append(endpoint)
        
        return list(groups.values())
    
    def _extract_code(self, response: str) -> str:
        """Extract code from AI response"""
        code = re.sub(r'^```[a-z]*\n', '', response, flags=re.MULTILINE)
        code = re.sub(r'\n```$', '', code, flags=re.MULTILINE)
        return code.strip()
    
    def _generate_database_py(self) -> str:
        """Generate database configuration"""
        return """from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/dbname")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()"""
    
    def _generate_auth_py(self) -> str:
        """Generate JWT authentication"""
        return """from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import os

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt"""
    
    def _generate_requirements_txt(self) -> str:
        """Generate Python dependencies"""
        return """fastapi==0.110.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.27
psycopg2-binary==2.9.9
pydantic==2.6.1
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.9
python-dotenv==1.0.1
alembic==1.13.1"""
    
    def _generate_env_example(self) -> str:
        """Generate .env.example"""
        return """DATABASE_URL=postgresql://user:password@localhost/dbname
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=http://localhost:3000"""


class DatabaseAgent:
    """
    Creates database migrations and schema setup.
    Uses GPT-4o for database logic.
    """
    
    def __init__(self):
        self.router = get_model_router()
        self.agent_type = "database"
    
    async def generate_migrations(self, plan: Dict, callback=None) -> Dict[str, str]:
        """Generate Alembic migrations"""
        if callback:
            await callback(AgentMessage(
                agent_type=self.agent_type,
                status="working",
                message="🗄️ Generating database migrations...",
                progress=80,
                timestamp=datetime.utcnow()
            ))
        
        files = {}
        
        # Generate alembic.ini
        files["alembic.ini"] = self._generate_alembic_ini()
        
        # Generate env.py
        files["alembic/env.py"] = self._generate_alembic_env()
        
        # Generate initial migration
        files["alembic/versions/001_initial.py"] = await self._generate_initial_migration(plan)
        
        if callback:
            await callback(AgentMessage(
                agent_type=self.agent_type,
                status="completed",
                message="✅ Database Migrations Created",
                progress=85,
                timestamp=datetime.utcnow()
            ))
        
        return files
    
    async def _generate_initial_migration(self, plan: Dict) -> str:
        """Generate initial Alembic migration"""
        system_message = """You are a database expert. Generate Alembic migration scripts.
Include proper up/down functions and all constraints."""

        models_json = json.dumps(plan.get('database_models', []), indent=2)
        
        prompt = f"""Generate an Alembic migration for these models:

{models_json}

Requirements:
1. Create all tables with proper columns
2. Add indexes and foreign keys
3. Include upgrade() and downgrade() functions
4. Use Alembic op operations

Return ONLY the migration code."""

        response = await self.router.generate_completion(
            task_type="backend",
            prompt=prompt,
            system_message=system_message,
            session_id=f"database_migration_{datetime.utcnow().timestamp()}"
        )
        
        return self._extract_code(response)
    
    def _extract_code(self, response: str) -> str:
        """Extract code from response"""
        code = re.sub(r'^```[a-z]*\n', '', response, flags=re.MULTILINE)
        code = re.sub(r'\n```$', '', code, flags=re.MULTILINE)
        return code.strip()
    
    def _generate_alembic_ini(self) -> str:
        """Generate alembic.ini configuration"""
        return """[alembic]
script_location = alembic
prepend_sys_path = .
version_path_separator = os

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S"""
    
    def _generate_alembic_env(self) -> str:
        """Generate alembic/env.py"""
        return """from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import Base
from models import *

config = context.config
fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()"""


class TestingAgent:
    """
    Generates automated tests for backend and frontend.
    Uses GPT-4o for test generation.
    """
    
    def __init__(self):
        self.router = get_model_router()
        self.agent_type = "testing"
    
    async def generate_tests(self, plan: Dict, callback=None) -> Dict[str, str]:
        """Generate test files"""
        if callback:
            await callback(AgentMessage(
                agent_type=self.agent_type,
                status="working",
                message="🧪 Generating automated tests...",
                progress=90,
                timestamp=datetime.utcnow()
            ))
        
        files = {}
        
        # Backend tests
        files["tests/test_main.py"] = await self._generate_backend_tests(plan)
        files["tests/conftest.py"] = self._generate_pytest_conftest()
        
        # Frontend tests would go here (Jest)
        # files["src/__tests__/App.test.jsx"] = await self._generate_frontend_tests(plan)
        
        if callback:
            await callback(AgentMessage(
                agent_type=self.agent_type,
                status="completed",
                message="✅ Tests Generated",
                progress=95,
                timestamp=datetime.utcnow()
            ))
        
        return files
    
    async def _generate_backend_tests(self, plan: Dict) -> str:
        """Generate pytest tests for backend"""
        system_message = """You are an expert in testing FastAPI applications.
Generate comprehensive pytest tests with fixtures and proper assertions."""

        endpoints_json = json.dumps(plan.get('api_endpoints', [])[:5], indent=2)
        
        prompt = f"""Generate pytest tests for these API endpoints:

{endpoints_json}

Requirements:
1. Use pytest fixtures
2. Test successful cases and error cases
3. Include authentication tests
4. Test database operations
5. Use proper assertions

Return ONLY the test code."""

        response = await self.router.generate_completion(
            task_type="backend",
            prompt=prompt,
            system_message=system_message,
            session_id=f"testing_{datetime.utcnow().timestamp()}"
        )
        
        return self._extract_code(response)
    
    def _extract_code(self, response: str) -> str:
        """Extract code from response"""
        code = re.sub(r'^```[a-z]*\n', '', response, flags=re.MULTILINE)
        code = re.sub(r'\n```$', '', code, flags=re.MULTILINE)
        return code.strip()
    
    def _generate_pytest_conftest(self) -> str:
        """Generate pytest configuration"""
        return """import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    return TestClient(app)"""
