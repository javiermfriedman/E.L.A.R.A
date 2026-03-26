from datetime import datetime

from fastapi import UploadFile
from pydantic import BaseModel, ConfigDict, Field


class AgentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    system_prompt: str
    first_message: str
    voice_id: str | None
    image: str | None
    created_at: datetime
