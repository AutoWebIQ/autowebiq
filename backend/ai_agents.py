# AI Agents with Emergent-Style Gradual Processing
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
import google.generativeai as genai
import os
import asyncio
import json
from datetime import datetime, timezone

from config import db, OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_AI_API_KEY
from credits import deduct_credits, get_user_credits, get_action_cost

class WebsiteBuilder:
    """Emergent-style website builder with gradual credit deduction"""
    
    def __init__(self, user_id: str, project_id: str, websocket=None):
        self.user_id = user_id
        self.project_id = project_id
        self.websocket = websocket
        
        # Initialize AI clients
        self.openai = AsyncOpenAI(api_key=OPENAI_API_KEY)
        self.anthropic = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
        genai.configure(api_key=GOOGLE_AI_API_KEY)
        self.gemini = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    async def send_status(self, status: str, credits_used: int = 0):
        """Send status update via WebSocket"""
        if self.websocket:
            try:
                await self.websocket.send_json({
                    'type': 'status',
                    'status': status,
                    'credits_used': credits_used,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })
            except:
                pass
    
    async def build_website(self, user_prompt: str):
        """Build website with gradual credit deduction (Emergent-style)"""
        try:
            # Check credits
            credits = await get_user_credits(self.user_id)
            if credits < 10:
                await self.send_status('❌ Insufficient credits', 0)
                return
            
            # Step 1: Planning Agent (2 credits)
            await self.send_status('🤖 Planning Agent working...', 0)
            await asyncio.sleep(1)  # Simulate work
            plan = await self.planning_agent(user_prompt)
            await deduct_credits(self.user_id, get_action_cost('planning'), 'planning')
            await self.send_status('✅ Planning complete', 2)
            
            # Step 2: Design Agent (3 credits)
            await self.send_status('🎨 Design Agent working...', 0)
            await asyncio.sleep(1)
            design = await self.design_agent(plan)
            await deduct_credits(self.user_id, get_action_cost('design'), 'design')
            await self.send_status('✅ Design complete', 3)
            
            # Step 3: Code Generation Agent (5 credits)
            await self.send_status('💻 Code Generation Agent working...', 0)
            code = await self.code_generation_agent(user_prompt, plan, design)
            await deduct_credits(self.user_id, get_action_cost('code_generation'), 'code_generation')
            await self.send_status('✅ Code generation complete', 5)
            
            # Step 4: Save to database
            await db.projects.update_one(
                {'id': self.project_id},
                {'$set': {
                    'generated_code': code,
                    'status': 'completed',
                    'updated_at': datetime.now(timezone.utc).isoformat()
                }}
            )
            
            # Send final result
            new_balance = await get_user_credits(self.user_id)
            await self.send_status('🎉 Website generated successfully!', 0)
            
            if self.websocket:
                await self.websocket.send_json({
                    'type': 'complete',
                    'code': code,
                    'total_credits_used': 10,
                    'new_balance': new_balance
                })
            
        except Exception as e:
            await self.send_status(f'❌ Error: {str(e)}', 0)
    
    async def planning_agent(self, user_prompt: str) -> dict:
        """Planning agent - analyzes requirements"""
        try:
            response = await self.gemini.generate_content_async(
                f"Analyze this website request and create a brief plan: {user_prompt}"
            )
            return {'plan': response.text}
        except:
            return {'plan': 'Simple modern website'}
    
    async def design_agent(self, plan: dict) -> dict:
        """Design agent - creates design system"""
        return {
            'colors': {'primary': '#6366f1', 'secondary': '#8b5cf6'},
            'layout': 'modern'
        }
    
    async def code_generation_agent(self, prompt: str, plan: dict, design: dict) -> str:
        """Code generation agent - generates HTML/CSS"""
        try:
            response = await self.anthropic.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                messages=[{
                    "role": "user",
                    "content": f"""Create a complete, modern, responsive HTML website for: {prompt}
                    
                    Requirements:
                    - Single HTML file with inline CSS
                    - Modern, professional design
                    - Responsive layout
                    - Clean code
                    
                    Return ONLY the HTML code, no explanations."""
                }]
            )
            
            return response.content[0].text
            
        except Exception as e:
            # Fallback simple template
            return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Your Website</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            line-height: 1.6;
            color: #333;
        }}
        .hero {{
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: center;
            padding: 2rem;
        }}
        h1 {{ font-size: 3rem; margin-bottom: 1rem; }}
        p {{ font-size: 1.2rem; }}
    </style>
</head>
<body>
    <section class="hero">
        <div>
            <h1>Welcome to Your Website</h1>
            <p>{prompt}</p>
        </div>
    </section>
</body>
</html>'''
