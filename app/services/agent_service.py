import json
import httpx
from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.services.task_service import TaskService
from app.services.column_service import ColumnService
from app.services.report_service import ReportService
from app.schemas.task import TaskCreate, TaskUpdate


class AgentService:
    def __init__(self):
        self.settings = get_settings()
    
    async def process_message(self, db: AsyncSession, message: str) -> Dict:
        """Process a user message and return AI response with actions."""
        
        # Get current context
        columns = await ColumnService.get_columns(db)
        columns_info = [col.to_dict() for col in columns]
        
        # Build system prompt
        system_prompt = self._build_system_prompt(columns_info)
        
        # Call AI provider
        response_text = await self._call_llm(system_prompt, message)
        
        # Parse response and extract actions
        result = self._parse_response(response_text)
        
        # Execute actions if any
        if result.get("actions"):
            executed_actions = await self._execute_actions(db, result["actions"])
            result["executed_actions"] = executed_actions
        
        return result
    
    def _build_system_prompt(self, columns_info: List[Dict]) -> str:
        current_time = datetime.now().isoformat()
        
        columns_text = "\n".join([
            f"- ID {col['id']}: {col['name']}" 
            for col in columns_info
        ])
        
        return f"""あなたはカンバンボード管理のAIアシスタントです。
ユーザーの自然言語の指示を解析し、適切なタスク管理アクションを実行してください。

対応可能なアクション:
- create_task: タスク作成（title, description, column_id, priority, due_date）
- update_task: タスク更新（task_id, 任意のフィールド）
- delete_task: タスク削除（task_id）
- move_task: タスク移動（task_id, column_id）
- search_tasks: タスク検索（query, priority, column_id）
- generate_report: レポート生成（report_type: summary/weekly）

現在の日時: {current_time}
カラム情報:
{columns_text}

応答形式:
1. まずユーザーへの自然言語での返答を記述
2. 実行するアクションがあれば、以下のJSON形式で記述:
   ```json
   {{
     "actions": [
       {{"type": "create_task", "data": {{...}}}},
       {{"type": "update_task", "data": {{...}}}}
     ],
     "requires_confirmation": false
   }}
   ```
3. 削除などの破壊的操作では requires_confirmation: true に設定
"""
    
    def _is_valid_key(self, key: str) -> bool:
        """Check if API key is set and not a placeholder."""
        return bool(key) and not key.startswith("your_") and not key.endswith("_here")
    
    async def _call_llm(self, system_prompt: str, user_message: str) -> str:
        """Call the configured LLM provider."""
        if self._is_valid_key(self.settings.openai_api_key):
            return await self._call_openai(system_prompt, user_message)
        elif self._is_valid_key(self.settings.anthropic_api_key):
            return await self._call_anthropic(system_prompt, user_message)
        elif self._is_valid_key(self.settings.gemini_api_key):
            return await self._call_gemini(system_prompt, user_message)
        elif self._is_valid_key(self.settings.openrouter_api_key):
            return await self._call_openrouter(system_prompt, user_message)
        elif self.settings.ollama_base_url and self.settings.ollama_base_url != "http://localhost:11434":
            return await self._call_ollama(system_prompt, user_message)
        else:
            # Fallback to simple response without AI
            return self._fallback_response(user_message)
    
    async def _call_openai(self, system_prompt: str, user_message: str) -> str:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.settings.openai_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.settings.openai_model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_message}
                        ],
                        "temperature": 0.7
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            return f"申し訳ありません。AIサービスでエラーが発生しました: {str(e)}"
    
    async def _call_anthropic(self, system_prompt: str, user_message: str) -> str:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": self.settings.anthropic_api_key,
                        "Content-Type": "application/json",
                        "anthropic-version": "2023-06-01"
                    },
                    json={
                        "model": self.settings.anthropic_model,
                        "max_tokens": 1000,
                        "system": system_prompt,
                        "messages": [
                            {"role": "user", "content": user_message}
                        ]
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                return data["content"][0]["text"]
        except Exception as e:
            return f"申し訳ありません。AIサービスでエラーが発生しました: {str(e)}"
    
    async def _call_gemini(self, system_prompt: str, user_message: str) -> str:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/{self.settings.gemini_model}:generateContent",
                    params={"key": self.settings.gemini_api_key},
                    headers={"Content-Type": "application/json"},
                    json={
                        "contents": [
                            {
                                "role": "user",
                                "parts": [{"text": f"{system_prompt}\n\n{user_message}"}]
                            }
                        ],
                        "generationConfig": {
                            "temperature": 0.7
                        }
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            return f"申し訳ありません。AIサービスでエラーが発生しました: {str(e)}"
    
    async def _call_openrouter(self, system_prompt: str, user_message: str) -> str:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.settings.openrouter_api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "http://localhost:8000",
                        "X-Title": "AI Kanban Board"
                    },
                    json={
                        "model": self.settings.openrouter_model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_message}
                        ],
                        "temperature": 0.7
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            return f"申し訳ありません。AIサービスでエラーが発生しました: {str(e)}"
    
    async def _call_ollama(self, system_prompt: str, user_message: str) -> str:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.settings.ollama_base_url}/api/chat",
                    headers={"Content-Type": "application/json"},
                    json={
                        "model": self.settings.ollama_model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_message}
                        ],
                        "stream": False
                    },
                    timeout=60.0
                )
                response.raise_for_status()
                data = response.json()
                return data["message"]["content"]
        except Exception as e:
            return f"申し訳ありません。AIサービスでエラーが発生しました: {str(e)}"
    
    def _fallback_response(self, message: str) -> str:
        return f"""申し訳ありません。AI APIキーが設定されていないため、高度な自然言語処理は利用できません。

メッセージ「{message}」を受け取りました。

利用可能なコマンド:
- タスク作成: `/create タスク名` 
- タスク検索: `/search キーワード`
- レポート: `/report`

設定ファイル（.env）にOpenAI、Anthropic、Gemini、OpenRouter、またはOllamaのAPIキーを設定してください。"""
    
    def _parse_response(self, response_text: str) -> Dict:
        """Parse AI response text to extract actions."""
        result = {
            "message": response_text,
            "actions": [],
            "requires_confirmation": False
        }
        
        # Try to extract JSON block
        if "```json" in response_text:
            try:
                json_start = response_text.index("```json") + 7
                json_end = response_text.index("```", json_start)
                json_str = response_text[json_start:json_end].strip()
                data = json.loads(json_str)
                
                if "actions" in data:
                    result["actions"] = data["actions"]
                if "requires_confirmation" in data:
                    result["requires_confirmation"] = data["requires_confirmation"]
                
                # Remove JSON block from message
                result["message"] = response_text[:json_start - 7].strip()
            except (ValueError, json.JSONDecodeError):
                pass
        
        return result
    
    async def _execute_actions(self, db: AsyncSession, actions: List[Dict]) -> List[Dict]:
        """Execute the actions returned by AI."""
        executed = []
        
        for action in actions:
            action_type = action.get("type")
            data = action.get("data", {})
            
            try:
                if action_type == "create_task":
                    task_data = TaskCreate(**data)
                    task = await TaskService.create_task(db, task_data)
                    executed.append({"type": "create_task", "success": True, "task": task.to_dict()})
                
                elif action_type == "update_task":
                    task_id = data.pop("task_id", None)
                    if task_id:
                        task_data = TaskUpdate(**data)
                        task = await TaskService.update_task(db, task_id, task_data)
                        executed.append({"type": "update_task", "success": True, "task": task.to_dict() if task else None})
                
                elif action_type == "delete_task":
                    task_id = data.get("task_id")
                    if task_id:
                        success = await TaskService.delete_task(db, task_id)
                        executed.append({"type": "delete_task", "success": success})
                
                elif action_type == "move_task":
                    task_id = data.get("task_id")
                    column_id = data.get("column_id")
                    if task_id and column_id:
                        task = await TaskService.move_task(db, task_id, column_id, 0)
                        executed.append({"type": "move_task", "success": True, "task": task.to_dict() if task else None})
                
                else:
                    executed.append({"type": action_type, "success": False, "error": "Unknown action type"})
            
            except Exception as e:
                executed.append({"type": action_type, "success": False, "error": str(e)})
        
        return executed
