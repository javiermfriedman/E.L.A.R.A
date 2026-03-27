from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ContactCreate(BaseModel):
    name: str
    phone_number: str


class ContactResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    phone_number: str
    image: str | None
    created_at: datetime

class ContactDeleteResponse(BaseModel):
    message: str