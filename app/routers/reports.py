from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.report_service import ReportService

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/summary")
async def get_summary(db: AsyncSession = Depends(get_db)):
    return await ReportService.get_summary(db)


@router.get("/weekly")
async def get_weekly_report(db: AsyncSession = Depends(get_db)):
    return await ReportService.get_weekly_report(db)
