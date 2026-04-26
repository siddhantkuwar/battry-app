from typing import Annotated

from fastapi import APIRouter
from fastapi import Query

from ..schemas.report import WeeklyReportResponse
from ..services.log_repository import list_logs
from ..services.report_service import build_weekly_report


router = APIRouter(tags=["reports"])


@router.get("/report/weekly", response_model=WeeklyReportResponse)
async def get_weekly_report(
    user_id: Annotated[str, Query(min_length=1)],
) -> WeeklyReportResponse:
    return WeeklyReportResponse(**build_weekly_report(list_logs(user_id), user_id))
