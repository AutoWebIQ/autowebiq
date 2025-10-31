# Template and Component System for AutoWebIQ
# Manages pre-built templates, components, and AI customization

import json
from typing import Dict, List, Optional
from datetime import datetime, timezone
import re

class TemplateLibrary:
    """Manages the template library with selection and customization"""
    
    def __init__(self, db):
        self.db = db
        self.templates_collection = db.templates
        self.components_collection = db.components
        
    async def initialize_library(self):
        """Initialize template and component library in database"""
        # Create indexes
        await self.templates_collection.create_index("template_id", unique=True)
        await self.templates_collection.create_index("category")
        await self.templates_collection.create_index("tags")
        await self.components_collection.create_index("component_id", unique=True)
        await self.components_collection.create_index("category")
        
        print("✅ Template library initialized")
    
    async def select_template(self, user_prompt: str, project_type: str = None) -> Dict:
        """Select best matching template based on user prompt"""
        
        # Extract features from prompt
        features = self._extract_features(user_prompt.lower())
        
        # Build query
        query = {}
        if project_type:
            query["category"] = project_type
        
        # Get all templates
        templates = await self.templates_collection.find(query).to_list(length=None)
        
        if not templates:
            return None
        
        # Score each template
        scored_templates = []
        for template in templates:
            score = self._calculate_match_score(template, features, user_prompt)
            scored_templates.append((template, score))
        
        # Return best match
        best_template = max(scored_templates, key=lambda x: x[1])[0]
        
        print(f"✅ Selected template: {best_template['template_id']} (score: {max(scored_templates, key=lambda x: x[1])[1]})")
        
        return best_template
    
    def _extract_features(self, prompt: str) -> Dict:
        """Extract features from user prompt"""
        features = {
            "style": [],
            "industry": [],
            "features": [],
            "keywords": []
        }
        
        # Style keywords
        styles = {
            "luxury": ["luxury", "premium", "elegant", "sophisticated", "high-end"],
            "modern": ["modern", "contemporary", "sleek", "minimal", "clean"],
            "creative": ["creative", "artistic", "unique", "bold", "innovative"],
            "professional": ["professional", "corporate", "business", "formal"],
            "playful": ["playful", "fun", "colorful", "vibrant", "energetic"]
        }
        
        # Industry keywords
        industries = {
            "ecommerce": ["ecommerce", "e-commerce", "store", "shop", "product", "retail", "marketplace"],
            "saas": ["saas", "software", "platform", "tool", "app", "service", "b2b"],
            "portfolio": ["portfolio", "showcase", "gallery", "work", "designer", "photographer"],
            "blog": ["blog", "article", "news", "magazine", "content"],
            "restaurant": ["restaurant", "cafe", "food", "dining", "menu"],
            "agency": ["agency", "studio", "consultant", "marketing", "digital"],
            "landing": ["landing", "launch", "campaign", "lead", "conversion"]
        }
        
        # Feature keywords
        feature_keywords = {
            "product_showcase": ["product", "catalog", "showcase", "items"],
            "testimonials": ["testimonial", "review", "feedback", "customer"],
            "pricing": ["pricing", "plan", "package", "subscription"],
            "contact_form": ["contact", "form", "inquiry", "get in touch"],
            "blog": ["blog", "article", "post"],
            "gallery": ["gallery", "photo", "image", "portfolio"],
            "video": ["video", "media", "youtube"],
            "team": ["team", "about", "people", "staff"]
        }
        
        # Extract styles
        for style_name, keywords in styles.items():
            if any(keyword in prompt for keyword in keywords):
                features["style"].append(style_name)
        
        # Extract industry
        for industry_name, keywords in industries.items():
            if any(keyword in prompt for keyword in keywords):
                features["industry"].append(industry_name)
        
        # Extract features
        for feature_name, keywords in feature_keywords.items():
            if any(keyword in prompt for keyword in keywords):
                features["features"].append(feature_name)
        
        # Extract keywords (all words longer than 3 chars)
        words = re.findall(r'\b\w{4,}\b', prompt)
        features["keywords"] = list(set(words))[:10]  # Top 10 unique keywords
        
        return features
    
    def _calculate_match_score(self, template: Dict, features: Dict, prompt: str) -> int:
        """Calculate match score for template"""
        score = 0
        
        # Category match (50 points)
        if features["industry"] and template["category"] in features["industry"]:
            score += 50
        
        # Style match (30 points)
        if features["style"]:
            template_style = template.get("style", "")
            if any(style in template_style for style in features["style"]):
                score += 30
        
        # Tag match (20 points)
        template_tags = set(template.get("tags", []))
        feature_keywords = set(features["keywords"])
        matching_tags = len(template_tags.intersection(feature_keywords))
        score += min(matching_tags * 5, 20)
        
        # Feature match (bonus 10 points per feature)
        template_features = set(template.get("features", []))
        feature_set = set(features["features"])
        matching_features = len(template_features.intersection(feature_set))
        score += matching_features * 10
        
        # Popularity bonus (max 10 points)
        use_count = template.get("use_count", 0)
        score += min(use_count / 100, 10)
        
        return score
    
    async def get_components(self, component_ids: List[str]) -> List[Dict]:
        """Get components by IDs"""
        query = {"component_id": {"$in": component_ids}}
        components = await self.components_collection.find(query).to_list(length=None)
        return components
    
    async def get_components_by_category(self, category: str) -> List[Dict]:
        """Get all components in a category"""
        components = await self.components_collection.find({"category": category}).to_list(length=None)
        return components
    
    async def increment_template_usage(self, template_id: str):
        """Increment template usage count"""
        await self.templates_collection.update_one(
            {"template_id": template_id},
            {"$inc": {"use_count": 1}}
        )


class TemplateCustomizer:
    """Handles AI-powered customization of templates"""
    
    def __init__(self, openai_client):
        self.client = openai_client
    
    async def customize_template(self, template: Dict, user_prompt: str, images: List[Dict] = []) -> str:
        """Customize template with user content"""
        
        # Get customization zones from template
        zones = template.get("customization_zones", [])
        
        # Generate content for each zone
        customizations = {}
        for zone in zones:
            if zone.get("ai_customizable"):
                content = await self._generate_zone_content(
                    zone_id=zone["zone_id"],
                    zone_type=zone.get("type", "text"),
                    user_prompt=user_prompt,
                    editable_fields=zone.get("editable", [])
                )
                customizations[zone["zone_id"]] = content
        
        # Get base HTML from template
        html = template.get("html", "")
        
        # Replace placeholders with customized content
        for zone_id, content in customizations.items():
            for field, value in content.items():
                placeholder = f"{{{{ {zone_id}.{field} }}}}"
                html = html.replace(placeholder, str(value))
        
        # Replace images
        if images:
            for idx, img in enumerate(images):
                placeholder = f"{{{{ image_{idx + 1} }}}}"
                html = html.replace(placeholder, img.get("url", ""))
        
        # Replace colors from template color scheme
        color_scheme = template.get("color_scheme", {})
        for color_name, color_value in color_scheme.items():
            placeholder = f"{{{{ color.{color_name} }}}}"
            html = html.replace(placeholder, color_value)
        
        return html
    
    async def _generate_zone_content(self, zone_id: str, zone_type: str, user_prompt: str, editable_fields: List[str]) -> Dict:
        """Generate content for a specific customization zone"""
        
        system_prompt = f"""You are a professional copywriter and content strategist.
Generate compelling, conversion-optimized content for a website {zone_id} section.

Based on the user's request, create content that:
- Matches the tone and style of the project
- Is engaging and action-oriented
- Uses persuasive language
- Is concise and impactful
- Follows best practices for web copy

Return ONLY a JSON object with the requested fields. No markdown, no explanations."""

        user_message = f"""User Request: {user_prompt}

Generate content for the {zone_id} section with these fields:
{', '.join(editable_fields)}

Return format:
{{
  {', '.join([f'"{field}": "content here"' for field in editable_fields])}
}}"""

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",  # Faster and cheaper for content generation
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.8,
                max_tokens=500
            )
            
            content_text = response.choices[0].message.content
            
            # Parse JSON
            json_match = re.search(r'\{.*\}', content_text, re.DOTALL)
            if json_match:
                content = json.loads(json_match.group())
                return content
            else:
                # Fallback
                return {field: f"Generated content for {field}" for field in editable_fields}
        
        except Exception as e:
            print(f"Content generation error for {zone_id}: {str(e)}")
            # Return fallback content
            return {field: f"Content for {field}" for field in editable_fields}
    
    async def generate_color_scheme(self, user_prompt: str, style: str = "modern") -> Dict:
        """Generate color scheme based on prompt"""
        
        system_prompt = """You are a professional UI/UX designer specializing in color theory.
Generate a cohesive, accessible color palette that matches the project's style and industry.

Return ONLY a JSON object with hex color codes. No markdown, no explanations."""

        user_message = f"""Generate a color palette for: {user_prompt}
Style: {style}

Requirements:
- Colors should be harmonious and professional
- Ensure good contrast for accessibility (WCAG AA)
- Primary and secondary colors should work well together
- Accent color should stand out but complement the palette

Return format:
{{
  "primary": "#hexcode",
  "secondary": "#hexcode",
  "accent": "#hexcode",
  "background": "#hexcode",
  "text": "#hexcode"
}}"""

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.9,  # More creative for colors
                max_tokens=200
            )
            
            color_text = response.choices[0].message.content
            
            # Parse JSON
            json_match = re.search(r'\{.*\}', color_text, re.DOTALL)
            if json_match:
                colors = json.loads(json_match.group())
                return colors
            else:
                # Fallback colors
                return {
                    "primary": "#6366f1",
                    "secondary": "#8b5cf6",
                    "accent": "#ec4899",
                    "background": "#ffffff",
                    "text": "#1f2937"
                }
        
        except Exception as e:
            print(f"Color generation error: {str(e)}")
            return {
                "primary": "#6366f1",
                "secondary": "#8b5cf6",
                "accent": "#ec4899",
                "background": "#ffffff",
                "text": "#1f2937"
            }
