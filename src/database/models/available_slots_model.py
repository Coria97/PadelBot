from sqlalchemy import Column, Integer, String, DateTime

from datetime import datetime

from src.database.models.base_model import Base


class AvailableSlot(Base):
    __tablename__ = 'available_slots'

    id = Column(Integer, primary_key=True)
    day = Column(String, nullable=False)  # Format: DD/MM/YYYY
    hour = Column(String, nullable=False)  # Format: HH:MM
    court = Column(String, nullable=False)
    attributes = Column(String)
    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<AvailableSlot(day='{self.day}', hour='{self.hour}', court='{self.court}')>" 
