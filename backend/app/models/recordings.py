from app.database import Base
from sqlalchemy import Column, Integer, String, LargeBinary, DateTime, ForeignKey
import datetime

class Recordings(Base):
    __tablename__ = "recordings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    audio = Column(LargeBinary, nullable=False)     # LargeBinary maps to BYTEA in Postgres
    created_at = Column(DateTime, default=datetime.datetime.now)