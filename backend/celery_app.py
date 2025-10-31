# Celery Application Configuration
# Task Queue for Async Website Generation

from celery import Celery
import os

# Redis Configuration
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

# Create Celery app
celery_app = Celery(
    'autowebiq',
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=['celery_tasks']  # Import tasks module
)

# Celery Configuration
celery_app.conf.update(
    # Task Configuration
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Task Routing
    task_routes={
        'celery_tasks.build_website_task': {'queue': 'builds'},
        'celery_tasks.generate_images_task': {'queue': 'images'},
    },
    
    # Task Execution
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_time_limit=300,  # 5 minutes max
    task_soft_time_limit=240,  # 4 minutes soft limit
    
    # Result Backend
    result_expires=3600,  # Results expire after 1 hour
    result_extended=True,
    
    # Worker Configuration
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
)

# Task Priority (0-10, higher = more priority)
celery_app.conf.task_default_priority = 5
celery_app.conf.broker_transport_options = {
    'priority_steps': [0, 3, 6, 9],
}

if __name__ == '__main__':
    celery_app.start()
