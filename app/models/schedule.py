from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=True)
    command = Column(Text, nullable=False)
    command_type = Column(String(20), nullable=False, default="agent")
    schedule_type = Column(String(20), nullable=False)
    interval_minutes = Column(Integer, nullable=True)
    cron_expression = Column(String(100), nullable=True)
    is_enabled = Column(Boolean, nullable=False, default=True)
    append_to_task_description = Column(Boolean, nullable=False, default=True)
    last_run_at = Column(DateTime(timezone=True), nullable=True)
    last_run_status = Column(String(20), nullable=True)
    last_run_result = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    project = relationship("Project", back_populates="schedules")
    task = relationship("Task", back_populates="schedules")
    resources = relationship("ScheduleResource", back_populates="schedule", cascade="all, delete-orphan")
    logs = relationship("TaskScheduleLog", back_populates="schedule", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "project_id": self.project_id,
            "task_id": self.task_id,
            "command": self.command,
            "command_type": self.command_type,
            "schedule_type": self.schedule_type,
            "interval_minutes": self.interval_minutes,
            "cron_expression": self.cron_expression,
            "is_enabled": self.is_enabled,
            "append_to_task_description": self.append_to_task_description,
            "last_run_at": self.last_run_at.isoformat() if self.last_run_at else None,
            "last_run_status": self.last_run_status,
            "last_run_result": self.last_run_result,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ScheduleResource(Base):
    __tablename__ = "schedule_resources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    schedule_id = Column(Integer, ForeignKey("schedules.id", ondelete="CASCADE"), nullable=False)
    resource_type = Column(String(20), nullable=False)
    path = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    schedule = relationship("Schedule", back_populates="resources")

    def to_dict(self):
        return {
            "id": self.id,
            "schedule_id": self.schedule_id,
            "resource_type": self.resource_type,
            "path": self.path,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class TaskScheduleLog(Base):
    __tablename__ = "task_schedule_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    schedule_id = Column(Integer, ForeignKey("schedules.id", ondelete="CASCADE"), nullable=False)
    executed_at = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(20), nullable=False)
    result = Column(Text, nullable=True)
    execution_time_sec = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    schedule = relationship("Schedule", back_populates="logs")

    def to_dict(self):
        return {
            "id": self.id,
            "schedule_id": self.schedule_id,
            "executed_at": self.executed_at.isoformat() if self.executed_at else None,
            "status": self.status,
            "result": self.result,
            "execution_time_sec": self.execution_time_sec,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
