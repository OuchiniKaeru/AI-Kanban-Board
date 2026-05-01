from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.schemas.column import ColumnCreate, ColumnUpdate, ColumnResponse
from app.services.column_service import ColumnService

router = APIRouter(prefix="/api/columns", tags=["columns"])


@router.get("", response_model=List[ColumnResponse])
async def list_columns(db: AsyncSession = Depends(get_db)):
    columns = await ColumnService.get_columns(db)
    return columns


@router.post("", response_model=ColumnResponse)
async def create_column(column: ColumnCreate, db: AsyncSession = Depends(get_db)):
    return await ColumnService.create_column(db, column)


@router.get("/{column_id}", response_model=ColumnResponse)
async def get_column(column_id: int, db: AsyncSession = Depends(get_db)):
    column = await ColumnService.get_column(db, column_id)
    if not column:
        raise HTTPException(status_code=404, detail="Column not found")
    return column


@router.put("/{column_id}", response_model=ColumnResponse)
async def update_column(column_id: int, column: ColumnUpdate, db: AsyncSession = Depends(get_db)):
    updated = await ColumnService.update_column(db, column_id, column)
    if not updated:
        raise HTTPException(status_code=404, detail="Column not found")
    return updated


@router.delete("/{column_id}")
async def delete_column(column_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await ColumnService.delete_column(db, column_id)
    if not deleted:
        raise HTTPException(status_code=400, detail="Column not found or not empty")
    return {"message": "Column deleted successfully"}
