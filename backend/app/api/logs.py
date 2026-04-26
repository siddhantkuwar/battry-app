from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from ..schemas.log import LogEntry, LogRequest, LogResponse, ParsedTask
from ..services.battery_service import (
    DEFAULT_BATTERY,
    calculate_battery_after,
    get_previous_battery_for_user,
)
from ..services.log_repository import (
    LOGS_DB,
    create_log as save_log,
    get_latest_battery_for_user,
    is_persistent_store_enabled,
    list_logs,
)
from ..services.parser_service import normalize_log_text, parse_log_text


router = APIRouter(tags=["logs"])


@router.get("/logs", response_model=list[LogEntry])
async def get_logs(user_id: Annotated[str, Query(min_length=1)]) -> list[LogEntry]:
    return [LogEntry(**log) for log in list_logs(user_id)]


@router.post("/logs", response_model=LogResponse)
async def create_log(log_request: LogRequest) -> LogResponse:
    normalized_text = normalize_log_text(log_request.text)
    if not normalized_text:
        raise HTTPException(status_code=400, detail="Log text cannot be empty.")

    parsed_tasks = [ParsedTask(**task) for task in parse_log_text(normalized_text)]
    if is_persistent_store_enabled():
        battery_before = get_latest_battery_for_user(log_request.user_id) or DEFAULT_BATTERY
    else:
        battery_before = get_previous_battery_for_user(LOGS_DB, log_request.user_id)
    battery_after = calculate_battery_after(battery_before, parsed_tasks)
    log = save_log(
        user_id=log_request.user_id,
        text=log_request.text,
        normalized_text=normalized_text,
        logged_at=log_request.logged_at,
        parsed_tasks=parsed_tasks,
        battery_before=battery_before,
        battery_after=battery_after,
    )

    return LogResponse(
        log_id=str(log["log_id"]),
        parsed_tasks=parsed_tasks,
        battery_before=battery_before,
        battery_after=battery_after,
    )
