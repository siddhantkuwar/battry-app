from typing import Annotated

from fastapi import APIRouter, Depends

from ..core.auth import AuthenticatedUser, get_current_user
from ..schemas.report import WeeklyReportResponse
from ..services.log_repository import list_logs
from ..services.report_service import build_weekly_report


router = APIRouter(tags=["reports"])


@router.get("/report/weekly", response_model=WeeklyReportResponse)
async def get_weekly_report(
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> WeeklyReportResponse:
    user_logs = list_logs(current_user.id)
    return WeeklyReportResponse(**build_weekly_report(user_logs, current_user.id))
