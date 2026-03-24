from app.database import Base
from sqlalchemy import Column, Integer, String, LargeBinary, DateTime, ForeignKey
import datetime

class Recording(Base):
    __tablename__ = "recordings"

    id = Column(Integer, primary_key=True, index=True)
    call_sid = Column(String, nullable=False, index=True)
    track = Column(String, nullable=False)          # 'merged', 'user', or 'bot'
    audio = Column(LargeBinary, nullable=False)     # LargeBinary maps to BYTEA in Postgres
    created_at = Column(DateTime, default=datetime.datetime.now)