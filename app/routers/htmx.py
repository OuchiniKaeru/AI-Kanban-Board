from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import date

from app.database import get_db
from app.services.column_service import ColumnService
from app.services.task_service import TaskService
from app.models.column import KanbanColumn
from sqlalchemy import select

router = APIRouter(prefix="/htmx", tags=["htmx"])
jinja_env = Environment(loader=FileSystemLoader("app/templates"), enable_async=True, cache_size=0)


@router.get("/board", response_class=HTMLResponse)
async def board_htmx(request: Request, project_id: Optional[int] = None, db: AsyncSession = Depends(get_db)):
    print(f"project_id: {project_id}")
    if project_id is not None:
        # プロジェクト選択時: そのプロジェクトのカラムとタスクのみ表示
        columns = await ColumnService.get_columns(db, project_id=project_id)
        
        # 全カラムを取得（名前マップ用）
        all_columns_result = await db.execute(select(KanbanColumn))
        all_columns = all_columns_result.scalars().all()
        column_map = {col.id: col.name for col in all_columns}
        
        # このプロジェクトの全タスクを取得
        all_tasks = await TaskService.get_tasks(db, project_id=project_id)
        
        columns_data = []
        for col in columns:
            # このカラム名と同じ名前の全カラムのタスクを集める
            # （タスクのcolumn_idがデフォルトカラムを指していても表示される）
            same_name_ids = [c.id for c in all_columns if c.name == col.name]
            tasks = [t for t in all_tasks if t.column_id in same_name_ids]
            col_dict = col.to_dict()
            col_dict["tasks"] = [task.to_dict() for task in tasks]
            columns_data.append(col_dict)
    else:
        # print("すべて")
        # # 「すべて」選択時: デフォルトカラムを表示し、全プロジェクトのタスクをカラム名でグループ化
        # columns = await ColumnService.get_columns(db, project_id=None)
        # print(columns)
        
        # # 全カラムを取得してID→名前のマップを作成
        # all_columns_result = await db.execute(select(KanbanColumn))
        # all_columns = all_columns_result.scalars().all()
        # column_map = {col.id: col.name for col in all_columns}
        
        # # 全タスク取得
        # all_tasks = await TaskService.get_tasks(db)
        
        # columns_data = []
        # for col in columns:
        #     # このカラム名と同じ名前の全カラムのタスクを集める
        #     tasks = [t for t in all_tasks if column_map.get(t.column_id) == col.name]
        #     col_dict = col.to_dict()
        #     col_dict["tasks"] = [task.to_dict() for task in tasks]
        #     columns_data.append(col_dict)

        print("すべて")
        # 全カラムを取得
        all_columns_result = await db.execute(select(KanbanColumn).order_by(KanbanColumn.order_index))
        all_columns = all_columns_result.scalars().all()

        # 名前ごとに代表カラムを1つだけ残す（重複除去）
        seen_names = set()
        columns = []
        for col in all_columns:
            if col.name not in seen_names:
                seen_names.add(col.name)
                columns.append(col)

        # ID→名前マップ
        column_map = {col.id: col.name for col in all_columns}

        # 全タスク取得
        all_tasks = await TaskService.get_tasks(db)

        columns_data = []
        for col in columns:
            tasks = [t for t in all_tasks if column_map.get(t.column_id) == col.name]
            col_dict = col.to_dict()
            col_dict["tasks"] = [task.to_dict() for task in tasks]
            columns_data.append(col_dict)
    
    template = jinja_env.get_template("components/board_content.html")
    html = await template.render_async(request=request, columns=columns_data, today=date.today())
    # ブラウザキャッシュを無効化
    return HTMLResponse(
        content=html,
        headers={"Cache-Control": "no-store"}
    )
