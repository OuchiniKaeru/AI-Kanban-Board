from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    column_id: Optional[int] = None
    project_id: int
    priority: str = Field("medium", pattern="^(low|medium|high)$")
    due_date: Optional[date] = None
    order_index: int = 0


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    column_id: Optional[int] = None
    priority: Optional[str] = Field(None, pattern="^(low|medium|high)$")
    due_date: Optional[date] = None
    order_index: Optional[int] = None


class TaskResponse(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
