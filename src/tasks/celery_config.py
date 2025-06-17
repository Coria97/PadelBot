from celery import Celery
from ..config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND, CHECK_INTERVAL

# Celery configuration
celery_app = Celery(
    'padelbot',
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND
)

# Celery beat schedule configuration
celery_app.conf.beat_schedule = {
    'check-availability': {
        'task': 'src.tasks.check_availability.check_availability',
        'schedule': CHECK_INTERVAL * 60.0,  # Convert minutes to seconds
    },
} 
