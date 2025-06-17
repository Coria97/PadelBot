from datetime import datetime

from celery import shared_task

from src.database.operations.subscription_manager import subscription_manager
from src.database.operations.available_slots_manager import available_slots_manager
from src.logger import setup_logger
from src.main import telegram_bot

logger = setup_logger(__name__)


@shared_task
def check_subscriptions():
    """
    Task that checks subscriptions and notifies users if slots are available.
    Deletes past subscriptions and notifies about future ones if availability exists.
    """
    if telegram_bot is None:
        logger.error("Telegram bot is not initialized")
        return

    current_date = datetime.now().strftime('%d/%m/%Y')
    
    # Get all subscriptions
    subscriptions = subscription_manager.get_subscriptions()
    
    for subscription in subscriptions:
        # Compare dates
        sub_date = datetime.strptime(subscription.day, '%d/%m/%Y')
        
        if sub_date < current_date:
            # Delete past subscriptions
            subscription_manager.session.delete(subscription)
            subscription_manager.session.commit()
        else:
            # Check availability for future subscriptions
            available_slots = available_slots_manager.get_available_slots_by_day_and_hour(
                subscription.day,
                subscription.hour
            )
            
            if available_slots:
                # Notify user using global bot instance
                telegram_bot.notify_available_slots(available_slots, subscription.chat_id)
