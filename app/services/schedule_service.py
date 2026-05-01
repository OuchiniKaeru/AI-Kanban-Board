from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional
from datetime import datetime

from app.models.schedule import Schedule, ScheduleResource, TaskScheduleLog
from app.schemas.schedule import ScheduleCreate, ScheduleUpdate, ScheduleResourceCreate


class ScheduleService:
    @staticmethod
    async def get_schedules(db: AsyncSession, task_id: Optional[int] = None) -> List[Schedule]:
        query = select(Schedule).order_by(Schedule.created_at.desc())
        if task_id is not None:
            query = query.where(Schedule.task_id == task_id)
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_schedule(db: AsyncSession, schedule_id: int) -> Optional[Schedule]:
        result = await db.execute(select(Schedule).where(Schedule.id == schedule_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def create_schedule(db: AsyncSession, schedule_data: ScheduleCreate) -> Schedule:
        schedule = Schedule(
            name=schedule_data.name,
            description=schedule_data.description,
            project_id=schedule_data.project_id,
            task_id=schedule_data.task_id,
            command=schedule_data.command,
            command_type=schedule_data.command_type,
            schedule_type=schedule_data.schedule_type,
            interval_minutes=schedule_data.interval_minutes,
            cron_expression=schedule_data.cron_expression,
            is_enabled=schedule_data.is_enabled,
            append_to_task_description=schedule_data.append_to_task_description,
        )
        db.add(schedule)
        await db.commit()
        await db.refresh(schedule)

        # Create resources if provided
        if schedule_data.resources:
            for res_data in schedule_data.resources:
                resource = ScheduleResource(
                    schedule_id=schedule.id,
                    resource_type=res_data.resource_type,
                    path=res_data.path,
                )
                db.add(resource)
            await db.commit()
            await db.refresh(schedule)

        return schedule

    @staticmethod
    async def update_schedule(db: AsyncSession, schedule_id: int, schedule_data: ScheduleUpdate) -> Optional[Schedule]:
        schedule = await ScheduleService.get_schedule(db, schedule_id)
        if not schedule:
            return None

        update_data = schedule_data.model_dump(exclude_unset=True)
        # Remove resources from update_data as they're handled separately
        update_data.pop("resources", None)
        for field, value in update_data.items():
            setattr(schedule, field, value)

        await db.commit()
        await db.refresh(schedule)
        return schedule

    @staticmethod
    async def delete_schedule(db: AsyncSession, schedule_id: int) -> bool:
        schedule = await ScheduleService.get_schedule(db, schedule_id)
        if not schedule:
            return False

        await db.delete(schedule)
        await db.commit()
        return True

    @staticmethod
    async def update_last_run(db: AsyncSession, schedule_id: int, status: str, result: str) -> None:
        schedule = await ScheduleService.get_schedule(db, schedule_id)
        if schedule:
            schedule.last_run_at = datetime.now()
            schedule.last_run_status = status
            schedule.last_run_result = result
            await db.commit()

    # Resource management
    @staticmethod
    async def get_resources(db: AsyncSession, schedule_id: int) -> List[ScheduleResource]:
        result = await db.execute(
            select(ScheduleResource).where(ScheduleResource.schedule_id == schedule_id)
        )
        return result.scalars().all()

    @staticmethod
    async def add_resource(db: AsyncSession, schedule_id: int, resource_data: ScheduleResourceCreate) -> ScheduleResource:
        resource = ScheduleResource(
            schedule_id=schedule_id,
            resource_type=resource_data.resource_type,
            path=resource_data.path,
        )
        db.add(resource)
        await db.commit()
        await db.refresh(resource)
        return resource

    @staticmethod
    async def delete_resource(db: AsyncSession, resource_id: int) -> bool:
        result = await db.execute(select(ScheduleResource).where(ScheduleResource.id == resource_id))
        resource = result.scalar_one_or_none()
        if not resource:
            return False
        await db.delete(resource)
        await db.commit()
        return True

    # Log management
    @staticmethod
    async def add_log(db: AsyncSession, schedule_id: int, status: str, result: str, execution_time_sec: float) -> TaskScheduleLog:
        log = TaskScheduleLog(
            schedule_id=schedule_id,
            executed_at=datetime.now(),
            status=status,
            result=result,
            execution_time_sec=execution_time_sec,
        )
        db.add(log)
        await db.commit()
        await db.refresh(log)
        return log

    @staticmethod
    async def get_logs(db: AsyncSession, schedule_id: int, limit: int = 50) -> List[TaskScheduleLog]:
        result = await db.execute(
            select(TaskScheduleLog)
            .where(TaskScheduleLog.schedule_id == schedule_id)
            .order_by(desc(TaskScheduleLog.executed_at))
            .limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def clear_logs(db: AsyncSession, schedule_id: int) -> None:
        await db.execute(
            TaskScheduleLog.__table__.delete().where(TaskScheduleLog.schedule_id == schedule_id)
        )
        await db.commit()
