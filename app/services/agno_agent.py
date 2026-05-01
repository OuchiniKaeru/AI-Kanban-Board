"""Agno AI Agent for Kanban Board."""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat
from agno.models.anthropic import Claude

from app.config import get_settings
from app.tools.kanban_tools import (
    set_db_session,
    search_tasks,
    get_task_by_id,
    create_task,
    update_task,
    delete_task,
    move_task,
    get_columns,
    get_projects,
    create_project,
    update_project,
    delete_project,
    generate_summary_report,
    generate_weekly_report,
    get_overdue_tasks,
    search_across_projects,
)


class KanbanAgnoAgent:
    def __init__(self):
        self.settings = get_settings()
        self._agent: Optional[Agent] = None

    def _get_model(self):
        if self.settings.openai_api_key and not self.settings.openai_api_key.startswith("your_"):
            return OpenAIChat(id=self.settings.openai_model, api_key=self.settings.openai_api_key)
        elif self.settings.anthropic_api_key and not self.settings.anthropic_api_key.startswith("your_"):
            return Claude(id=self.settings.anthropic_model, api_key=self.settings.anthropic_api_key)
        elif self.settings.gemini_api_key and not self.settings.gemini_api_key.startswith("your_"):
            from agno.models.google import Gemini
            return Gemini(id=self.settings.gemini_model, api_key=self.settings.gemini_api_key)
        elif self.settings.openrouter_api_key and not self.settings.openrouter_api_key.startswith("your_"):
            return OpenAIChat(
                id=self.settings.openrouter_model,
                api_key=self.settings.openrouter_api_key,
                base_url="https://openrouter.ai/api/v1",
            )
        else:
            raise ValueError("No valid AI API key configured.")

    def _create_agent(self) -> Agent:
        model = self._get_model()
        return Agent(
            name="Kanban AI Assistant",
            model=model,
            tools=[
                search_tasks, get_task_by_id, create_task, update_task,
                delete_task, move_task, get_columns, get_projects,
                create_project, update_project, delete_project,
                generate_summary_report, generate_weekly_report,
                get_overdue_tasks, search_across_projects,
            ],
            instructions=[
                "あなたはカンバンボード管理のAIアシスタントです。",
                "ユーザーの自然言語の指示を解析し、適切なツールを使用してタスク管理を支援してください。",
                "タスクの検索、作成、更新、削除、移動、レポート生成ができます。",
                "プロジェクト単位で管理されており、横断検索も可能です。",
                "カラム名は 'ToDo', 'Doing', 'Done' などがあります。",
                "回答は日本語で、親切で分かりやすく説明してください。",
                "タスク一覧を表示する際は、ID、タイトル、優先度、期限を含めてください。",
                "操作が成功した場合は確認メッセージを、失敗した場合はエラー内容を伝えてください。",
                "定期実行の場合は、実行結果を簡潔にまとめてください。",
            ],
            description="AI assistant for managing kanban board tasks and projects",
            db=SqliteDb(db_file="./kanban_agent.db"),
            add_history_to_context=True,
            num_history_runs=5,
            add_datetime_to_context=True,
            markdown=True,
            tool_call_limit=20,
        )

    async def process_message(self, db: AsyncSession, message: str, session_id: Optional[str] = None) -> dict:
        set_db_session(db)
        if self._agent is None:
            self._agent = self._create_agent()
        response = await self._agent.arun(message, session_id=session_id or "default")
        return {"message": response.content, "session_id": response.session_id, "run_id": response.run_id}