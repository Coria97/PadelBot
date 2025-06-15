from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from src.logger import setup_logger

from src.database.models.available_slots_model import Base, AvailableSlot

logger = setup_logger(__name__)

# Create the SQLite database with a relative path
db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'padel_slots.db')
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
            day (str): Day in format DD/MM
            hour (str): Hour in format HH:MM
            
        Returns:
            list: List of available slots
        """
        session = self.Session()
        try:
            # Convert hour string to datetime for comparison
            target_hour = datetime.strptime(hour, '%H:%M').time()
            
            # Add current year to the day
            current_year = datetime.now().year
            day_with_year = f"{day}/{current_year}"
            
            # Get slots for the specified day
            slots = session.query(AvailableSlot) \
                .filter(AvailableSlot.day == day_with_year) \
                .all()
                
            # Filter slots by hour range (3 hours window)
            filtered_slots = []
            for slot in slots:
                slot_hour = datetime.strptime(slot.hour, '%H:%M').time()
                # Check if slot is within 3 hours window
                if target_hour <= slot_hour <= datetime.strptime('22:00', '%H:%M').time():
                    filtered_slots.append(slot)
                    
            return filtered_slots
        finally:
            session.close()

# Create a global instance of AvailableSlotsManager
available_slots_manager = AvailableSlotsManager()

# For backward compatibility
def save_slots(slots):
    return available_slots_manager.save_slots(slots)

def get_available_slots_by_day_and_hour(day, hour):
    return available_slots_manager.get_available_slots_by_day_and_hour(day, hour) 