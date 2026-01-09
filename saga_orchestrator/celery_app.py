# Note: eventlet monkey patching removed to avoid Flask context warnings
# Use --pool=solo on Windows instead of --pool=eventlet
from celery import Celery
import os

# Redis connection URL (default to localhost)
REDIS_URL = os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/0')

# Create Celery app
celery_app = Celery(
    'saga_orchestrator',
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=['saga_orchestrator.tasks']
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes max per task
    task_soft_time_limit=25 * 60,  # 25 minutes soft limit
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
)

if __name__ == '__main__':
    celery_app.start()