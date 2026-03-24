from pydantic import BaseModel
from datetime import datetime
class ContactCreate(BaseModel):
    name: str
    phone_number: str

class ContactResponse(BaseModel):
    id: int
    name: str
    phone_number: str
    created_at: datetime
    class Config:
        from_attributes = True  # allows converting SQLAlchemy models to this schema

