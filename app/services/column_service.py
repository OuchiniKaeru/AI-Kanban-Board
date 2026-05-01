from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional
from app.models.column import KanbanColumn
from app.models.task import Task
from app.schemas.column import ColumnCreate, ColumnUpdate
from app.services.task_service import TaskService



class ColumnService:
    @staticmethod
    async def get_columns(db: AsyncSession, project_id: Optional[int] = None) -> List[KanbanColumn]:
        if project_id is not None:
            result = await db.execute(
                select(KanbanColumn)
                .where(KanbanColumn.project_id == project_id)
                .order_by(KanbanColumn.order_index)
            )
        else:
            result = await db.execute(
                select(KanbanColumn)
                # .where(KanbanColumn.project_id.is_(None))
                .order_by(KanbanColumn.order_index)
            )
        return result.scalars().all()
    
    @staticmethod
    async def get_column(db: AsyncSession, column_id: int) -> Optional[KanbanColumn]:
        result = await db.execute(select(KanbanColumn).where(KanbanColumn.id == column_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create_column(db: AsyncSession, column_data: ColumnCreate) -> KanbanColumn:
        result = await db.execute(
            select(KanbanColumn).order_by(KanbanColumn.order_index.desc())
        )
        last_col = result.scalar_one_or_none()
        order_index = (last_col.order_index + 1) if last_col else 0
        
        column = KanbanColumn(
            name=column_data.name,
            order_index=order_index
        )
        db.add(column)
        await db.commit()
        await db.refresh(column)
        return column
    
    @staticmethod
    async def update_column(db: AsyncSession, column_id: int, column_data: ColumnUpdate) -> Optional[KanbanColumn]:
        column = await ColumnService.get_column(db, column_id)
        if not column:
            return None
        
        update_data = column_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(column, field, value)
        
        await db.commit()
        await db.refresh(column)
        return column
    
    @staticmethod
    async def delete_column(db: AsyncSession, column_id: int) -> bool:
        column = await ColumnService.get_column(db, column_id)
        if not column:
            return False
        
        # Check if column has tasks
        result = await db.execute(select(Task).where(Task.column_id == column_id))
        tasks = result.scalars().all()
        if tasks:
            return False
        
        await db.delete(column)
        await db.commit()
        return True
    
    @staticmethod
    async def init_default_columns(db: AsyncSession) -> None:
        result = await db.execute(select(KanbanColumn))
        columns = result.scalars().all()
        if not columns:
            defaults = ["ToDo", "Doing", "Done"]
            for i, name in enumerate(defaults):
                column = KanbanColumn(name=name, order_index=i)
                db.add(column)
            await db.commit()
