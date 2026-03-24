from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app.database import Base

class Agents(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    voice_id = Column(String)
    name = Column(String)
    description = Column(String)    
    system_prompt = Column(String)
    first_message = Column(String)
    created_at = Column(DateTime, default=datetime.now)