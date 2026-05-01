from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from typing import List, Optional
from datetime import datetime
from app.models.task import Task
from app.models.column import KanbanColumn
from app.schemas.task import TaskCreate, TaskUpdate


class TaskService:
    @staticmethod
    async def get_tasks(
        db: AsyncSession,
        column_id: Optional[int] = None,
        project_id: Optional[int] = None,
        priority: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[Task]:
        query = select(Task).order_by(Task.order_index)
        
        if column_id is not None:
            query = query.where(Task.column_id == column_id)
        if project_id is not None:
            query = query.where(Task.project_id == project_id)
        if priority is not None:
            query = query.where(Task.priority == priority)
        if search is not None:
            query = query.where(
                Task.title.ilike(f"%{search}%") | Task.description.ilike(f"%{search}%")
            )
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_task(db: AsyncSession, task_id: int) -> Optional[Task]:
        result = await db.execute(select(Task).where(Task.id == task_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create_task(db: AsyncSession, task_data: TaskCreate) -> Task:
        result = await db.execute(
            select(Task).where(Task.column_id == task_data.column_id).order_by(Task.order_index.desc()).limit(1)
        )
        last_task = result.scalar_one_or_none()
        order_index = (last_task.order_index + 1) if last_task else 0
        
        task = Task(
            title=task_data.title,
            description=task_data.description,
            column_id=task_data.column_id,
            project_id=task_data.project_id,
            priority=task_data.priority,
            due_date=task_data.due_date,
            order_index=order_index
        )
        db.add(task)
        await db.commit()
        await db.refresh(task)
        return task
    
    @staticmethod
    async def update_task(db: AsyncSession, task_id: int, task_data: TaskUpdate) -> Optional[Task]:
        task = await TaskService.get_task(db, task_id)
        if not task:
            return None
        
        update_data = task_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)
        
        await db.commit()
        await db.refresh(task)
        return task
    
    @staticmethod
    async def delete_task(db: AsyncSession, task_id: int) -> bool:
        task = await TaskService.get_task(db, task_id)
        if not task:
            return False
        
        await db.delete(task)
        await db.commit()
        return True
    
    @staticmethod
    async def get_overdue_tasks(db: AsyncSession) -> List[Task]:
        from datetime import date
        result = await db.execute(
            select(Task).where(Task.due_date < date.today())
        )
        return result.scalars().all()

    @staticmethod
    async def move_task(
        db: AsyncSession,
        task_id: int,
        column_id: int,
        order_index: int
    ) -> Optional[Task]:
        task = await TaskService.get_task(db, task_id)
        if not task:
            return None

        # 移動先カラムが存在するか確認
        column_result = await db.execute(
            select(KanbanColumn).where(KanbanColumn.id == column_id)
        )
        column = column_result.scalar_one_or_none()
        if not column:
            return None

        # 移動先カラムの既存タスクをorder_index以降にずらす
        await db.execute(
            update(Task)
            .where(Task.column_id == column_id, Task.order_index >= order_index)
            .values(order_index=Task.order_index + 1)
        )

        task.column_id = column_id
        task.order_index = order_index

        await db.commit()
        await db.refresh(task)
        return task

    @staticmethod
    async def append_schedule_result(
        db: AsyncSession,
        task_id: int,
        schedule_name: str,
        status: str,
        result: str,
        execution_time: float
    ) -> None:
        task = await TaskService.get_task(db, task_id)
        if not task:
            return

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status_icon = "success" if status == "success" else "error"
        block = f"""---
[定期実行: {schedule_name}] {timestamp}
ステータス: {status_icon}
実行時間: {execution_time:.1f}s

結果:
{result}
---"""

        current = task.description or ""
        if current:
            task.description = f"{current}\n\n{block}"
        else:
            task.description = block

        separator = "\n---\n"
        blocks = task.description.split(separator)
        if len(blocks) > 51:
            original = blocks[0]
            history = blocks[-50:]
            task.description = original + separator + separator.join(history)

        await db.commit()
