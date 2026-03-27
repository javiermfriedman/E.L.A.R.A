import base64
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, LargeBinary, String

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
    image_filename = Column(String)
    image_data = Column(LargeBinary)
    created_at = Column(DateTime, default=datetime.now)

    @property
    def image(self) -> str | None:
        if self.image_data is None:
            return None
        return base64.b64encode(self.image_data).decode()
