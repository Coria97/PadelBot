import asyncio
from src.logger import setup_logger
from src.telegram_bot import TelegramBot
from telegram import Update

logger = setup_logger(__name__)

# create a global instance of the telegram bot
telegram_bot = None

def main():
    """
    Main function that runs the Telegram bot
    """
    global telegram_bot
    logger.info("Starting PadelBot...")
    
    try:
        logger.info("Initializing Telegram bot...")
        # Initialize the Telegram notifier
        telegram_bot = TelegramBot()
        logger.info("Telegram bot initialized successfully")

        logger.info("Starting bot polling...")
        # Start the bot (this will block until the bot is stopped)
        telegram_bot.application.run_polling(allowed_updates=Update.ALL_TYPES)

    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise 