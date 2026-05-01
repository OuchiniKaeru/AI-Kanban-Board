from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from app.models.project import Project
from app.models.column import KanbanColumn
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
    @staticmethod
    async def get_projects(db: AsyncSession) -> List[Project]:
        result = await db.execute(select(Project).order_by(Project.created_at.desc()))
        return result.scalars().all()

    @staticmethod
    async def get_project(db: AsyncSession, project_id: int) -> Optional[Project]:
        result = await db.execute(select(Project).where(Project.id == project_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def create_project(db: AsyncSession, project_data: ProjectCreate) -> Project:
        project = Project(
            name=project_data.name,
            description=project_data.description,
            color=project_data.color,
        )
        db.add(project)
        await db.commit()
        await db.refresh(project)

        defaults = ["ToDo", "Doing", "Done"]
        for i, name in enumerate(defaults):
            column = KanbanColumn(name=name, order_index=i, project_id=project.id)
            db.add(column)
        await db.commit()

        return project

    @staticmethod
    async def update_project(db: AsyncSession, project_id: int, project_data: ProjectUpdate) -> Optional[Project]:
        project = await ProjectService.get_project(db, project_id)
        if not project:
            return None

        update_data = project_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)

        await db.commit()
        await db.refresh(project)
        return project

    @staticmethod
    async def delete_project(db: AsyncSession, project_id: int) -> bool:
        project = await ProjectService.get_project(db, project_id)
        if not project:
            return False

        await db.delete(project)
        await db.commit()
        return True

    @staticmethod
    async def search_across_projects(db: AsyncSession, query: str) -> List[dict]:
        from app.models.task import Task

        result = await db.execute(
            select(Task, Project)
            .join(Project, Task.project_id == Project.id)
            .where(
                Task.title.ilike(f"%{query}%") | Task.description.ilike(f"%{query}%")
            )
            .order_by(Task.created_at.desc())
        )

        results = []
        for task, project in result.all():
            results.append({
                "task": task.to_dict(),
                "project": project.to_dict(),
            })
        return results