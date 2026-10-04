from pydantic import BaseModel, Field


class ChatIn(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000, examples=["Hi, who are you?"])
    thread_id: str | None = Field(
        default=None,
        description="Conversation thread id. Omit to start a new thread.",
        examples=["3f1c8e2a-7b4d-4c9a-9e2f-1a2b3c4d5e6f"],
    )


class ChatOut(BaseModel):
    reply: str
    thread_id: str
    employee_id: str
    employee_email: str
