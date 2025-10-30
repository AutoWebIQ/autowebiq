# AutoWebIQ Multi-Agent System
# This module manages the AI agent orchestration for full-stack website generation

import asyncio
import uuid
from typing import List, Dict, Optional, Callable
from datetime import datetime, timezone
from enum import Enum

class AgentType(Enum):
    """Types of agents in the system"""
    PLANNER = "planner"  # Main architect - plans the entire project
    FRONTEND = "frontend"  # Generates React/HTML/CSS/JS
    BACKEND = "backend"  # Generates FastAPI/Node backend
    DATABASE = "database"  # Designs database schemas
    TESTING = "testing"  # Tests code and APIs
    DEPLOYMENT = "deployment"  # Handles deployment
    IMAGE = "image"  # Generates/sources images
    CONTENT = "content"  # Writes copy and content

class AgentStatus(Enum):
    """Agent execution status"""
    IDLE = "idle"
    THINKING = "thinking"
    WORKING = "working"
    COMPLETED = "completed"
    FAILED = "failed"

class AgentMessage:
    """Message format for agent communication"""
    def __init__(self, agent_type: AgentType, content: str, status: AgentStatus, progress: int = 0):
        self.id = str(uuid.uuid4())
        self.agent_type = agent_type
        self.content = content
        self.status = status
        self.progress = progress  # 0-100
        self.timestamp = datetime.now(timezone.utc)
    
    def to_dict(self):
        return {
            "id": self.id,
            "agent": self.agent_type.value,
            "content": self.content,
            "status": self.status.value,
            "progress": self.progress,
            "timestamp": self.timestamp.isoformat()
        }

class Agent:
    """Base Agent class"""
    def __init__(self, agent_type: AgentType, model: str, api_client):
        self.type = agent_type
        self.model = model
        self.client = api_client
        self.status = AgentStatus.IDLE
        self.messages: List[AgentMessage] = []
    
    async def send_message(self, content: str, status: AgentStatus = AgentStatus.WORKING, progress: int = 0):
        """Send a status message"""
        msg = AgentMessage(self.type, content, status, progress)
        self.messages.append(msg)
        return msg
    
    async def think(self, prompt: str, context: Dict) -> str:
        """Main thinking/generation method - to be overridden"""
        raise NotImplementedError

class PlannerAgent(Agent):
    """Main planning agent - orchestrates the project"""
    
    def __init__(self, api_client):
        super().__init__(AgentType.PLANNER, "claude-sonnet-4-20250514", api_client)
    
    async def think(self, user_prompt: str, context: Dict) -> Dict:
        """Analyze user prompt and create project plan"""
        await self.send_message("🧠 Analyzing your requirements...", AgentStatus.THINKING, 10)
        
        system_prompt = """You are an expert software architect. Analyze the user's website request and create a detailed plan.

Return a JSON with:
{
    "project_name": "name",
    "description": "brief description",
    "type": "landing_page|webapp|ecommerce|blog|portfolio",
    "pages": ["home", "about", ...],
    "features": ["feature1", "feature2", ...],
    "needs_backend": true/false,
    "needs_database": true/false,
    "color_scheme": "modern_blue|professional_gray|...",
    "tech_stack": {
        "frontend": "React|HTML",
        "backend": "FastAPI|None",
        "database": "MongoDB|None"
    }
}"""
        
        try:
            # Call Claude Sonnet 4 for planning
            import anthropic
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                system=system_prompt,
                messages=[{
                    "role": "user",
                    "content": f"Create a plan for: {user_prompt}"
                }]
            )
            
            plan_text = response.content[0].text
            
            # Parse JSON from response
            import json
            import re
            json_match = re.search(r'\{.*\}', plan_text, re.DOTALL)
            if json_match:
                plan = json.loads(json_match.group())
            else:
                plan = {
                    "project_name": "Website",
                    "description": user_prompt,
                    "type": "landing_page",
                    "pages": ["home"],
                    "features": ["responsive design"],
                    "needs_backend": False,
                    "needs_database": False,
                    "tech_stack": {"frontend": "HTML", "backend": "None", "database": "None"}
                }
            
            await self.send_message("✅ Project plan created!", AgentStatus.COMPLETED, 100)
            return plan
            
        except Exception as e:
            await self.send_message(f"❌ Planning failed: {str(e)}", AgentStatus.FAILED, 0)
            raise

class FrontendAgent(Agent):
    """Generates frontend code"""
    
    def __init__(self, api_client):
        super().__init__(AgentType.FRONTEND, "gpt-4o", api_client)
    
    async def think(self, plan: Dict, context: Dict) -> str:
        """Generate frontend code based on plan"""
        await self.send_message("🎨 Designing user interface...", AgentStatus.THINKING, 20)
        
        system_prompt = """You are an expert frontend developer. Generate a complete, modern, responsive website.

Requirements:
- Use modern HTML5, CSS3, JavaScript
- Mobile-first responsive design
- Clean, professional styling
- Include all pages from the plan
- Add smooth animations and transitions
- Use modern color schemes
- Include placeholder images with proper alt text
- Make it production-ready

Return ONLY the complete HTML code with embedded CSS and JS."""
        
        try:
            from openai import AsyncOpenAI
            
            await self.send_message("🎨 Building components...", AgentStatus.WORKING, 50)
            
            prompt = f"""Project: {plan['project_name']}
Description: {plan['description']}
Type: {plan['type']}
Pages: {', '.join(plan['pages'])}
Features: {', '.join(plan['features'])}
Color Scheme: {plan.get('color_scheme', 'modern')}

Generate a complete, beautiful, modern website."""
            
            completion = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            html_code = completion.choices[0].message.content
            
            # Extract HTML
            if "```html" in html_code:
                html_code = html_code.split("```html")[1].split("```")[0].strip()
            elif "```" in html_code:
                html_code = html_code.split("```")[1].split("```")[0].strip()
            
            await self.send_message("✅ Frontend code generated!", AgentStatus.COMPLETED, 100)
            return html_code
            
        except Exception as e:
            await self.send_message(f"❌ Frontend generation failed: {str(e)}", AgentStatus.FAILED, 0)
            raise

class BackendAgent(Agent):
    """Generates backend API code"""
    
    def __init__(self, api_client):
        super().__init__(AgentType.BACKEND, "gpt-4o", api_client)
    
    async def think(self, plan: Dict, context: Dict) -> str:
        """Generate backend API based on plan"""
        
        if not plan.get('needs_backend'):
            await self.send_message("⏭️ No backend needed for this project", AgentStatus.COMPLETED, 100)
            return ""
        
        await self.send_message("⚙️ Designing API architecture...", AgentStatus.THINKING, 20)
        
        system_prompt = """You are an expert backend developer. Generate a complete FastAPI backend.

Requirements:
- Use FastAPI with async/await
- Include CORS middleware
- Add proper error handling
- Include all necessary endpoints
- Add Pydantic models for validation
- Use best practices for security
- Include health check endpoint
- Add proper documentation

Return ONLY the complete Python FastAPI code."""
        
        try:
            from openai import AsyncOpenAI
            
            await self.send_message("⚙️ Building API endpoints...", AgentStatus.WORKING, 60)
            
            prompt = f"""Project: {plan['project_name']}
Description: {plan['description']}
Features: {', '.join(plan['features'])}
Database: {plan['tech_stack'].get('database', 'None')}

Generate a complete FastAPI backend with all necessary endpoints."""
            
            completion = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=3000
            )
            
            backend_code = completion.choices[0].message.content
            
            # Extract Python code
            if "```python" in backend_code:
                backend_code = backend_code.split("```python")[1].split("```")[0].strip()
            elif "```" in backend_code:
                backend_code = backend_code.split("```")[1].split("```")[0].strip()
            
            await self.send_message("✅ Backend API generated!", AgentStatus.COMPLETED, 100)
            return backend_code
            
        except Exception as e:
            await self.send_message(f"❌ Backend generation failed: {str(e)}", AgentStatus.FAILED, 0)
            raise

class AgentOrchestrator:
    """Orchestrates all agents to build a complete website"""
    
    def __init__(self, openai_key: str, anthropic_key: str, gemini_key: str):
        # Initialize API clients
        from openai import AsyncOpenAI
        import anthropic
        
        self.openai_client = AsyncOpenAI(api_key=openai_key)
        self.anthropic_client = anthropic.Anthropic(api_key=anthropic_key)
        # gemini_client can be added later
        
        # Initialize agents
        self.planner = PlannerAgent(self.anthropic_client)
        self.frontend = FrontendAgent(self.openai_client)
        self.backend = BackendAgent(self.openai_client)
        
        self.all_agents = [self.planner, self.frontend, self.backend]
        self.message_callback: Optional[Callable] = None
    
    def set_message_callback(self, callback: Callable):
        """Set callback for real-time agent messages"""
        self.message_callback = callback
    
    async def build_website(self, user_prompt: str, project_id: str) -> Dict:
        """Main orchestration method - builds complete website"""
        
        try:
            # Phase 1: Planning
            plan = await self.planner.think(user_prompt, {})
            
            if self.message_callback:
                for msg in self.planner.messages:
                    await self.message_callback(project_id, msg.to_dict())
            
            # Phase 2: Frontend Generation
            frontend_code = await self.frontend.think(plan, {})
            
            if self.message_callback:
                for msg in self.frontend.messages:
                    await self.message_callback(project_id, msg.to_dict())
            
            # Phase 3: Backend Generation (if needed)
            backend_code = ""
            if plan.get('needs_backend'):
                backend_code = await self.backend.think(plan, {})
                
                if self.message_callback:
                    for msg in self.backend.messages:
                        await self.message_callback(project_id, msg.to_dict())
            
            # Return complete project
            return {
                "plan": plan,
                "frontend_code": frontend_code,
                "backend_code": backend_code,
                "status": "completed"
            }
            
        except Exception as e:
            return {
                "plan": {},
                "frontend_code": "",
                "backend_code": "",
                "status": "failed",
                "error": str(e)
            }
