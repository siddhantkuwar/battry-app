from fastapi import APIRouter

from ..api.logs import LOGS_DB
from ..schemas.report import WeeklyReportResponse
from ..services.report_service import build_weekly_report


router = APIRouter(tags=["reports"])


@router.get("/report/weekly", response_model=WeeklyReportResponse)
async def get_weekly_report(user_id: str) -> WeeklyReportResponse:
    return WeeklyReportResponse(**build_weekly_report(LOGS_DB, user_id))
