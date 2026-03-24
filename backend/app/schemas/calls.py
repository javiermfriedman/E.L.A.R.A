from pydantic import BaseModel

class DialoutRequest(BaseModel):
    to_number: str
    agent_id: int

class TwilioCallResult(BaseModel):
    call_sid: str
    to_number: str

class DialoutResponse(BaseModel):
    call_sid: str
    status: str
    to_number: str

class TwimlRequest(BaseModel):
    to_number: str | None
    from_number: str | None
    call_sid: str | None