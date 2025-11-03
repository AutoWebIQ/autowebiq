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
        """Code generation agent - generates INCREDIBLE, FULLY FUNCTIONAL websites"""
        try:
            # SUPERIOR prompt for Claude Sonnet 4
            enhanced_prompt = f"""You are an EXPERT web developer. Create a COMPLETE, PRODUCTION-READY, FULLY FUNCTIONAL website.

USER REQUEST: {prompt}

CRITICAL REQUIREMENTS:
1. **FULLY FUNCTIONAL** - All buttons, forms, navigation MUST work with JavaScript
2. **INCREDIBLE UI/UX** - Modern, beautiful, professional design that looks like a $10,000 website
3. **COMPLETE SECTIONS**:
   - Professional navigation bar with smooth scroll
   - Stunning hero section with CTA buttons
   - Features/Services section (3-6 items)
   - About section
   - Contact form that validates and shows success message
   - Professional footer with social links
4. **WORKING INTERACTIVITY**:
   - Mobile hamburger menu that opens/closes
   - Smooth scroll to sections
   - Form validation with JavaScript
   - Hover effects and animations
   - Contact form submission handling
5. **MODERN DESIGN**:
   - Gradient backgrounds or modern color schemes
   - Box shadows and depth
   - Smooth animations and transitions
   - Professional typography
   - Proper spacing and alignment
6. **HIGH-QUALITY IMAGES**:
   - Use beautiful Unsplash images (https://images.unsplash.com/photo-...)
   - At least 3-5 relevant, high-quality images
   - Proper image optimization
7. **RESPONSIVE**:
   - Perfect on mobile, tablet, desktop
   - Mobile-first approach
8. **PRODUCTION-READY**:
   - Clean, semantic HTML5
   - Modern CSS with flexbox/grid
   - Vanilla JavaScript (no dependencies)
   - Cross-browser compatible
   - SEO-friendly meta tags

DESIGN STYLE: Modern, professional, clean, with smooth animations

OUTPUT: Single HTML file with inline CSS and JavaScript. Make it look INCREDIBLE - like a professional developer spent days building it!

IMPORTANT: 
- Use REAL Unsplash image URLs
- Make EVERY button functional
- Add smooth scrolling
- Include working form validation
- Add mobile menu toggle
- Use modern CSS (gradients, shadows, animations)

CREATE THE WEBSITE NOW:"""

            response = await self.anthropic.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=8000,  # Increased for complete websites
                messages=[{
                    "role": "user",
                    "content": enhanced_prompt
                }]
            )
            
            generated_code = response.content[0].text
            
            # Clean up if Claude adds markdown code blocks
            if '```html' in generated_code:
                generated_code = generated_code.split('```html')[1].split('```')[0].strip()
            elif '```' in generated_code:
                generated_code = generated_code.split('```')[1].split('```')[0].strip()
            
            return generated_code
            
        except Exception as e:
            # Enhanced fallback with working features
            return self._create_fallback_website(prompt)
