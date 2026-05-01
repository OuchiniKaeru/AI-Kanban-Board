from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader
from contextlib import asynccontextmanager

from app.database import init_db
from app.routers import columns, tasks, chat, reports, agent, htmx, projects, schedules
from app.scheduler import kanban_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await kanban_scheduler.load_schedules()
    yield
    await kanban_scheduler.stop()


app = FastAPI(title="AI Kanban Board", lifespan=lifespan)

# Static files and templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
jinja_env = Environment(loader=FileSystemLoader("app/templates"), enable_async=True)

# Include routers
app.include_router(columns.router)
app.include_router(tasks.router)
app.include_router(chat.router)
app.include_router(reports.router)
app.include_router(agent.router)
app.include_router(htmx.router)
app.include_router(projects.router)
app.include_router(schedules.router)


@app.get("/")
async def root():
    return {"message": "AI Kanban Board API"}


@app.get("/board", response_class=HTMLResponse)
async def board_page(request: Request):
    template = jinja_env.get_template("board.html")
    html = await template.render_async(request=request)
    return HTMLResponse(content=html)

