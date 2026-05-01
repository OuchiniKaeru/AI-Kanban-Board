from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import date, timedelta
from typing import Dict, List
from app.models.task import Task
from app.models.column import KanbanColumn


class ReportService:
    @staticmethod
    async def get_summary(db: AsyncSession) -> Dict:
        # Total tasks
        result = await db.execute(select(func.count(Task.id)))
        total_tasks = result.scalar()
        
        # Tasks by column
        result = await db.execute(
            select(KanbanColumn.name, func.count(Task.id))
            .outerjoin(Task, KanbanColumn.id == Task.column_id)
            .group_by(KanbanColumn.id)
        )
        column_stats = {name: count for name, count in result.all()}
        
        # Tasks by priority
        result = await db.execute(
            select(Task.priority, func.count(Task.id))
            .group_by(Task.priority)
        )
        priority_stats = {priority: count for priority, count in result.all()}
        
        # Overdue tasks
        today = date.today()
        result = await db.execute(
            select(func.count(Task.id)).where(Task.due_date < today)
        )
        overdue_count = result.scalar()
        
        # Due this week
        week_end = today + timedelta(days=7)
        result = await db.execute(
            select(func.count(Task.id))
            .where(Task.due_date >= today)
            .where(Task.due_date <= week_end)
        )
        due_this_week = result.scalar()
        
        return {
            "total_tasks": total_tasks,
            "column_stats": column_stats,
            "priority_stats": priority_stats,
            "overdue_count": overdue_count,
            "due_this_week": due_this_week
        }
    
    @staticmethod
    async def get_weekly_report(db: AsyncSession) -> Dict:
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        # Tasks created this week
        result = await db.execute(
            select(func.count(Task.id))
            .where(func.date(Task.created_at) >= week_start)
        )
        created_this_week = result.scalar()
        
        # Tasks completed this week (moved to Done)
        result = await db.execute(
            select(func.count(Task.id))
            .where(func.date(Task.updated_at) >= week_start)
        )
        completed_this_week = result.scalar()
        
        summary = await ReportService.get_summary(db)
        
        return {
            "week_start": week_start.isoformat(),
            "week_end": week_end.isoformat(),
            "created_this_week": created_this_week,
            "completed_this_week": completed_this_week,
            "summary": summary
        }
