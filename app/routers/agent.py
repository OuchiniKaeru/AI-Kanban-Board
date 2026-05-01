"""Agent router - Agno version with schedule support."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse, ScheduleExecuteRequest
from app.services.agno_agent import KanbanAgnoAgent
from app.services.chat_service import ChatService
from app.services.schedule_service import ScheduleService

router = APIRouter(prefix="/api/agent", tags=["agent"])

_kanban_agent: KanbanAgnoAgent | None = None


def get_kanban_agent() -> KanbanAgnoAgent:
    global _kanban_agent
    if _kanban_agent is None:
        _kanban_agent = KanbanAgnoAgent()
    return _kanban_agent


@router.post("/process", response_model=ChatResponse)
async def process_message(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    await ChatService.add_message(db, "user", request.message)
    agent = get_kanban_agent()
    result = await agent.process_message(
        db=db,
        message=request.message,
        session_id=getattr(request, "session_id", None),
    )
    await ChatService.add_message(db, "assistant", result["message"])
    return ChatResponse(success=True, message=result["message"], actions=None, requires_confirmation=False)


@router.post("/schedule", response_model=ChatResponse)
async def execute_scheduled_command(request: ScheduleExecuteRequest, db: AsyncSession = Depends(get_db)):
    agent = get_kanban_agent()
    context = f"[定期実行] {request.schedule_name}\n\n{request.command}"
    if request.project_id:
        context += f"\n\n対象プロジェクトID: {request.project_id}"
    result = await agent.process_message(db=db, message=context, session_id=f"schedule-{request.schedule_id}")
    await ScheduleService.update_last_run(db, request.schedule_id, "success", result["message"])
    return ChatResponse(success=True, message=result["message"], actions=None, requires_confirmation=False)


@router.post("/schedule/{schedule_id}/run")
async def run_schedule_via_agent(schedule_id: int, db: AsyncSession = Depends(get_db)):
    schedule = await ScheduleService.get_schedule(db, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    request = ScheduleExecuteRequest(
        schedule_id=schedule.id,
        schedule_name=schedule.name,
        command=schedule.command,
        project_id=schedule.project_id,
    )
    return await execute_scheduled_command(request, db)