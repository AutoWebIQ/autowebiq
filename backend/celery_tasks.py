# Celery Tasks - Async Website Generation
# Handles long-running builds in background

from celery_app import celery_app
from celery import Task
from celery.signals import task_prerun, task_postrun, task_failure
import asyncio
from typing import Dict, List
import traceback
from datetime import datetime, timezone
from websocket_manager import ws_manager

# Task state tracking
@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, **kwds):
    """Called before task starts"""
    print(f"🚀 Task {task.name} [{task_id}] starting...")


@task_postrun.connect
def task_postrun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, retval=None, **kwds):
    """Called after task completes"""
    print(f"✅ Task {task.name} [{task_id}] completed")


@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, args=None, kwargs=None, traceback=None, einfo=None, **kwds):
    """Called when task fails"""
    print(f"❌ Task {sender.name} [{task_id}] failed: {exception}")


class AsyncTask(Task):
    """Base task that handles async functions"""
    
    def __call__(self, *args, **kwargs):
        """Execute async function in sync context"""
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.run_async(*args, **kwargs))
    
    async def run_async(self, *args, **kwargs):
        """Override this method in subclasses"""
        raise NotImplementedError()


@celery_app.task(
    bind=True,
    name='celery_tasks.build_website_task',
    max_retries=0,
)
def build_website_task(
    self,
    user_prompt: str,
    project_id: str,
    user_id: str,
    uploaded_images: List[str] = []
) -> Dict:
    """
    Async website generation task
    
    Args:
        user_prompt: User's website description
        project_id: Project ID
        user_id: User ID
        uploaded_images: List of uploaded image URLs
    
    Returns:
        Dict with status, generated_code, build_time, etc.
    """
    
    # Run async code
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(
        _build_website_async(self, user_prompt, project_id, user_id, uploaded_images)
    )


async def _build_website_async(task_self, user_prompt, project_id, user_id, uploaded_images):
    """Internal async function for website building"""
    try:
        print(f"🏗️  Building website for project {project_id}...")
        start_time = datetime.now(timezone.utc)
        
        # Update task state
        task_task_self.update_state(
            state='PROGRESS',
            meta={'stage': 'initializing', 'progress': 0}
        )
            
            # Import here to avoid circular dependencies
            from template_orchestrator import TemplateBasedOrchestrator
            from database import mongo_db
            import os
            
            # Initialize orchestrator
            openai_key = os.environ.get('OPENAI_API_KEY')
            anthropic_key = os.environ.get('ANTHROPIC_API_KEY')
            gemini_key = os.environ.get('GEMINI_API_KEY')
            
            orchestrator = TemplateBasedOrchestrator(
                openai_key=openai_key,
                anthropic_key=anthropic_key,
                gemini_key=gemini_key,
                db=mongo_db
            )
            
            # Set up progress callback with WebSocket updates
            async def progress_callback(stage: str, progress: int, message: str):
                task_self.update_state(
                    state='PROGRESS',
                    meta={
                        'stage': stage,
                        'progress': progress,
                        'message': message
                    }
                )
                
                # Send WebSocket update
                await ws_manager.send_agent_message(
                    project_id=project_id,
                    agent_type=stage,
                    message=message,
                    status='working',
                    progress=progress
                )
                
                print(f"📊 [{progress}%] {stage}: {message}")
            
            # Generate website
            task_self.update_state(
                state='PROGRESS',
                meta={'stage': 'building', 'progress': 10}
            )
            
            result = await orchestrator.build_website(
                user_prompt=user_prompt,
                project_id=project_id,
                uploaded_images=uploaded_images
            )
            
            # Calculate build time
            end_time = datetime.now(timezone.utc)
            build_time = (end_time - start_time).total_seconds()
            
            # Update result
            result['build_time'] = build_time
            result['completed_at'] = end_time.isoformat()
            
            # Send WebSocket completion notification
            await ws_manager.send_build_complete(project_id, result)
            
            print(f"✅ Website built successfully in {build_time:.1f}s")
            
            # Update task state
            task_self.update_state(
                state='SUCCESS',
                meta={
                    'stage': 'completed',
                    'progress': 100,
                    'build_time': build_time
                }
            )
            
            return result
            
        except Exception as e:
            error_msg = str(e)
            error_trace = traceback.format_exc()
            
            print(f"❌ Build failed: {error_msg}")
            print(error_trace)
            
            # Send WebSocket error notification
            await ws_manager.send_build_error(project_id, error_msg)
            
            # Update task state
            task_self.update_state(
                state='FAILURE',
                meta={
                    'stage': 'failed',
                    'error': error_msg,
                    'traceback': error_trace
                }
            )
            
            return {
                'status': 'failed',
                'error': error_msg,
                'traceback': error_trace
            }


# Register the task
build_website_task = celery_app.task(
    bind=True,
    base=BuildWebsiteTask,
    name='celery_tasks.build_website_task',
    max_retries=0,
)(BuildWebsiteTask())


class GenerateImagesTask(AsyncTask):
    """Async image generation task"""
    
    async def run_async(
        self,
        image_requirements: List[Dict],
        project_id: str
    ) -> Dict:
        """
        Async image generation task
        
        Args:
            image_requirements: List of image specs
            project_id: Project ID
        
        Returns:
            Dict with status and generated images
        """
        
        try:
            print(f"🎨 Generating images for project {project_id}...")
            
            # Import here
            from agents_v2 import ImprovedImageAgent
            from openai import AsyncOpenAI
            import os
            
            # Initialize image agent
            openai_key = os.environ.get('OPENAI_API_KEY')
            client = AsyncOpenAI(api_key=openai_key)
            image_agent = ImprovedImageAgent(client)
            
            # Update state
            task_self.update_state(
                state='PROGRESS',
                meta={'stage': 'generating_images', 'progress': 50}
            )
            
            # Generate images
            plan = {
                'image_requirements': image_requirements,
                'project_id': project_id
            }
            
            images = await image_agent.think(plan, {})
            
            print(f"✅ Generated {len(images)} images")
            
            return {
                'status': 'success',
                'images': images,
                'count': len(images)
            }
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Image generation failed: {error_msg}")
            
            return {
                'status': 'failed',
                'error': error_msg
            }


# Register the task
generate_images_task = celery_app.task(
    bind=True,
    base=GenerateImagesTask,
    name='celery_tasks.generate_images_task',
    max_retries=2,
)(GenerateImagesTask())


# Health check task
@celery_app.task(name='celery_tasks.health_check')
def health_check():
    """Simple health check task"""
    return {'status': 'healthy', 'timestamp': datetime.now(timezone.utc).isoformat()}
