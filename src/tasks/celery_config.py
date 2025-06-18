from celery import Celery
from ..config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND, CHECK_INTERVAL

# Celery configuration
celery_app = Celery(
    'padelbot',
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND
)

# Configure Celery logging to avoid duplicates
celery_app.conf.update(
    worker_log_format='[%(asctime)s: %(levelname)s/%(processName)s] %(message)s',
    worker_task_log_format='[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s',
    worker_redirect_stdouts=False,
    worker_redirect_stdouts_level='INFO',
)

# Celery beat schedule configuration
celery_app.conf.beat_schedule = {
    'check-availability': {
        'task': 'src.tasks.check_availability.check_availability',
        'schedule': CHECK_INTERVAL * 60.0,  # Convert minutes to seconds
    },
    'check-subscriptions': {
        'task': 'src.tasks.check_subscription.check_subscriptions',
        'schedule': 200.0,  # 200 seconds
    },
} 
