from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RecordingsResponse(BaseModel):
    """List/detail metadata only — never put raw audio in JSON."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime
