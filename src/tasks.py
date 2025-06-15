from celery import Celery
import asyncio
from .scraper import PadelScraper
from .config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND, CHECK_INTERVAL
from .logger import setup_logger

logger = setup_logger(__name__)

# Celery configuration
celery_app = Celery(
    'padelbot',
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND
)

# Celery configuration
celery_app.conf.beat_schedule = {
    'check-availability': {
        'task': 'src.tasks.check_availability',
        'schedule': CHECK_INTERVAL * 60.0,  # Convert minutes to seconds
    },
}

@celery_app.task
def check_availability():
    """
    Celery task to check for availability of slots
    """
    try:
        logger.info("Starting check availability task...")
        scraper = PadelScraper()

        # Run the scraper and wait for the result
        available_slots = asyncio.run(scraper.check_availability())
        logger.info("Check availability task completed successfully")
        return {"status": "success", "slots_found": len(available_slots)}
    except Exception as e:
        logger.error(f"Error in check availability task: {str(e)}")
        raise 