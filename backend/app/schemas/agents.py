from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AgentCreate(BaseModel):
    name: str
    description: str
    system_prompt: str
    voice_id: str = Field(
        default="zmcVlqmyk3Jpn5AVYcAL",
        description="ElevenLabs voice id; defaults to project default if omitted",
    )


class AgentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    system_prompt: str
    voice_id: str | None
    created_at: datetime
