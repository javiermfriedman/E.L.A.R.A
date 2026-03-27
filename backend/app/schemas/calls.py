from pydantic import BaseModel

class DialoutRequest(BaseModel):
    agent_id: str
    to_number: str

class TwilioCallResult(BaseModel):
    call_sid: str
    to_number: str

class TwilioCallResult(BaseModel):
    call_sid: str
    to_number: str

class DialoutResponse(BaseModel):
    call_sid: str
    status: str
    to_number: str

class TwimlRequest(BaseModel):
    to_number: str
    from_number: str