from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AgentCreate(BaseModel):
    name: str
    description: str
    system_prompt: str
    first_message: str = Field(default="Hello how are you today?")
    voice_id: str = Field(default="zmcVlqmyk3Jpn5AVYcAL")

class AgentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    system_prompt: str
    voice_id: str
    first_message: str
    created_at: datetime
