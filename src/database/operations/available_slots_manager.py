import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from datetime import datetime, timedelta

from src.logger import setup_logger
from src.database.models.base_model import Base
from src.database.models.available_slots_model import AvailableSlot
from src.database.models.subscription_model import Subscription

logger = setup_logger(__name__)

# Create the SQLite database with an absolute path
db_path = os.path.join('/app/data', 'padel_bot.db')
engine = create_engine(f'sqlite:///{db_path}')

# Create all tables
Base.metadata.create_all(engine)

class AvailableSlotsManager:
    def __init__(self):
        self.Session = sessionmaker(bind=engine)

    def save_slots(self, slots):
        """
        Save the available slots in the database
        
        Args:
            slots (list): List of available slots
        """
        session = self.Session()
        
        try:
            # Delete all existing records
            session.query(AvailableSlot).delete()
            session.commit()
            logger.info(f"Deleted existing records from database")
            
            # Save the new slots
            for slot in slots:
                # Convert the slot to an AvailableSlot object
                db_slot = AvailableSlot(
                    day=slot['day'],
                    hour=slot['hour'],
                    court=slot['court'],
                    attributes=slot['attributes']
                )
                session.add(db_slot)

            session.commit()
            logger.info(f"Successfully saved {len(slots)} slots to database")
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving slots to database: {str(e)}")
            raise e
        finally:
            session.close()

    def get_available_slots_by_day_and_hour(self, day, hour):
        """
        Get available slots for a specific day and hour range
        
        Args:
            day (str): Day in format DD/MM/YYYY
            hour (str): Hour in format HH:MM
            
        Returns:
            list: List of available slots
        """
        session = self.Session()
        try:
            # Get slots for the specified day
            slots = session.query(AvailableSlot) \
                .filter(AvailableSlot.day == day) \
                .all()

            # Filter slots by hour range (3 hours window)
            filtered_slots = []
            target_hour = datetime.strptime(hour, '%H:%M').time()
            
            # Calculate end hour (3 hours after target hour)
            end_hour = datetime.combine(datetime.today(), target_hour) + timedelta(hours=3)
            end_hour = end_hour.time()
            
            for slot in slots:
                slot_hour = datetime.strptime(slot.hour, '%H:%M').time()
                # Check if slot is within 3 hours window
                if target_hour <= slot_hour <= end_hour:
                    filtered_slots.append({
                        'fecha': slot.day,
                        'hora': slot.hour,
                        'cancha': slot.court
                    })
            
            # Sort slots by hour
            filtered_slots.sort(key=lambda x: x['hora'])
            
            return filtered_slots
        except Exception as e:
            logger.error(f"Error getting available slots: {str(e)}")
            raise e
        finally:
            session.close()

# Create a global instance of AvailableSlotsManager
available_slots_manager = AvailableSlotsManager()

# For backward compatibility
def save_slots(slots):
    return available_slots_manager.save_slots(slots)

def get_available_slots_by_day_and_hour(day, hour):
    return available_slots_manager.get_available_slots_by_day_and_hour(day, hour) 