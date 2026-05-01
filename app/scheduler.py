"""APScheduler-based scheduler for periodic command execution."""

import asyncio
import os
import time
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

from app.database import AsyncSessionLocal
from app.services.schedule_service import ScheduleService
from app.services.task_service import TaskService
from app.services.agno_agent import KanbanAgnoAgent


class KanbanScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self._job_map = {}

    def start(self):
        self.scheduler.start()

    def shutdown(self):
        self.scheduler.shutdown()

    async def load_schedules(self):
        async with AsyncSessionLocal() as db:
            schedules = await ScheduleService.get_schedules(db)
            for schedule in schedules:
                if schedule.is_enabled:
                    self.add_job(schedule)

    def add_job(self, schedule):
        if schedule.schedule_type == "interval":
            minutes = schedule.interval_minutes or 60
            trigger = IntervalTrigger(minutes=minutes)
        elif schedule.schedule_type == "cron":
            trigger = CronTrigger.from_crontab(schedule.cron_expression or "0 0 * * *")
        else:
            return
        job_id = f"schedule_{schedule.id}"
        self.scheduler.add_job(
            self._execute_command,
            trigger=trigger,
            id=job_id,
            replace_existing=True,
            args=[schedule.id, schedule.command, schedule.project_id, schedule.task_id],
        )
        self._job_map[schedule.id] = job_id

    def remove_job(self, schedule_id: int):
        job_id = self._job_map.get(schedule_id)
        if job_id:
            self.scheduler.remove_job(job_id)
            del self._job_map[schedule_id]

    async def _execute_command(
        self,
        schedule_id: int,
        command: str,
        project_id: Optional[int],
        task_id: Optional[int]
    ):
        async with AsyncSessionLocal() as db:
            schedule = await ScheduleService.get_schedule(db, schedule_id)
            if not schedule:
                return

            start_time = time.time()
            try:
                if schedule.command_type == "shell":
                    result = await self._execute_shell_command(db, schedule, command)
                else:
                    result = await self._execute_agent_command(db, schedule, command, project_id)
                status = "success"
            except asyncio.TimeoutError:
                result = "Execution timed out after 60 seconds"
                status = "timeout"
            except Exception as e:
                result = str(e)
                status = "error"

            execution_time = time.time() - start_time

            # Record log
            await ScheduleService.add_log(db, schedule_id, status, result, execution_time)

            # Append to task description if enabled
            if schedule.append_to_task_description and task_id:
                await TaskService.append_schedule_result(
                    db, task_id, schedule.name, status, result, execution_time
                )

            await ScheduleService.update_last_run(db, schedule_id, status, result)

    async def _execute_shell_command(self, db, schedule, command: str) -> str:
        resources = await ScheduleService.get_resources(db, schedule.id)

        # Expand placeholders
        for i, res in enumerate(resources, 1):
            command = command.replace(f"{{resource_{i}}}", res.path)

        # Set environment variable with all paths
        env = os.environ.copy()
        env["KANBAN_RESOURCE_PATHS"] = ",".join([r.path for r in resources])

        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
        )
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=60.0)
        except asyncio.TimeoutError:
            proc.kill()
            raise

        output = (stdout + stderr).decode("utf-8", errors="replace")[:10000]
        return output

    async def _execute_agent_command(self, db, schedule, command: str, project_id: Optional[int]) -> str:
        agent = KanbanAgnoAgent()
        context = f"[定期実行] スケジュールID: {schedule.id}\n\n{command}"
        if project_id:
            context += f"\n\n対象プロジェクトID: {project_id}"

        resources = await ScheduleService.get_resources(db, schedule.id)
        if resources:
            context += "\n\n登録リソース:\n"
            for i, res in enumerate(resources, 1):
                context += f"  {i}. [{res.resource_type}] {res.path}\n"

        result = await agent.process_message(
            db, context, session_id=f"schedule-{schedule.id}"
        )
        return result.get("message", "")


kanban_scheduler = KanbanScheduler()
