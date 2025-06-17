from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

from src.database.models.base_model import Base


class Subscription(Base):
    __tablename__ = 'subscriptions'

    id = Column(Integer, primary_key=True)
    chat_id = Column(String, nullable=False)
    day = Column(String, nullable=False)
    hour = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<Subscription (day='{self.day}', hour='{self.hour}', chat_id='{self.chat_id}')>" 
