"""MCP Server for Kanban Board - exposes tools to external AI agents."""

import json
from mcp.server import Server
from mcp.types import TextContent, Tool
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.services.project_service import ProjectService
from app.services.column_service import ColumnService
from app.services.task_service import TaskService
from app.services.report_service import ReportService
from app.services.schedule_service import ScheduleService
from app.schemas.task import TaskCreate, TaskUpdate

mcp_server = Server("kanban-board")


@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(name="search_tasks", description="Search tasks across projects", inputSchema={"type": "object", "properties": {"project_id": {"type": "integer"}, "column_name": {"type": "string"}, "priority": {"type": "string", "enum": ["low", "medium", "high"]}, "query": {"type": "string"}}}),
        Tool(name="get_task", description="Get task details", inputSchema={"type": "object", "properties": {"task_id": {"type": "integer"}}, "required": ["task_id"]}),
        Tool(name="create_task", description="Create a new task", inputSchema={"type": "object", "properties": {"title": {"type": "string"}, "project_id": {"type": "integer"}, "column_name": {"type": "string", "default": "ToDo"}, "description": {"type": "string"}, "priority": {"type": "string", "enum": ["low", "medium", "high"], "default": "medium"}, "due_date": {"type": "string"}}, "required": ["title", "project_id"]}),
        Tool(name="update_task", description="Update a task", inputSchema={"type": "object", "properties": {"task_id": {"type": "integer"}, "title": {"type": "string"}, "description": {"type": "string"}, "priority": {"type": "string"}, "due_date": {"type": "string"}}, "required": ["task_id"]}),
        Tool(name="delete_task", description="Delete a task", inputSchema={"type": "object", "properties": {"task_id": {"type": "integer"}}, "required": ["task_id"]}),
        Tool(name="move_task", description="Move task to column", inputSchema={"type": "object", "properties": {"task_id": {"type": "integer"}, "column_name": {"type": "string"}}, "required": ["task_id", "column_name"]}),
        Tool(name="get_projects", description="Get all projects", inputSchema={"type": "object", "properties": {}}),
        Tool(name="get_columns", description="Get columns for a project", inputSchema={"type": "object", "properties": {"project_id": {"type": "integer"}}, "required": ["project_id"]}),
        Tool(name="generate_report", description="Generate report", inputSchema={"type": "object", "properties": {"project_id": {"type": "integer"}, "report_type": {"type": "string", "enum": ["summary", "weekly"], "default": "summary"}}}),
        Tool(name="get_overdue_tasks", description="Get overdue tasks", inputSchema={"type": "object", "properties": {"project_id": {"type": "integer"}}}),
        Tool(name="create_project", description="Create a new project", inputSchema={"type": "object", "properties": {"name": {"type": "string"}, "description": {"type": "string"}, "color": {"type": "string"}}, "required": ["name"]}),
        Tool(name="update_project", description="Update a project", inputSchema={"type": "object", "properties": {"project_id": {"type": "integer"}, "name": {"type": "string"}, "description": {"type": "string"}, "color": {"type": "string"}}, "required": ["project_id"]}),
        Tool(name="delete_project", description="Delete a project", inputSchema={"type": "object", "properties": {"project_id": {"type": "integer"}}, "required": ["project_id"]}),
        Tool(name="create_schedule", description="Create scheduled command", inputSchema={"type": "object", "properties": {"name": {"type": "string"}, "command": {"type": "string"}, "project_id": {"type": "integer"}, "schedule_type": {"type": "string", "enum": ["interval", "cron"]}, "interval_minutes": {"type": "integer"}, "cron_expression": {"type": "string"}}, "required": ["name", "command", "schedule_type"]}),
        Tool(name="list_schedules", description="List schedules", inputSchema={"type": "object", "properties": {}}),
    ]


@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    async with AsyncSessionLocal() as db:
        try:
            handlers = {
                "search_tasks": _search_tasks,
                "get_task": _get_task,
                "create_task": _create_task,
                "update_task": _update_task,
                "delete_task": _delete_task,
                "move_task": _move_task,
                "get_projects": _get_projects,
                "get_columns": _get_columns,
                "generate_report": _generate_report,
                "get_overdue_tasks": _get_overdue_tasks,
                "create_project": _create_project,
                "update_project": _update_project,
                "delete_project": _delete_project,
                "create_schedule": _create_schedule,
                "list_schedules": _list_schedules,
            }
            handler = handlers.get(name)
            if handler:
                return await handler(db, arguments)
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]


async def _search_tasks(db: AsyncSession, args: dict) -> list[TextContent]:
    column_name = args.get("column_name")
    priority = args.get("priority")
    query = args.get("query")
    column_id = None
    if column_name:
        columns = await ColumnService.get_columns(db)
        for col in columns:
            if col.name.lower() == column_name.lower():
                column_id = col.id
                break
    tasks = await TaskService.get_tasks(db, column_id=column_id, priority=priority, search=query)
    if not tasks:
        return [TextContent(type="text", text="該当するタスクは見つかりませんでした。")]
    lines = [f"タスク一覧（{len(tasks)}件）:"]
    for task in tasks:
        due = f"、期限: {task.due_date}" if task.due_date else ""
        lines.append(f"- ID {task.id}: {task.title} (優先度: {task.priority}{due})")
    return [TextContent(type="text", text="\n".join(lines))]


async def _get_task(db: AsyncSession, args: dict) -> list[TextContent]:
    task = await TaskService.get_task(db, args["task_id"])
    if not task:
        return [TextContent(type="text", text=f"ID {args['task_id']} のタスクは見つかりません。")]
    lines = [f"タスク詳細 (ID: {task.id}):", f"タイトル: {task.title}", f"説明: {task.description or 'なし'}", f"優先度: {task.priority}", f"期限: {task.due_date or 'なし'}"]
    return [TextContent(type="text", text="\n".join(lines))]


async def _create_task(db: AsyncSession, args: dict) -> list[TextContent]:
    column_id = None
    if args.get("column_name"):
        columns = await ColumnService.get_columns(db)
        for col in columns:
            if col.name.lower() == args["column_name"].lower():
                column_id = col.id
                break
    task_data = TaskCreate(title=args["title"], description=args.get("description"), column_id=column_id, project_id=args["project_id"], priority=args.get("priority", "medium"), due_date=args.get("due_date"))
    task = await TaskService.create_task(db, task_data)
    return [TextContent(type="text", text=f"タスクを作成しました: {task.title} (ID: {task.id})")]


async def _update_task(db: AsyncSession, args: dict) -> list[TextContent]:
    task_id = args.pop("task_id")
    update_data = {k: v for k, v in args.items() if v is not None}
    if not update_data:
        return [TextContent(type="text", text="更新する項目が指定されていません。")]
    task_data = TaskUpdate(**update_data)
    task = await TaskService.update_task(db, task_id, task_data)
    if not task:
        return [TextContent(type="text", text=f"ID {task_id} のタスクは見つかりません。")]
    return [TextContent(type="text", text=f"タスクを更新しました: {task.title}")]


async def _delete_task(db: AsyncSession, args: dict) -> list[TextContent]:
    success = await TaskService.delete_task(db, args["task_id"])
    if success:
        return [TextContent(type="text", text=f"ID {args['task_id']} のタスクを削除しました。")]
    return [TextContent(type="text", text=f"ID {args['task_id']} のタスクは見つかりません。")]


async def _move_task(db: AsyncSession, args: dict) -> list[TextContent]:
    columns = await ColumnService.get_columns(db)
    column_id = None
    for col in columns:
        if col.name.lower() == args["column_name"].lower():
            column_id = col.id
            break
    if not column_id:
        return [TextContent(type="text", text=f"カラム '{args['column_name']}' が見つかりません。")]
    task = await TaskService.move_task(db, args["task_id"], column_id, 0)
    if not task:
        return [TextContent(type="text", text=f"ID {args['task_id']} のタスクは見つかりません。")]
    return [TextContent(type="text", text=f"タスク '{task.title}' を {args['column_name']} に移動しました。")]


async def _get_projects(db: AsyncSession) -> list[TextContent]:
    projects = await ProjectService.get_projects(db)
    if not projects:
        return [TextContent(type="text", text="プロジェクトが登録されていません。")]
    lines = ["プロジェクト一覧:"]
    for p in projects:
        lines.append(f"- ID {p.id}: {p.name}")
    return [TextContent(type="text", text="\n".join(lines))]


async def _get_columns(db: AsyncSession, args: dict) -> list[TextContent]:
    columns = await ColumnService.get_columns(db)
    lines = ["カラム一覧:"]
    for col in columns:
        lines.append(f"- ID {col.id}: {col.name}")
    return [TextContent(type="text", text="\n".join(lines))]


async def _generate_report(db: AsyncSession, args: dict) -> list[TextContent]:
    report_type = args.get("report_type", "summary")
    if report_type == "summary":
        report = await ReportService.get_summary(db)
    else:
        report = await ReportService.get_weekly_report(db)
    return [TextContent(type="text", text=json.dumps(report, ensure_ascii=False, indent=2))]


async def _get_overdue_tasks(db: AsyncSession, args: dict) -> list[TextContent]:
    tasks = await TaskService.get_overdue_tasks(db)
    if not tasks:
        return [TextContent(type="text", text="期限切れのタスクはありません。")]
    lines = [f"期限切れタスク一覧（{len(tasks)}件）:"]
    for task in tasks:
        lines.append(f"- ID {task.id}: {task.title} (期限: {task.due_date})")
    return [TextContent(type="text", text="\n".join(lines))]


async def _create_project(db: AsyncSession, args: dict) -> list[TextContent]:
    from app.schemas.project import ProjectCreate
    project_data = ProjectCreate(name=args["name"], description=args.get("description"), color=args.get("color", "#3B82F6"))
    project = await ProjectService.create_project(db, project_data)
    return [TextContent(type="text", text=f"プロジェクトを作成しました: {project.name} (ID: {project.id})")]


async def _update_project(db: AsyncSession, args: dict) -> list[TextContent]:
    from app.schemas.project import ProjectUpdate
    project_id = args.pop("project_id")
    update_data = {k: v for k, v in args.items() if v is not None}
    if not update_data:
        return [TextContent(type="text", text="更新する項目が指定されていません。")]
    project_data = ProjectUpdate(**update_data)
    project = await ProjectService.update_project(db, project_id, project_data)
    if not project:
        return [TextContent(type="text", text=f"ID {project_id} のプロジェクトは見つかりません。")]
    return [TextContent(type="text", text=f"プロジェクトを更新しました: {project.name}")]


async def _delete_project(db: AsyncSession, args: dict) -> list[TextContent]:
    success = await ProjectService.delete_project(db, args["project_id"])
    if success:
        return [TextContent(type="text", text=f"ID {args['project_id']} のプロジェクトを削除しました。")]
    return [TextContent(type="text", text=f"ID {args['project_id']} のプロジェクトは見つかりません。")]


async def _create_schedule(db: AsyncSession, args: dict) -> list[TextContent]:
    from app.schemas.schedule import ScheduleCreate
    schedule_data = ScheduleCreate(name=args["name"], command=args["command"], project_id=args.get("project_id"), schedule_type=args["schedule_type"], interval_minutes=args.get("interval_minutes"), cron_expression=args.get("cron_expression"))
    schedule = await ScheduleService.create_schedule(db, schedule_data)
    return [TextContent(type="text", text=f"スケジュールを作成しました: {schedule.name} (ID: {schedule.id})")]


async def _list_schedules(db: AsyncSession) -> list[TextContent]:
    schedules = await ScheduleService.get_schedules(db)
    if not schedules:
        return [TextContent(type="text", text="スケジュールは登録されていません。")]
    lines = ["スケジュール一覧:"]
    for s in schedules:
        status = "有効" if s.is_enabled else "無効"
        lines.append(f"- ID {s.id}: {s.name} ({status}, {s.schedule_type})")
    return [TextContent(type="text", text="\n".join(lines))]