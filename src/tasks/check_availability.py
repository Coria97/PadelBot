import asyncio
from ..scraper import PadelScraper
from ..logger import setup_logger
from .celery_config import celery_app

logger = setup_logger(__name__)

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