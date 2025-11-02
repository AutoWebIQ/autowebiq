# Multi-Model Router System for AutoWebIQ
# Intelligently routes tasks to the most appropriate AI model
# Claude Sonnet 4 → Frontend/UI, GPT-4o/5 → Backend/API, Gemini → Content

import os
from typing import Literal, Dict, Any
from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage
from emergentintegrations.llm.openai.image_generation import OpenAIImageGeneration

load_dotenv()

TaskType = Literal[
    "frontend",  # UI components, HTML/CSS/JS, design
    "backend",   # API logic, technical architecture
    "content",   # Copywriting, SEO, descriptions
    "image"      # Image generation
]

class ModelRouter:
    """
    Intelligent model router that directs tasks to the most appropriate AI model.
    
    Routing Strategy:
    - Claude Sonnet 4 → Frontend/UI tasks (best for design, components, user experience)
    - GPT-4o/5 → Backend logic (best for technical architecture, APIs)
    - Gemini 2.5 Pro → Content generation (best for copywriting, SEO, descriptions)
    - OpenAI gpt-image-1 → HD image generation
    """
    
    def __init__(self):
        # Get API keys from environment
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        self.gemini_key = os.getenv("GOOGLE_AI_API_KEY")
        
        # Validate API keys
        if not all([self.openai_key, self.anthropic_key, self.gemini_key]):
            raise ValueError("Missing required API keys (OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_AI_API_KEY)")
        
        # Model configurations
        self.model_config = {
            "frontend": {
                "provider": "anthropic",
                "model": "claude-4-sonnet-20250514",  # Latest Claude Sonnet 4
                "reason": "Best for frontend, UI/UX, HTML/CSS/JS generation"
            },
            "backend": {
                "provider": "openai",
                "model": "gpt-4o",  # GPT-4o for backend logic
                "reason": "Best for backend logic, API design, technical architecture"
            },
            "content": {
                "provider": "gemini",
                "model": "gemini-2.5-pro",  # Gemini 2.5 Pro for content
                "reason": "Best for content generation, copywriting, SEO"
            }
        }
        
        # Initialize image generator
        self.image_generator = OpenAIImageGeneration(api_key=self.openai_key)
        
        print(f"✅ Model Router initialized:")
        print(f"   Frontend → Claude Sonnet 4 (claude-4-sonnet-20250514)")
        print(f"   Backend → GPT-4o (gpt-4o)")
        print(f"   Content → Gemini 2.5 Pro (gemini-2.5-pro)")
        print(f"   Images → OpenAI gpt-image-1")
    
    def get_chat_client(self, task_type: TaskType, system_message: str, session_id: str) -> LlmChat:
        """
        Get the appropriate chat client for the task type.
        
        Args:
            task_type: Type of task (frontend, backend, content)
            system_message: System message for the AI
            session_id: Unique session ID for the conversation
        
        Returns:
            LlmChat: Configured chat client for the task
        """
        config = self.model_config[task_type]
        
        # Select API key based on provider
        api_key_map = {
            "openai": self.openai_key,
            "anthropic": self.anthropic_key,
            "gemini": self.gemini_key
        }
        
        api_key = api_key_map[config["provider"]]
        
        # Initialize chat client
        chat = LlmChat(
            api_key=api_key,
            session_id=session_id,
            system_message=system_message
        )
        
        # Configure with the appropriate model
        chat.with_model(config["provider"], config["model"])
        
        print(f"🎯 Routing {task_type} task to {config['provider']} ({config['model']})")
        
        return chat
    
    async def generate_completion(
        self, 
        task_type: TaskType, 
        prompt: str, 
        system_message: str = "You are a helpful AI assistant.",
        session_id: str = "default"
    ) -> str:
        """
        Generate completion for a given task using the appropriate model.
        
        Args:
            task_type: Type of task (frontend, backend, content)
            prompt: User prompt
            system_message: System message for context
            session_id: Session ID for the conversation
        
        Returns:
            str: Generated completion
        """
        chat = self.get_chat_client(task_type, system_message, session_id)
        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        return response
    
    async def generate_image(
        self, 
        prompt: str, 
        number_of_images: int = 1
    ) -> list:
        """
        Generate HD images using OpenAI gpt-image-1.
        
        Args:
            prompt: Image generation prompt
            number_of_images: Number of images to generate (default: 1)
        
        Returns:
            list: List of image bytes
        """
        print(f"🎨 Generating {number_of_images} HD image(s) with gpt-image-1...")
        
        images = await self.image_generator.generate_images(
            prompt=prompt,
            model="gpt-image-1",  # Latest HD image model
            number_of_images=number_of_images
        )
        
        print(f"✅ Generated {len(images)} HD image(s)")
        return images
    
    def get_model_info(self, task_type: TaskType) -> Dict[str, Any]:
        """Get information about which model is used for a task type."""
        return self.model_config.get(task_type, {})
    
    def get_all_models(self) -> Dict[TaskType, Dict[str, Any]]:
        """Get information about all model configurations."""
        return self.model_config


# Singleton instance
_router_instance = None

def get_model_router() -> ModelRouter:
    """Get or create singleton model router instance."""
    global _router_instance
    if _router_instance is None:
        _router_instance = ModelRouter()
    return _router_instance
