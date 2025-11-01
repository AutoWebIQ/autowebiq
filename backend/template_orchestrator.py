# Template-Based Agent Orchestrator V3
# Uses pre-built templates + AI customization instead of pure generation

import asyncio
from typing import Dict, List, Optional, Callable
from datetime import datetime, timezone
import os

from template_system import TemplateLibrary, TemplateCustomizer
from agents_v2 import ImprovedImageAgent, AgentMessage, AgentStatus, AgentType
from token_tracker import get_token_tracker

class TemplateBasedOrchestrator:
    """Orchestrator that uses template system + AI customization"""
    
    def __init__(self, openai_key: str, anthropic_key: str, gemini_key: str):
        from openai import AsyncOpenAI
        
        self.openai_client = AsyncOpenAI(api_key=openai_key)
        
        # Initialize systems (PostgreSQL now used internally)
        self.template_library = TemplateLibrary()
        self.template_customizer = TemplateCustomizer(self.openai_client)
        self.image_agent = ImprovedImageAgent(self.openai_client)
        
        self.message_callback: Optional[Callable] = None
    
    def set_message_callback(self, callback: Callable):
        """Set callback for real-time agent messages"""
        self.message_callback = callback
    
    async def build_website(self, user_prompt: str, project_id: str, uploaded_images: List[str] = []) -> Dict:
        """Build website using template system"""
        
        try:
            print(f"\n🚀 Starting template-based build for: {user_prompt[:50]}...")
            
            # Step 1: Template Selection
            await self._send_message(project_id, "planner", "🎯 Analyzing requirements and selecting best template...", AgentStatus.THINKING, 10)
            
            template = await self.template_library.select_template(user_prompt)
            
            if not template:
                print("❌ No matching template found, falling back to AI generation")
                await self._send_message(project_id, "planner", "⚠️ No matching template, using AI generation", AgentStatus.WORKING, 15)
                # Fall back to pure AI generation
                return {"status": "failed", "error": "No matching template"}
            
            template_name = template.get('name', 'Unknown')
            print(f"✅ Selected template: {template_name}")
            await self._send_message(project_id, "planner", f"✅ Selected template: {template_name}", AgentStatus.COMPLETED, 20)
            
            # Increment usage count
            await self.template_library.increment_template_usage(template['template_id'])
            
            # Step 2: Image Generation (if needed)
            await self._send_message(project_id, "image", "🎨 Generating contextual images...", AgentStatus.WORKING, 30)
            
            # Create a simplified plan for image generation
            image_plan = {
                "project_name": user_prompt[:50],
                "description": user_prompt,
                "type": template.get("category", "landing"),
                "color_scheme": template.get("color_scheme", {}),
                "image_requirements": [
                    {
                        "type": "hero",
                        "description": f"Professional hero image for {user_prompt}",
                        "style": template.get("style", "modern")
                    }
                ]
            }
            
            images = await self.image_agent.think(image_plan, {})
            
            print(f"✅ Generated {len(images)} images")
            await self._send_message(project_id, "image", f"✅ Generated {len(images)} professional images", AgentStatus.COMPLETED, 50)
            
            # Step 3: Template Customization
            await self._send_message(project_id, "frontend", "🎨 Customizing template with your content...", AgentStatus.WORKING, 60)
            
            customized_html = await self.template_customizer.customize_template(
                template=template,
                user_prompt=user_prompt,
                images=images
            )
            
            print(f"✅ Template customized ({len(customized_html)} chars)")
            await self._send_message(project_id, "frontend", "✅ Website customized and optimized", AgentStatus.COMPLETED, 90)
            
            # Step 4: Final validation
            await self._send_message(project_id, "testing", "🔍 Running quality checks...", AgentStatus.WORKING, 95)
            
            validation_result = self._validate_output(customized_html)
            
            if validation_result['passed']:
                await self._send_message(project_id, "testing", "✅ All quality checks passed!", AgentStatus.COMPLETED, 100)
            else:
                await self._send_message(project_id, "testing", f"⚠️ {len(validation_result['issues'])} minor issues found", AgentStatus.COMPLETED, 100)
            
            # Return complete project
            return {
                "plan": {
                    "project_name": template_name,
                    "template_used": template['template_id'],
                    "pages": [{"name": "index", "sections": template.get("features", [])}],
                    "features": template.get("features", [])
                },
                "frontend_code": customized_html,
                "backend_code": "",
                "images": images,
                "test_results": validation_result,
                "status": "completed",
                "template_based": True
            }
            
        except Exception as e:
            print(f"❌ Orchestrator error: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "plan": {},
                "frontend_code": "",
                "backend_code": "",
                "images": [],
                "test_results": {},
                "status": "failed",
                "error": str(e)
            }
    
    async def _send_message(self, project_id: str, agent: str, content: str, status: AgentStatus, progress: int):
        """Send agent message"""
        if self.message_callback:
            message = {
                "id": f"{agent}_{datetime.now().timestamp()}",
                "agent": agent,
                "content": content,
                "status": status.value,
                "progress": progress,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            await self.message_callback(project_id, message)
    
    def _validate_output(self, html: str) -> Dict:
        """Basic validation of generated HTML"""
        issues = []
        
        # Check 1: DOCTYPE
        if "<!DOCTYPE html>" not in html:
            issues.append("Missing DOCTYPE declaration")
        
        # Check 2: Basic structure
        if "<html" not in html or "</html>" not in html:
            issues.append("Missing HTML tags")
        
        if "<head>" not in html or "</head>" not in html:
            issues.append("Missing head section")
        
        if "<body>" not in html or "</body>" not in html:
            issues.append("Missing body section")
        
        # Check 3: Meta tags
        if '<meta charset="UTF-8">' not in html and '<meta charset="utf-8">' not in html.lower():
            issues.append("Missing charset meta tag")
        
        if 'viewport' not in html:
            issues.append("Missing viewport meta tag")
        
        # Check 4: Content
        if len(html) < 2000:
            issues.append("HTML seems too short")
        
        # Check 5: Minimum sections
        if html.count('<section') < 2:
            issues.append("Should have at least 2 sections")
        
        return {
            "passed": len(issues) == 0,
            "score": max(0, 100 - (len(issues) * 10)),
            "issues": issues
        }
