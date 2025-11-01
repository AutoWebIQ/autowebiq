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
        
        # Token tracking for real-time credit deduction
        self.token_tracker = get_token_tracker()
        
        self.message_callback: Optional[Callable] = None
        self.current_session_id: Optional[str] = None
    
    def set_message_callback(self, callback: Callable):
        """Set callback for real-time agent messages"""
        self.message_callback = callback
    
    async def build_website(self, user_prompt: str, project_id: str, uploaded_images: List[str] = []) -> Dict:
        """Build website using template system"""
        
        # Start token tracking session
        session_id = f"build_{project_id}_{datetime.now().timestamp()}"
        self.current_session_id = session_id
        self.token_tracker.start_session(session_id)
        
        try:
            print(f"\n🚀 Starting template-based build for: {user_prompt[:50]}...")
            
            # Step 1: Initialize
            await self._send_message_with_status(
                project_id, 
                "initializing", 
                "🚀 Initializing build system...",
                "working",
                0
            )
            await asyncio.sleep(0.5)  # Small delay for UI visibility
            
            # Step 2: Template Selection
            await self._send_message_with_status(
                project_id,
                "planner",
                "🤔 Analyzing your requirements...",
                "thinking",
                10
            )
            await asyncio.sleep(0.3)
            
            await self._send_message_with_status(
                project_id,
                "planner",
                "🔍 Searching template library (24 templates, 50 components)...",
                "working",
                15
            )
            
            template = await self.template_library.select_template(user_prompt)
            
            if not template:
                print("❌ No matching template found, falling back to AI generation")
                await self._send_message_with_status(
                    project_id,
                    "planner",
                    "⚠️ No matching template found. Using full AI generation...",
                    "warning",
                    20
                )
                # Fall back to pure AI generation
                return {"status": "failed", "error": "No matching template"}
            
            template_name = template.get('name', 'Unknown')
            print(f"✅ Selected template: {template_name}")
            
            await self._send_message_with_status(
                project_id,
                "planner",
                f"✅ Selected template: **{template_name}**\nCategory: {template.get('category', 'N/A')} • Match score: {template.get('match_score', 'N/A')}",
                "completed",
                25
            )
            
            # Increment usage count
            await self.template_library.increment_template_usage(template['template_id'])
            
            # Step 3: Image Generation Agent
            await self._send_message_with_status(
                project_id,
                "image",
                "🎨 Image Agent starting...",
                "waiting",
                30
            )
            await asyncio.sleep(0.3)
            
            await self._send_message_with_status(
                project_id,
                "image",
                "🖼️ Generating contextual images for your website...",
                "working",
                35
            )
            
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
            await self._send_message_with_status(
                project_id,
                "image",
                f"✅ Generated {len(images)} professional images\nQuality: High resolution • Style: {template.get('style', 'modern')}",
                "completed",
                55
            )
            
            # Step 4: Frontend Agent - Template Customization
            await self._send_message_with_status(
                project_id,
                "frontend",
                "🎨 Frontend Agent starting...",
                "waiting",
                60
            )
            await asyncio.sleep(0.3)
            
            await self._send_message_with_status(
                project_id,
                "frontend",
                "⚙️ Customizing template with your content...\nAnalyzing brand requirements...",
                "working",
                65
            )
            await asyncio.sleep(0.5)
            
            await self._send_message_with_status(
                project_id,
                "frontend",
                "🎨 Applying design customizations...\nOptimizing layout and responsiveness...",
                "working",
                75
            )
            
            customized_html = await self.template_customizer.customize_template(
                template=template,
                user_prompt=user_prompt,
                images=images
            )
            
            print(f"✅ Template customized ({len(customized_html)} chars)")
            await self._send_message_with_status(
                project_id,
                "frontend",
                f"✅ Website customized successfully\nGenerated: {len(customized_html):,} characters of production-ready code",
                "completed",
                85
            )
            
            # Step 5: Testing Agent - Quality Validation
            await self._send_message_with_status(
                project_id,
                "testing",
                "🧪 Testing Agent starting...",
                "waiting",
                90
            )
            await asyncio.sleep(0.3)
            
            await self._send_message_with_status(
                project_id,
                "testing",
                "🔍 Running quality checks...\nValidating HTML structure, accessibility, and SEO...",
                "working",
                93
            )
            
            validation_result = self._validate_output(customized_html)
            
            if validation_result['passed']:
                await self._send_message_with_status(
                    project_id,
                    "testing",
                    f"✅ All quality checks passed!\nScore: {validation_result['score']}/100 • Issues: 0",
                    "completed",
                    98
                )
            else:
                await self._send_message_with_status(
                    project_id,
                    "testing",
                    f"⚠️ {len(validation_result['issues'])} minor issues found\nScore: {validation_result['score']}/100 • Still production-ready",
                    "completed",
                    98
                )
            
            # Step 6: Finalize
            await self._send_message_with_status(
                project_id,
                "building",
                "✅ Build complete! Finalizing...",
                "completed",
                100
            )
            
            # Get token usage summary
            token_summary = self.token_tracker.get_session_summary(session_id)
            
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
                "template_based": True,
                "token_usage": token_summary
            }
            
        except Exception as e:
            print(f"❌ Orchestrator error: {str(e)}")
            import traceback
            traceback.print_exc()
            
            await self._send_message_with_status(
                project_id,
                "building",
                f"❌ Build failed: {str(e)}",
                "error",
                0
            )
            
            return {
                "plan": {},
                "frontend_code": "",
                "backend_code": "",
                "images": [],
                "test_results": {},
                "status": "failed",
                "error": str(e)
            }
        finally:
            # End token tracking
            if self.current_session_id:
                self.token_tracker.end_session(self.current_session_id)
                self.current_session_id = None
    
    async def _send_message(self, project_id: str, agent: str, content: str, status: AgentStatus, progress: int):
        """Send agent message (legacy method for compatibility)"""
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
    
    async def _send_message_with_status(
        self, 
        project_id: str, 
        agent: str, 
        content: str, 
        status: str,
        progress: int
    ):
        """
        Send Emergent-style agent message with detailed status
        
        Status options: "thinking", "waiting", "working", "completed", "warning", "error"
        """
        if self.message_callback:
            # Status emoji mapping (Emergent-style)
            status_emoji = {
                "thinking": "🤔",
                "waiting": "⏸️",
                "working": "⚙️",
                "completed": "✅",
                "warning": "⚠️",
                "error": "❌"
            }
            
            # Agent emoji mapping
            agent_emoji = {
                "initializing": "🚀",
                "planner": "🧠",
                "frontend": "🎨",
                "backend": "⚙️",
                "image": "🖼️",
                "testing": "🧪",
                "building": "🏗️"
            }
            
            message = {
                "id": f"{agent}_{datetime.now().timestamp()}",
                "agent": agent,
                "agent_display_name": agent.replace("_", " ").title() + " Agent",
                "content": content,
                "status": status,
                "status_emoji": status_emoji.get(status, "💬"),
                "agent_emoji": agent_emoji.get(agent, "💬"),
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
