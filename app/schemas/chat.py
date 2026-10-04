from pydantic import BaseModel, Field


class ChatIn(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000, examples=["Hi, who are you?"])


class ChatOut(BaseModel):
    reply: str
    employee_id: str
    employee_email: str
