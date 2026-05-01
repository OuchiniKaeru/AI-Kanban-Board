from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.schemas.chat import ChatMessageResponse
from app.services.chat_service import ChatService

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.get("/history", response_model=List[ChatMessageResponse])
async def get_chat_history(db: AsyncSession = Depends(get_db)):
    messages = await ChatService.get_history(db)
    return messages


@router.delete("/history")
async def clear_chat_history(db: AsyncSession = Depends(get_db)):
    await ChatService.clear_history(db)
    return {"message": "Chat history cleared"}
