from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.database import get_db
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.schemas.schedule import ScheduleResponse
from app.services.task_service import TaskService
from app.services.schedule_service import ScheduleService

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("", response_model=List[TaskResponse])
async def list_tasks(
    column_id: Optional[int] = Query(None),
    priority: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    tasks = await TaskService.get_tasks(db, column_id=column_id, priority=priority, search=search)
    return tasks


@router.post("", response_model=TaskResponse)
async def create_task(task: TaskCreate, db: AsyncSession = Depends(get_db)):
    return await TaskService.create_task(db, task)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, db: AsyncSession = Depends(get_db)):
    task = await TaskService.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, task: TaskUpdate, db: AsyncSession = Depends(get_db)):
    updated = await TaskService.update_task(db, task_id, task)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated


@router.delete("/{task_id}")
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await TaskService.delete_task(db, task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}


@router.put("/{task_id}/move", response_model=TaskResponse)
async def move_task(
    task_id: int,
    column_id: int = Query(...),
    order_index: int = Query(0),
    db: AsyncSession = Depends(get_db)
):
    moved = await TaskService.move_task(db, task_id, column_id, order_index)
    if not moved:
        raise HTTPException(status_code=404, detail="Task not found")
    return moved


@router.get("/{task_id}/schedules", response_model=List[ScheduleResponse])
async def get_task_schedules(task_id: int, db: AsyncSession = Depends(get_db)):
    task = await TaskService.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    schedules = await ScheduleService.get_schedules(db, task_id=task_id)
    result = []
    for schedule in schedules:
        schedule_dict = schedule.to_dict()
        resources = await ScheduleService.get_resources(db, schedule.id)
        schedule_dict["resources"] = [r.to_dict() for r in resources]
        result.append(schedule_dict)
    return result
