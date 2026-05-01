from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ChatMessageBase(BaseModel):
    role: str
    content: str


class ChatMessageCreate(ChatMessageBase):
    pass


class ChatMessageResponse(ChatMessageBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ScheduleExecuteRequest(BaseModel):
    schedule_id: int
    schedule_name: str
    command: str
    project_id: Optional[int] = None


class ChatResponse(BaseModel):
    success: bool
    message: str
    actions: Optional[list] = None
    requires_confirmation: bool = False
