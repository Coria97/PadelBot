import time
import asyncio
import schedule

from src.config import CHECK_INTERVAL 
from src.logger import setup_logger
from src.scraper import PadelScraper
from src.telegram_notifier import TelegramNotifier

logger = setup_logger(__name__)

async def run_check():
    """
    Executes the availability check using PadelScraper
    """
    logger.info("Starting availability check...")
    scraper = PadelScraper()
    await scraper.check_availability()

async def main():
    """
    Main function that schedules and runs the checks
    """
    logger.info("Starting PadelBot...")

    # Initialize the Telegram notifier
    telegram_notifier = TelegramNotifier()
    asyncio.create_task(telegram_notifier.start_polling())

    # Schedule the initial check
    await run_check()

    # Schedule periodic checks
    schedule.every(CHECK_INTERVAL).minutes.do(lambda: asyncio.run(run_check()))

    # Keep the program running
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main()) 