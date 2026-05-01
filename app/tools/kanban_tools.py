"""Kanban board tools for Agno AI Agent."""

from typing import Optional
from agno.tools.decorator import tool

from app.services.task_service import TaskService
from app.services.column_service import ColumnService
from app.services.project_service import ProjectService
from app.services.report_service import ReportService
from app.schemas.task import TaskCreate, TaskUpdate
from app.schemas.project import ProjectCreate, ProjectUpdate
from sqlalchemy.ext.asyncio import AsyncSession

_db_session: Optional[AsyncSession] = None


def set_db_session(db: AsyncSession):
    global _db_session
    _db_session = db


def get_db_session() -> AsyncSession:
    if _db_session is None:
        raise RuntimeError("Database session not set.")
    return _db_session


@tool
async def get_projects() -> str:
    """Get the list of all projects."""
    db = get_db_session()
    projects = await ProjectService.get_projects(db)
    if not projects:
        return "プロジェクトが登録されていません。"
    lines = ["プロジェクト一覧:"]
    for p in projects:
        lines.append(f"- ID {p.id}: {p.name}")
    return "\n".join(lines)


@tool
async def search_tasks(
    project_id: Optional[int] = None,
    column_name: Optional[str] = None,
    priority: Optional[str] = None,
    query: Optional[str] = None,
) -> str:
    """Search for tasks. Filter by project, column, priority, or keyword."""
    db = get_db_session()
    column_id = None
    if column_name:
        columns = await ColumnService.get_columns(db)
        for col in columns:
            if col.name.lower() == column_name.lower():
                column_id = col.id
                break
    tasks = await TaskService.get_tasks(db, column_id=column_id, priority=priority, search=query)
    if not tasks:
        return "該当するタスクは見つかりませんでした。"
    lines = [f"タスク一覧（{len(tasks)}件）:"]
    for task in tasks:
        due = f"、期限: {task.due_date}" if task.due_date else ""
        lines.append(f"- ID {task.id}: {task.title} (優先度: {task.priority}{due})")
    return "\n".join(lines)


@tool
async def search_across_projects(query: str) -> str:
    """Search tasks across all projects."""
    db = get_db_session()
    results = await ProjectService.search_across_projects(db, query)
    if not results:
        return "該当するタスクは見つかりませんでした。"
    lines = [f"横断検索結果（{len(results)}件）:"]
    for r in results:
        task = r["task"]
        project = r["project"]
        lines.append(f"- ID {task['id']}: {task['title']} (プロジェクト: {project['name']})")
    return "\n".join(lines)


@tool
async def get_task_by_id(task_id: int) -> str:
    """Get detailed information about a specific task."""
    db = get_db_session()
    task = await TaskService.get_task(db, task_id)
    if not task:
        return f"ID {task_id} のタスクは見つかりません。"
    lines = [
        f"タスク詳細 (ID: {task.id}):",
        f"タイトル: {task.title}",
        f"説明: {task.description or 'なし'}",
        f"優先度: {task.priority}",
        f"期限: {task.due_date or 'なし'}",
    ]
    return "\n".join(lines)


@tool
async def create_task(
    title: str,
    project_id: int,
    column_name: str = "ToDo",
    description: Optional[str] = None,
    priority: str = "medium",
    due_date: Optional[str] = None,
) -> str:
    """Create a new task in the kanban board."""
    db = get_db_session()
    columns = await ColumnService.get_columns(db)
    column_id = None
    for col in columns:
        if col.name.lower() == column_name.lower():
            column_id = col.id
            break
    if column_id is None:
        return f"カラム '{column_name}' が見つかりません。"
    task_data = TaskCreate(
        title=title,
        description=description,
        column_id=column_id,
        project_id=project_id,
        priority=priority,
        due_date=due_date,
    )
    task = await TaskService.create_task(db, task_data)
    return f"タスクを作成しました: {task.title} (ID: {task.id})"


@tool
async def update_task(
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    priority: Optional[str] = None,
    due_date: Optional[str] = None,
) -> str:
    """Update an existing task."""
    db = get_db_session()
    update_data = {}
    if title is not None:
        update_data["title"] = title
    if description is not None:
        update_data["description"] = description
    if priority is not None:
        update_data["priority"] = priority
    if due_date is not None:
        update_data["due_date"] = due_date
    if not update_data:
        return "更新する項目が指定されていません。"
    task_data = TaskUpdate(**update_data)
    task = await TaskService.update_task(db, task_id, task_data)
    if not task:
        return f"ID {task_id} のタスクは見つかりません。"
    return f"タスクを更新しました: {task.title}"


@tool
async def delete_task(task_id: int) -> str:
    """Delete a task from the kanban board."""
    db = get_db_session()
    success = await TaskService.delete_task(db, task_id)
    if success:
        return f"ID {task_id} のタスクを削除しました。"
    return f"ID {task_id} のタスクは見つかりません。"


@tool
async def move_task(task_id: int, column_name: str) -> str:
    """Move a task to a different column."""
    db = get_db_session()
    columns = await ColumnService.get_columns(db)
    column_id = None
    for col in columns:
        if col.name.lower() == column_name.lower():
            column_id = col.id
            break
    if column_id is None:
        return f"カラム '{column_name}' が見つかりません。"
    task = await TaskService.move_task(db, task_id, column_id, 0)
    if not task:
        return f"ID {task_id} のタスクは見つかりません。"
    return f"タスク '{task.title}' を {column_name} に移動しました。"


@tool
async def get_columns() -> str:
    """Get the list of all columns in the kanban board."""
    db = get_db_session()
    columns = await ColumnService.get_columns(db)
    if not columns:
        return "カラムが登録されていません。"
    lines = ["カラム一覧:"]
    for col in columns:
        lines.append(f"- ID {col.id}: {col.name}")
    return "\n".join(lines)


@tool
async def generate_summary_report() -> str:
    """Generate a summary report of the kanban board."""
    db = get_db_session()
    report = await ReportService.get_summary(db)
    lines = [
        "=== サマリーレポート ===",
        f"総タスク数: {report['total_tasks']}",
        "",
        "【カラム別タスク数】",
    ]
    for col_name, count in report["column_stats"].items():
        lines.append(f"  {col_name}: {count}件")
    lines.extend(["", "【優先度別タスク数】"])
    for priority, count in report["priority_stats"].items():
        lines.append(f"  {priority}: {count}件")
    lines.extend(["", f"期限切れタスク: {report['overdue_count']}件", f"今週期限のタスク: {report['due_this_week']}件"])
    return "\n".join(lines)


@tool
async def generate_weekly_report() -> str:
    """Generate a weekly report."""
    db = get_db_session()
    report = await ReportService.get_weekly_report(db)
    lines = [
        "=== 週次レポート ===",
        f"対象期間: {report['week_start']} 〜 {report['week_end']}",
        f"今週作成されたタスク: {report['created_this_week']}件",
        f"今週完了したタスク: {report['completed_this_week']}件",
        "",
        "【サマリー】",
        f"  総タスク数: {report['summary']['total_tasks']}",
        f"  期限切れ: {report['summary']['overdue_count']}件",
    ]
    return "\n".join(lines)


@tool
async def create_project(name: str, description: Optional[str] = None, color: Optional[str] = "#3B82F6") -> str:
    """Create a new project."""
    db = get_db_session()
    project_data = ProjectCreate(name=name, description=description, color=color)
    project = await ProjectService.create_project(db, project_data)
    return f"プロジェクトを作成しました: {project.name} (ID: {project.id})"


@tool
async def update_project(project_id: int, name: Optional[str] = None, description: Optional[str] = None, color: Optional[str] = None) -> str:
    """Update an existing project."""
    db = get_db_session()
    update_data = {}
    if name is not None:
        update_data["name"] = name
    if description is not None:
        update_data["description"] = description
    if color is not None:
        update_data["color"] = color
    if not update_data:
        return "更新する項目が指定されていません。"
    project_data = ProjectUpdate(**update_data)
    project = await ProjectService.update_project(db, project_id, project_data)
    if not project:
        return f"ID {project_id} のプロジェクトは見つかりません。"
    return f"プロジェクトを更新しました: {project.name}"


@tool
async def delete_project(project_id: int) -> str:
    """Delete a project."""
    db = get_db_session()
    success = await ProjectService.delete_project(db, project_id)
    if success:
        return f"ID {project_id} のプロジェクトを削除しました。"
    return f"ID {project_id} のプロジェクトは見つかりません。"


@tool
async def get_overdue_tasks() -> str:
    """Get all overdue tasks."""
    db = get_db_session()
    tasks = await TaskService.get_overdue_tasks(db)
    if not tasks:
        return "期限切れのタスクはありません。"
    lines = [f"期限切れタスク一覧（{len(tasks)}件）:"]
    for task in tasks:
        lines.append(f"- ID {task.id}: {task.title} (期限: {task.due_date})")
    return "\n".join(lines)