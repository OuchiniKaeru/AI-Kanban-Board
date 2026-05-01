from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ScheduleResourceBase(BaseModel):
    resource_type: str
    path: str


class ScheduleResourceCreate(ScheduleResourceBase):
    pass


class ScheduleResourceResponse(ScheduleResourceBase):
    id: int
    schedule_id: int
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


class TaskScheduleLogResponse(BaseModel):
    id: int
    schedule_id: int
    executed_at: datetime
    status: str
    result: Optional[str]
    execution_time_sec: Optional[float]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


class ScheduleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    project_id: Optional[int] = None
    task_id: Optional[int] = None
    command: str
    command_type: str = "agent"
    schedule_type: str
    interval_minutes: Optional[int] = None
    cron_expression: Optional[str] = None
    is_enabled: bool = True
    append_to_task_description: bool = True
    resources: Optional[List[ScheduleResourceCreate]] = None


class ScheduleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    project_id: Optional[int] = None
    task_id: Optional[int] = None
    command: Optional[str] = None
    command_type: Optional[str] = None
    schedule_type: Optional[str] = None
    interval_minutes: Optional[int] = None
    cron_expression: Optional[str] = None
    is_enabled: Optional[bool] = None
    append_to_task_description: Optional[bool] = None


class ScheduleResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    project_id: Optional[int]
    task_id: Optional[int]
    command: str
    command_type: str
    schedule_type: str
    interval_minutes: Optional[int]
    cron_expression: Optional[str]
    is_enabled: bool
    append_to_task_description: bool
    last_run_at: Optional[datetime]
    last_run_status: Optional[str]
    last_run_result: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    resources: Optional[List[ScheduleResourceResponse]] = None

    class Config:
        from_attributes = True
