from datetime import datetime

from celery import shared_task

from src.database.operations.subscription_manager import subscription_manager
from src.database.operations.available_slots_manager import available_slots_manager
from src.logger import setup_logger
from src.telegram_bot import TelegramBot

logger = setup_logger(__name__)


@shared_task
def check_subscriptions():
    """
    Task that checks subscriptions and notifies users if slots are available.
    Deletes past subscriptions and notifies about future ones if availability exists.
    """
    logger.info("Starting subscription verification")
    
    try:
        # Create a new instance of the Telegram bot for this task
        telegram_bot = TelegramBot()
        logger.info("Telegram bot initialized for subscription check")
    except Exception as e:
        logger.error(f"Failed to initialize Telegram bot: {str(e)}")
        return

    current_date = datetime.now().strftime('%d/%m/%Y')
    
    # Get all subscriptions
    subscriptions = subscription_manager.get_subscriptions()
    
    for subscription in subscriptions:
        logger.debug(f"Processing subscription: day={subscription.day}, hour={subscription.hour}, chat_id={subscription.chat_id}")
        
        # Compare dates
        sub_date = datetime.strptime(subscription.day, '%d/%m/%Y')
        current_date_obj = datetime.strptime(current_date, '%d/%m/%Y')
        
        if sub_date < current_date_obj:
            # Delete past subscriptions
            logger.info(f"Deleting past subscription: {subscription.day} {subscription.hour}")
            subscription_manager.session.delete(subscription)
            subscription_manager.session.commit()
        else:
            # Check availability for future subscriptions
            available_slots = available_slots_manager.get_available_slots_by_day_and_hour(
                subscription.day,
                subscription.hour
            )
            
            if available_slots:
                # Notify user using the bot instance
                logger.info(f"Notifying availability to chat_id {subscription.chat_id} for {subscription.day} {subscription.hour}")
                # Use asyncio to run the async notification
                import asyncio
                slots_to_notify = available_slots[:3]
                asyncio.run(telegram_bot.notify_available_slots(slots_to_notify, subscription.chat_id))
                
            else:
                logger.debug(f"No slots available for {subscription.day} {subscription.hour}")
    