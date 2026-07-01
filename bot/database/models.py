from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, String, Integer, DateTime
from datetime import datetime

class Base(DeclarativeBase):
    pass

class Tasks(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    title = Column(String)
    description = Column(String)
    priority = Column(String)
    deadline = Column(DateTime)
    status = Column(String, default="انجام نشده")
    created_at = Column(DateTime, default=datetime.now)