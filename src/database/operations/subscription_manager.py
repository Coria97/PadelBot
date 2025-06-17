import os

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from datetime import datetime

from src.logger import setup_logger
from src.database.models.base_model import Base
from src.database.models.available_slots_model import AvailableSlot
from src.database.models.subscription_model import Subscription

logger = setup_logger(__name__)

# Create the SQLite database with an absolute path
db_path = os.path.join('/app/data', 'padel_slots.db')
engine = create_engine(f'sqlite:///{db_path}')

# Create all tables
Base.metadata.create_all(engine)

class SubscriptionManager:
    def __init__(self):
        self.Session = sessionmaker(bind=engine)

    def add_subscription(self, day, hour, chat_id):
        """
        Add a new subscription to the database.
        
        Args:
            day (str): Day of the week for the subscription
            hour (str): Hour of the day for the subscription
            chat_id (int): Telegram chat ID of the subscriber
            
        Returns:
            Subscription: The created subscription object
            
        Raises:
            ValueError: If the day or hour format is invalid
            SQLAlchemyError: If there's an error during database operations
        """
        try:
            # Validate day and hour format
            if not isinstance(day, str) or not isinstance(hour, str):
                raise ValueError("Day and hour must be strings")
                
            subscription = Subscription(day=day, hour=hour, chat_id=chat_id)
            self.session.add(subscription)
            self.session.commit()
            logger.info(f"Added new subscription for chat_id {chat_id} on {day} at {hour}")
            return subscription
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error adding subscription: {str(e)}")
            raise

    def get_subscriptions(self, chat_id=None):
        """
        Retrieve subscriptions from the database.
        
        Args:
            chat_id (int, optional): Filter subscriptions by chat_id
            
        Returns:
            list: List of Subscription objects
            
        Raises:
            SQLAlchemyError: If there's an error during database operations
        """
        try:
            query = self.session.query(Subscription)
            return query.all()
        except Exception as e:
            logger.error(f"Error retrieving subscriptions: {str(e)}")
            raise

# Create a global instance of AvailableSlotsManager
subscription_manager = SubscriptionManager()

# For backward compatibility
def add_subscription(day, hour, chat_id):
    return subscription_manager.add_subscription(day, hour, chat_id)

def get_subscriptions():
    return subscription_manager.get_subscriptions() 
