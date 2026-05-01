from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.schemas.schedule import (
    ScheduleCreate, ScheduleUpdate, ScheduleResponse,
    ScheduleResourceCreate, ScheduleResourceResponse,
    TaskScheduleLogResponse
)
from app.services.schedule_service import ScheduleService
from app.scheduler import kanban_scheduler

router = APIRouter(prefix="/api/schedules", tags=["schedules"])


@router.get("", response_model=List[ScheduleResponse])
async def get_schedules(task_id: int = None, db: AsyncSession = Depends(get_db)):
    schedules = await ScheduleService.get_schedules(db, task_id=task_id)
    # Load resources for each schedule
    result = []
    for schedule in schedules:
        schedule_dict = schedule.to_dict()
        resources = await ScheduleService.get_resources(db, schedule.id)
        schedule_dict["resources"] = [r.to_dict() for r in resources]
        result.append(schedule_dict)
    return result


@router.post("", response_model=ScheduleResponse)
async def create_schedule(schedule: ScheduleCreate, db: AsyncSession = Depends(get_db)):
    created = await ScheduleService.create_schedule(db, schedule)
    if created.is_enabled:
        kanban_scheduler.add_job(created)
    schedule_dict = created.to_dict()
    resources = await ScheduleService.get_resources(db, created.id)
    schedule_dict["resources"] = [r.to_dict() for r in resources]
    return schedule_dict


@router.get("/{schedule_id}", response_model=ScheduleResponse)
async def get_schedule(schedule_id: int, db: AsyncSession = Depends(get_db)):
    schedule = await ScheduleService.get_schedule(db, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    schedule_dict = schedule.to_dict()
    resources = await ScheduleService.get_resources(db, schedule.id)
    schedule_dict["resources"] = [r.to_dict() for r in resources]
    return schedule_dict


@router.put("/{schedule_id}", response_model=ScheduleResponse)
async def update_schedule(schedule_id: int, schedule: ScheduleUpdate, db: AsyncSession = Depends(get_db)):
    updated = await ScheduleService.update_schedule(db, schedule_id, schedule)
    if not updated:
        raise HTTPException(status_code=404, detail="Schedule not found")
    kanban_scheduler.remove_job(schedule_id)
    if updated.is_enabled:
        kanban_scheduler.add_job(updated)
    schedule_dict = updated.to_dict()
    resources = await ScheduleService.get_resources(db, updated.id)
    schedule_dict["resources"] = [r.to_dict() for r in resources]
    return schedule_dict


@router.delete("/{schedule_id}")
async def delete_schedule(schedule_id: int, db: AsyncSession = Depends(get_db)):
    kanban_scheduler.remove_job(schedule_id)
    success = await ScheduleService.delete_schedule(db, schedule_id)
    if not success:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return {"message": "Schedule deleted"}


@router.post("/{schedule_id}/run")
async def run_schedule_now(schedule_id: int, db: AsyncSession = Depends(get_db)):
    schedule = await ScheduleService.get_schedule(db, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    await kanban_scheduler._execute_command(
        schedule.id, schedule.command, schedule.project_id, schedule.task_id
    )
    return {"message": "Schedule executed"}


# Resource management
@router.get("/{schedule_id}/resources", response_model=List[ScheduleResourceResponse])
async def get_resources(schedule_id: int, db: AsyncSession = Depends(get_db)):
    schedule = await ScheduleService.get_schedule(db, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    resources = await ScheduleService.get_resources(db, schedule_id)
    return resources


@router.post("/{schedule_id}/resources", response_model=ScheduleResourceResponse)
async def add_resource(schedule_id: int, resource: ScheduleResourceCreate, db: AsyncSession = Depends(get_db)):
    schedule = await ScheduleService.get_schedule(db, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    created = await ScheduleService.add_resource(db, schedule_id, resource)
    return created


@router.delete("/{schedule_id}/resources/{resource_id}")
async def delete_resource(schedule_id: int, resource_id: int, db: AsyncSession = Depends(get_db)):
    success = await ScheduleService.delete_resource(db, resource_id)
    if not success:
        raise HTTPException(status_code=404, detail="Resource not found")
    return {"message": "Resource deleted"}


# Log management
@router.get("/{schedule_id}/logs", response_model=List[TaskScheduleLogResponse])
async def get_logs(schedule_id: int, limit: int = 50, db: AsyncSession = Depends(get_db)):
    schedule = await ScheduleService.get_schedule(db, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    logs = await ScheduleService.get_logs(db, schedule_id, limit=limit)
    return logs


@router.delete("/{schedule_id}/logs")
async def clear_logs(schedule_id: int, db: AsyncSession = Depends(get_db)):
    schedule = await ScheduleService.get_schedule(db, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    await ScheduleService.clear_logs(db, schedule_id)
    return {"message": "Logs cleared"}
