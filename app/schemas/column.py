from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class ColumnBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    order_index: int = 0


class ColumnCreate(ColumnBase):
    pass


class ColumnUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    order_index: Optional[int] = None


class ColumnResponse(ColumnBase):
    id: int
    created_at: datetime
    tasks: List["TaskResponse"] = []
    
    class Config:
        from_attributes = True


# Forward reference for circular import
from app.schemas.task import TaskResponse
ColumnResponse.model_rebuild()
