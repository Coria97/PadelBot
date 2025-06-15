from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class AvailableSlot(Base):
    __tablename__ = 'available_slots'

    id = Column(Integer, primary_key=True)
    day = Column(String, nullable=False)
    hour = Column(String, nullable=False)
    court = Column(String, nullable=False)
    attributes = Column(String)
    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<AvailableSlot(day='{self.day}', hour='{self.hour}', court='{self.court}')>" 
