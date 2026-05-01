from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List
from app.models.chat import ChatMessage


class ChatService:
    @staticmethod
    async def get_history(db: AsyncSession, limit: int = 10) -> List[ChatMessage]:
        result = await db.execute(
            select(ChatMessage).order_by(desc(ChatMessage.created_at)).limit(limit)
        )
        messages = result.scalars().all()
        return list(reversed(messages))
    
    @staticmethod
    async def add_message(db: AsyncSession, role: str, content: str) -> ChatMessage:
        message = ChatMessage(role=role, content=content)
        db.add(message)
        await db.commit()
        await db.refresh(message)
        return message
    
    @staticmethod
    async def clear_history(db: AsyncSession) -> None:
        from sqlalchemy import delete
        await db.execute(delete(ChatMessage))
        await db.commit()
