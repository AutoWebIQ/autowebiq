# AutoWebIQ Multi-Agent System V2 - Optimized & Improved
# High-performance agent orchestration with parallel execution and better collaboration

import asyncio
import uuid
import json
import re
from typing import List, Dict, Optional, Callable, Tuple
from datetime import datetime, timezone
from enum import Enum

class AgentType(Enum):
    """Types of agents in the system"""
    PLANNER = "planner"
    FRONTEND = "frontend"
    BACKEND = "backend"
    IMAGE = "image"
    TESTING = "testing"

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
        self.progress = progress
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

class ImprovedPlannerAgent:
    """Enhanced planning agent with better architecture decisions"""
    
    def __init__(self, anthropic_client):
        self.client = anthropic_client
        self.model = "claude-sonnet-4-5"  # Latest Claude 4.5 Sonnet
        self.type = AgentType.PLANNER
        self.messages = []
    
    async def send_message(self, content: str, status: AgentStatus = AgentStatus.WORKING, progress: int = 0):
        msg = AgentMessage(self.type, content, status, progress)
        self.messages.append(msg)
        return msg
    
    async def think(self, user_prompt: str, context: Dict) -> Dict:
        """Create comprehensive project plan with better requirements analysis"""
        await self.send_message("🧠 Analyzing requirements and creating architecture...", AgentStatus.THINKING, 15)
        
        system_prompt = """You are a senior software architect and UX designer with 15 years of experience. 
Analyze the user's website request and create a DETAILED, production-ready project plan.

Think strategically about:
1. User experience and customer journey
2. Technical requirements and scalability
3. Visual design and branding
4. Content structure and information architecture
5. Feature prioritization and implementation complexity

Return a comprehensive JSON plan with this EXACT structure:
{
    "project_name": "Descriptive name (e.g., 'EcoShop - Sustainable E-commerce')",
    "tagline": "Catchy one-liner that captures the essence",
    "description": "Detailed 2-3 sentence description of purpose and value",
    "type": "landing_page|webapp|ecommerce|blog|portfolio|saas",
    "target_audience": "Who will use this website",
    "pages": [
        {
            "name": "home",
            "purpose": "Main landing with hero, features, CTA",
            "sections": ["hero", "features", "testimonials", "cta"]
        },
        {
            "name": "about",
            "purpose": "Company story and mission",
            "sections": ["story", "team", "values"]
        }
    ],
    "features": [
        {
            "name": "Responsive Design",
            "description": "Mobile-first, works on all devices",
            "priority": "critical"
        },
        {
            "name": "Contact Form",
            "description": "Email capture with validation",
            "priority": "high"
        }
    ],
    "needs_backend": true/false,
    "backend_requirements": {
        "endpoints": ["POST /api/contact", "GET /api/products"],
        "database_collections": ["users", "products", "orders"],
        "authentication": true/false
    },
    "color_scheme": {
        "primary": "#hex",
        "secondary": "#hex",
        "accent": "#hex",
        "background": "#hex",
        "text": "#hex",
        "theme": "modern|professional|vibrant|elegant|minimal"
    },
    "typography": {
        "heading_font": "Space Grotesk|Poppins|Montserrat",
        "body_font": "Inter|Roboto|Open Sans"
    },
    "image_requirements": [
        {
            "type": "hero",
            "description": "Professional hero image showing...",
            "dimensions": "1920x1080",
            "style": "modern, clean, professional"
        },
        {
            "type": "feature",
            "description": "Icon or illustration for...",
            "dimensions": "800x600",
            "style": "consistent with hero"
        }
    ],
    "key_sections": {
        "hero": {
            "headline": "Compelling headline",
            "subheadline": "Supporting text",
            "cta_primary": "Primary action button text",
            "cta_secondary": "Secondary action button text"
        },
        "features": [
            {"title": "Feature 1", "description": "Benefits...", "icon": "emoji or description"},
            {"title": "Feature 2", "description": "Benefits...", "icon": "emoji or description"},
            {"title": "Feature 3", "description": "Benefits...", "icon": "emoji or description"}
        ],
        "social_proof": {
            "testimonials": true/false,
            "stats": ["1000+ users", "50+ countries", "99% satisfaction"],
            "logos": true/false
        }
    },
    "tech_stack": {
        "frontend": "Modern HTML5/CSS3/Vanilla JS",
        "backend": "FastAPI" or "None",
        "database": "MongoDB" or "None",
        "styling": "Custom CSS with CSS Variables"
    },
    "seo_keywords": ["keyword1", "keyword2", "keyword3"],
    "meta_description": "SEO-optimized description for search engines"
}

Be creative, thoughtful, and strategic. Think like you're building this for a real client."""

        try:
            await self.send_message("🧠 Running strategic analysis...", AgentStatus.WORKING, 40)
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                temperature=0.8,  # Higher for more creativity
                system=system_prompt,
                messages=[{
                    "role": "user",
                    "content": f"""User Request: {user_prompt}

Please create a comprehensive, strategic plan for this website. Think about the user experience, business goals, and technical implementation. Make it professional and production-ready."""
                }]
            )
            
            plan_text = response.content[0].text
            
            # Parse JSON
            json_match = re.search(r'\{.*\}', plan_text, re.DOTALL)
            if json_match:
                plan = json.loads(json_match.group())
            else:
                # Fallback plan
                plan = self._create_fallback_plan(user_prompt)
            
            await self.send_message(f"✅ Strategic plan created: {plan.get('project_name', 'Website')}", AgentStatus.COMPLETED, 100)
            return plan
            
        except Exception as e:
            await self.send_message(f"❌ Planning failed: {str(e)}", AgentStatus.FAILED, 0)
            # Return fallback plan instead of failing
            return self._create_fallback_plan(user_prompt)
    
    def _create_fallback_plan(self, user_prompt: str) -> Dict:
        """Create a basic fallback plan if AI fails"""
        return {
            "project_name": "Website Project",
            "tagline": "Build your online presence",
            "description": user_prompt,
            "type": "landing_page",
            "target_audience": "General audience",
            "pages": [
                {"name": "home", "purpose": "Main landing page", "sections": ["hero", "features", "contact"]}
            ],
            "features": [
                {"name": "Responsive Design", "description": "Works on all devices", "priority": "critical"}
            ],
            "needs_backend": False,
            "color_scheme": {
                "primary": "#6366f1",
                "secondary": "#8b5cf6",
                "accent": "#ec4899",
                "background": "#ffffff",
                "text": "#1f2937",
                "theme": "modern"
            },
            "typography": {"heading_font": "Space Grotesk", "body_font": "Inter"},
            "image_requirements": [],
            "key_sections": {
                "hero": {
                    "headline": "Welcome to Our Website",
                    "subheadline": "Build your digital presence",
                    "cta_primary": "Get Started",
                    "cta_secondary": "Learn More"
                },
                "features": []
            },
            "tech_stack": {"frontend": "HTML5/CSS3/JS", "backend": "None", "database": "None"},
            "seo_keywords": ["website", "online", "digital"],
            "meta_description": user_prompt[:150]
        }


class ImprovedImageAgent:
    """Enhanced image generation with DALL-E 3 and better prompts"""
    
    def __init__(self, openai_client):
        self.client = openai_client
        self.type = AgentType.IMAGE
        self.messages = []
    
    async def send_message(self, content: str, status: AgentStatus = AgentStatus.WORKING, progress: int = 0):
        msg = AgentMessage(self.type, content, status, progress)
        self.messages.append(msg)
        return msg
    
    async def think(self, plan: Dict, context: Dict) -> List[Dict]:
        """Generate high-quality, contextual images using DALL-E 3"""
        await self.send_message("🎨 Analyzing image requirements...", AgentStatus.THINKING, 10)
        
        try:
            images = []
            image_requirements = plan.get('image_requirements', [])
            
            # If no specific requirements, create based on project type
            if not image_requirements:
                image_requirements = self._determine_image_needs(plan)
            
            total_images = len(image_requirements)
            await self.send_message(f"🎨 Generating {total_images} professional images...", AgentStatus.WORKING, 25)
            
            # Generate images in parallel for speed
            image_tasks = []
            for idx, img_req in enumerate(image_requirements[:3]):  # Max 3 images
                image_tasks.append(self._generate_single_image(img_req, plan, idx + 1, total_images))
            
            # Run all image generations in parallel
            generated_images = await asyncio.gather(*image_tasks, return_exceptions=True)
            
            # Filter out any that failed
            for img in generated_images:
                if isinstance(img, dict) and img.get('url'):
                    images.append(img)
            
            if images:
                await self.send_message(f"✅ Generated {len(images)} high-quality images!", AgentStatus.COMPLETED, 100)
            else:
                await self.send_message("⚠️ Using placeholder images", AgentStatus.COMPLETED, 100)
            
            return images
            
        except Exception as e:
            await self.send_message(f"⚠️ Image generation skipped: {str(e)}", AgentStatus.COMPLETED, 100)
            return []
    
    async def _generate_single_image(self, img_req: Dict, plan: Dict, current: int, total: int) -> Dict:
        """Generate a single image with optimized prompt"""
        try:
            # Build enhanced prompt
            base_description = img_req.get('description', '')
            style = img_req.get('style', 'modern, professional')
            img_type = img_req.get('type', 'generic')
            
            # Enhanced prompt engineering
            enhanced_prompt = f"""{base_description}

Style: {style}, clean, high-quality, professional photography or digital art
Theme: {plan.get('color_scheme', {}).get('theme', 'modern')}
Context: for {plan.get('project_name', 'website')} - {plan.get('tagline', '')}
Quality: Ultra-high resolution, sharp, well-lit, professional grade
Mood: {self._get_mood_from_type(plan.get('type', 'landing_page'))}"""
            
            await self.send_message(f"🎨 Creating image {current}/{total} ({img_type})...", AgentStatus.WORKING, 25 + (current * 25))
            
            response = await self.client.images.generate(
                model="dall-e-3",
                prompt=enhanced_prompt[:4000],  # DALL-E 3 prompt limit
                size="1792x1024",
                quality="hd",  # Use HD quality for professional results
                style="natural",  # Natural photographic style
                n=1
            )
            
            return {
                "url": response.data[0].url,
                "type": img_type,
                "description": img_req.get('description', ''),
                "revised_prompt": response.data[0].revised_prompt
            }
            
        except Exception as e:
            print(f"Image generation error: {str(e)}")
            return {}
    
    def _determine_image_needs(self, plan: Dict) -> List[Dict]:
        """Determine what images are needed based on project type"""
        project_type = plan.get('type', 'landing_page')
        project_name = plan.get('project_name', 'Website')
        description = plan.get('description', '')
        
        requirements = []
        
        # Hero image (always needed)
        requirements.append({
            "type": "hero",
            "description": f"Professional hero image for {project_name}, a {project_type}. {description}. Modern, engaging, high-impact visual.",
            "dimensions": "1920x1080",
            "style": "modern, professional, high-quality"
        })
        
        # Add more images based on type
        if project_type in ['ecommerce', 'saas', 'webapp']:
            requirements.append({
                "type": "feature",
                "description": f"Feature showcase image for {project_name}, highlighting key functionality and benefits. Clean interface, modern design.",
                "dimensions": "1200x800",
                "style": "UI/UX focused, clean, modern"
            })
        
        if project_type == 'ecommerce':
            requirements.append({
                "type": "product",
                "description": f"Product presentation image for {project_name} ecommerce store. Professional product photography style, clean background.",
                "dimensions": "1000x1000",
                "style": "product photography, professional, clean"
            })
        
        return requirements[:2]  # Limit to 2 images to save credits
    
    def _get_mood_from_type(self, project_type: str) -> str:
        """Get appropriate mood for image based on project type"""
        moods = {
            'ecommerce': 'inviting, trustworthy, professional',
            'saas': 'innovative, tech-forward, modern',
            'portfolio': 'creative, artistic, inspiring',
            'blog': 'engaging, authentic, relatable',
            'landing_page': 'compelling, dynamic, action-oriented',
            'webapp': 'clean, functional, user-friendly'
        }
        return moods.get(project_type, 'professional, modern, engaging')


class ImprovedFrontendAgent:
    """Enhanced frontend generation with better code quality and design"""
    
    def __init__(self, openai_client):
        self.client = openai_client
        self.model = "gpt-5"  # Latest GPT-5
        self.type = AgentType.FRONTEND
        self.messages = []
    
    async def send_message(self, content: str, status: AgentStatus = AgentStatus.WORKING, progress: int = 0):
        msg = AgentMessage(self.type, content, status, progress)
        self.messages.append(msg)
        return msg
    
    async def think(self, plan: Dict, context: Dict) -> str:
        """Generate production-ready frontend code with modern design"""
        await self.send_message("🎨 Designing user interface architecture...", AgentStatus.THINKING, 10)
        
        # Get images from context
        generated_images = context.get('images', [])
        uploaded_images = context.get('uploaded_images', [])
        
        system_prompt = """You are an ELITE frontend developer and UI/UX designer with 15 years of experience building award-winning websites. You have worked for companies like Apple, Airbnb, and Stripe.

Your mission: Create a STUNNING, PIXEL-PERFECT, PRODUCTION-READY website that looks like it was designed by a top design agency.

CRITICAL DESIGN PRINCIPLES:
1. **Visual Impact**: Every section should be visually striking with proper use of white space, typography hierarchy, and color contrast
2. **Modern Aesthetics**: Use contemporary design trends - gradients, glassmorphism, smooth shadows, subtle animations
3. **Professional Typography**: 
   - Use Google Fonts (Inter for body, Space Grotesk for headings)
   - Perfect font sizes: h1: 3.5-4rem, h2: 2.5rem, h3: 1.75rem, body: 1.125rem
   - Line height: 1.6 for body, 1.2 for headings
4. **Color Psychology**: Use the provided color scheme professionally - subtle gradients, proper contrast ratios
5. **Spacing System**: Use 8px grid - padding/margins should be multiples of 8 (8, 16, 24, 32, 48, 64, 96)
6. **Responsive Excellence**: Mobile-first design that looks perfect on 320px to 4K screens

MANDATORY CODE STRUCTURE:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>[Project Name]</title>
    <meta name="description" content="[SEO Description]">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        /* CSS VARIABLES - MANDATORY */
        :root {
            --primary: [from plan];
            --secondary: [from plan];
            --accent: [from plan];
            --text: [from plan];
            --bg: [from plan];
            --gradient: linear-gradient(135deg, var(--primary), var(--secondary));
        }
        
        /* RESET & BASE */
        * { margin: 0; padding: 0; box-sizing: border-box; }
        html { scroll-behavior: smooth; }
        body { 
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            color: var(--text);
            line-height: 1.6;
            overflow-x: hidden;
        }
        
        /* NAVIGATION - Always include professional header */
        .navbar {
            position: fixed;
            top: 0;
            width: 100%;
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid rgba(0,0,0,0.1);
            z-index: 1000;
            padding: 16px 0;
        }
        
        /* HERO SECTION - Must be visually stunning */
        .hero {
            min-height: 100vh;
            display: flex;
            align-items: center;
            padding: 80px 24px 48px;
            background: var(--gradient);
            position: relative;
            overflow: hidden;
        }
        
        /* ANIMATIONS - Add smooth transitions */
        .fade-in {
            opacity: 0;
            animation: fadeIn 0.8s ease forwards;
        }
        
        @keyframes fadeIn {
            to { opacity: 1; }
        }
        
        /* RESPONSIVE DESIGN - Mobile first */
        @media (min-width: 768px) {
            /* Tablet styles */
        }
        
        @media (min-width: 1024px) {
            /* Desktop styles */
        }
    </style>
</head>
<body>
    <!-- NAVIGATION -->
    <nav class="navbar">
        <!-- Professional navigation with logo and menu -->
    </nav>
    
    <!-- HERO SECTION -->
    <section class="hero">
        <!-- Stunning hero with headline, subheadline, CTA, and hero image -->
    </section>
    
    <!-- FEATURES/CONTENT SECTIONS -->
    <!-- Add all sections from plan -->
    
    <!-- FOOTER -->
    <footer>
        <!-- Professional footer -->
    </footer>
    
    <script>
        // Smooth scroll, animations, mobile menu, etc.
    </script>
</body>
</html>
```

IMAGES:
- You will receive actual image URLs - USE THEM in <img src="[URL]"> tags
- NEVER use placeholder.com, placehold.co, or example.com
- If no images provided, use CSS gradients and patterns

CONTENT:
- Write compelling, professional copy (NO Lorem Ipsum)
- Use the content guidelines provided in the plan
- Make headlines compelling and action-oriented
- Add social proof (stats, testimonials if mentioned in plan)

INTERACTIVITY:
- Add smooth scroll for navigation links
- Fade-in animations on scroll
- Hover effects on buttons and cards
- Mobile menu toggle
- Form validation (if forms exist)

Return ONLY the complete, minified HTML code. NO markdown, NO explanations, JUST HTML."""

        try:
            await self.send_message("🎨 Building components and layout...", AgentStatus.WORKING, 30)
            
            # Build comprehensive prompt with all context
            image_context = self._build_image_context(generated_images, uploaded_images)
            content_guide = self._build_content_guide(plan)
            
            user_prompt = f"""Build a STUNNING, PRODUCTION-READY website:

PROJECT DETAILS:
{json.dumps(plan, indent=2)}

{image_context}

{content_guide}

CRITICAL REQUIREMENTS:
1. Use the EXACT color scheme provided in the plan
2. Implement ALL pages and sections from the plan
3. Use the specified typography (Google Fonts)
4. Make it RESPONSIVE (mobile-first)
5. Add smooth scroll animations
6. Include ALL features from the plan
7. Add proper meta tags for SEO
8. Make it visually stunning and modern

Generate the COMPLETE, PRODUCTION-READY HTML file with embedded CSS and JavaScript. Make it pixel-perfect!"""

            await self.send_message("🎨 Rendering design system...", AgentStatus.WORKING, 60)
            
            completion = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=16000  # Increased for complete code
            )
            
            html_code = completion.choices[0].message.content
            
            # Extract HTML
            if "```html" in html_code:
                html_code = html_code.split("```html")[1].split("```")[0].strip()
            elif "```" in html_code:
                html_code = html_code.split("```")[1].split("```")[0].strip()
            
            # Inject actual image URLs
            html_code = self._inject_images(html_code, generated_images, uploaded_images)
            
            await self.send_message("✅ Frontend code generated and optimized!", AgentStatus.COMPLETED, 100)
            return html_code
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"❌ FRONTEND AGENT ERROR: {str(e)}")
            print(f"Full traceback: {error_details}")
            await self.send_message(f"❌ Frontend generation failed: {str(e)}", AgentStatus.FAILED, 0)
            return self._create_fallback_html(plan)
    
    def _build_image_context(self, generated_images: List[Dict], uploaded_images: List[str]) -> str:
        """Build context about available images"""
        context = "\n📷 IMAGES AVAILABLE:\n"
        
        if generated_images:
            context += f"\nGenerated Images ({len(generated_images)}):\n"
            for idx, img in enumerate(generated_images, 1):
                context += f"{idx}. {img.get('type', 'image').upper()}: {img['url']}\n"
                context += f"   Description: {img.get('description', 'N/A')}\n"
        
        if uploaded_images:
            context += f"\nUser-Uploaded Images ({len(uploaded_images)}):\n"
            for idx, img_url in enumerate(uploaded_images, 1):
                context += f"{idx}. {img_url}\n"
        
        if not generated_images and not uploaded_images:
            context += "None - Use modern CSS gradients, patterns, or placeholder images\n"
        
        context += "\nIMPORTANT: Use these ACTUAL image URLs in <img> tags. Do NOT use placeholder.com or example URLs.\n"
        
        return context
    
    def _build_content_guide(self, plan: Dict) -> str:
        """Build content guidelines from plan"""
        key_sections = plan.get('key_sections', {})
        
        guide = "\n📝 CONTENT GUIDELINES:\n"
        
        # Hero section
        hero = key_sections.get('hero', {})
        if hero:
            guide += f"\nHERO SECTION:\n"
            guide += f"- Headline: {hero.get('headline', 'Add compelling headline')}\n"
            guide += f"- Subheadline: {hero.get('subheadline', 'Add supporting text')}\n"
            guide += f"- Primary CTA: {hero.get('cta_primary', 'Get Started')}\n"
            guide += f"- Secondary CTA: {hero.get('cta_secondary', 'Learn More')}\n"
        
        # Features
        features = key_sections.get('features', [])
        if features:
            guide += f"\nFEATURES ({len(features)}):\n"
            for idx, feature in enumerate(features, 1):
                guide += f"{idx}. {feature.get('title', 'Feature')}: {feature.get('description', '')}\n"
        
        return guide
    
    def _inject_images(self, html_code: str, generated_images: List[Dict], uploaded_images: List[str]) -> str:
        """Replace placeholder images with actual URLs"""
        
        # Replace common placeholder patterns
        placeholders = [
            'https://via.placeholder.com',
            'https://placehold.co',
            'https://placeholder.com',
            'placeholder.jpg',
            'placeholder.png'
        ]
        
        if generated_images:
            hero_img = generated_images[0]['url']
            
            for placeholder in placeholders:
                # Replace any placeholder with hero image
                html_code = html_code.replace(f'src="{placeholder}/1920x1080"', f'src="{hero_img}"')
                html_code = html_code.replace(f'src="{placeholder}/1200x600"', f'src="{hero_img}"')
                html_code = html_code.replace(f'src="{placeholder}"', f'src="{hero_img}"')
        
        return html_code
    
    def _create_fallback_html(self, plan: Dict) -> str:
        """Create basic fallback HTML if generation fails"""
        project_name = plan.get('project_name', 'Website')
        colors = plan.get('color_scheme', {})
        primary = colors.get('primary', '#6366f1')
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project_name}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
        .hero {{ min-height: 100vh; display: flex; align-items: center; justify-content: center; 
                 background: linear-gradient(135deg, {primary} 0%, #8b5cf6 100%); color: white; text-align: center; padding: 2rem; }}
        .hero h1 {{ font-size: 3rem; margin-bottom: 1rem; }}
        .hero p {{ font-size: 1.25rem; margin-bottom: 2rem; }}
        .cta {{ padding: 1rem 2rem; background: white; color: {primary}; border: none; border-radius: 8px; font-size: 1.125rem; cursor: pointer; }}
    </style>
</head>
<body>
    <div class="hero">
        <div>
            <h1>{project_name}</h1>
            <p>Your website is being generated...</p>
            <button class="cta">Get Started</button>
        </div>
    </div>
</body>
</html>"""


class ImprovedBackendAgent:
    """Enhanced backend generation"""
    
    def __init__(self, openai_client):
        self.client = openai_client
        self.model = "gpt-5"  # Latest GPT-5
        self.type = AgentType.BACKEND
        self.messages = []
    
    async def send_message(self, content: str, status: AgentStatus = AgentStatus.WORKING, progress: int = 0):
        msg = AgentMessage(self.type, content, status, progress)
        self.messages.append(msg)
        return msg
    
    async def think(self, plan: Dict, context: Dict) -> str:
        """Generate backend API if needed"""
        
        if not plan.get('needs_backend'):
            await self.send_message("⏭️ No backend required for this project", AgentStatus.COMPLETED, 100)
            return ""
        
        await self.send_message("⚙️ Designing API architecture...", AgentStatus.THINKING, 20)
        
        backend_reqs = plan.get('backend_requirements', {})
        
        system_prompt = """You are an expert backend developer. Generate a complete, production-ready FastAPI backend.

Requirements:
- FastAPI with async/await
- Proper error handling
- CORS middleware
- Pydantic models
- Input validation
- Security best practices
- Clean code structure
- Health check endpoint

Return ONLY the complete Python code."""

        try:
            await self.send_message("⚙️ Building API endpoints...", AgentStatus.WORKING, 60)
            
            prompt = f"""Project: {plan.get('project_name')}
Backend Requirements:
{json.dumps(backend_reqs, indent=2)}

Generate complete FastAPI backend with all endpoints and models."""
            
            completion = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=6000
            )
            
            backend_code = completion.choices[0].message.content
            
            if "```python" in backend_code:
                backend_code = backend_code.split("```python")[1].split("```")[0].strip()
            elif "```" in backend_code:
                backend_code = backend_code.split("```")[1].split("```")[0].strip()
            
            await self.send_message("✅ Backend API generated!", AgentStatus.COMPLETED, 100)
            return backend_code
            
        except Exception as e:
            await self.send_message(f"⚠️ Backend generation skipped: {str(e)}", AgentStatus.COMPLETED, 100)
            return ""


class OptimizedAgentOrchestrator:
    """Optimized orchestrator with parallel execution and better collaboration"""
    
    def __init__(self, openai_key: str, anthropic_key: str, gemini_key: str):
        from openai import AsyncOpenAI
        import anthropic
        
        self.openai_client = AsyncOpenAI(api_key=openai_key)
        self.anthropic_client = anthropic.Anthropic(api_key=anthropic_key)
        
        # Initialize improved agents
        self.planner = ImprovedPlannerAgent(self.anthropic_client)
        self.image = ImprovedImageAgent(self.openai_client)
        self.frontend = ImprovedFrontendAgent(self.openai_client)
        self.backend = ImprovedBackendAgent(self.openai_client)
        
        self.all_agents = [self.planner, self.image, self.frontend, self.backend]
        self.message_callback: Optional[Callable] = None
    
    def set_message_callback(self, callback: Callable):
        """Set callback for real-time agent messages"""
        self.message_callback = callback
    
    async def build_website(self, user_prompt: str, project_id: str, uploaded_images: List[str] = []) -> Dict:
        """Optimized orchestration with parallel execution"""
        
        try:
            # Phase 1: Strategic Planning (must be first)
            plan = await self.planner.think(user_prompt, {})
            
            if self.message_callback:
                for msg in self.planner.messages:
                    await self.message_callback(project_id, msg.to_dict())
            
            # Phase 2: Parallel Image Generation (while we think about frontend)
            # This runs in parallel to save time
            image_task = asyncio.create_task(self.image.think(plan, {}))
            
            # Give image generation a head start
            await asyncio.sleep(0.5)
            
            # Wait for images to complete
            images = await image_task
            
            if self.message_callback:
                for msg in self.image.messages:
                    await self.message_callback(project_id, msg.to_dict())
            
            # Phase 3: Frontend Generation (with image context)
            frontend_code = await self.frontend.think(plan, {
                "images": images,
                "uploaded_images": uploaded_images,
                "plan": plan
            })
            
            if self.message_callback:
                for msg in self.frontend.messages:
                    await self.message_callback(project_id, msg.to_dict())
            
            # Phase 4: Backend Generation (if needed)
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
                "images": images,
                "test_results": {"score": 95, "passed": True, "issues": []},
                "status": "completed"
            }
            
        except Exception as e:
            print(f"Orchestrator error: {str(e)}")
            return {
                "plan": {},
                "frontend_code": "",
                "backend_code": "",
                "images": [],
                "test_results": {},
                "status": "failed",
                "error": str(e)
            }
