from uuid import uuid4

from fastapi import APIRouter, HTTPException

from ..schemas.log import LogEntry, LogRequest, LogResponse, ParsedTask
from ..services.battery_service import (
    calculate_battery_after,
    get_previous_battery_for_user,
)
from ..services.parser_service import normalize_log_text, parse_log_text


router = APIRouter(tags=["logs"])

LOGS_DB = []


@router.get("/logs", response_model=list[LogEntry])
async def get_logs(user_id: str | None = None) -> list[LogEntry]:
    logs = LOGS_DB
    if user_id is not None:
        logs = [log for log in LOGS_DB if log["user_id"] == user_id]

    return [LogEntry(**log) for log in logs]


@router.post("/logs", response_model=LogResponse)
async def create_log(log_request: LogRequest) -> LogResponse:
    normalized_text = normalize_log_text(log_request.text)
    if not normalized_text:
        raise HTTPException(status_code=400, detail="Log text cannot be empty.")

    parsed_tasks = [ParsedTask(**task) for task in parse_log_text(normalized_text)]
    battery_before = get_previous_battery_for_user(LOGS_DB, log_request.user_id)
    battery_after = calculate_battery_after(battery_before, parsed_tasks)
    log_id = str(uuid4())

    LOGS_DB.append(
        {
            "log_id": log_id,
            "user_id": log_request.user_id,
            "text": log_request.text,
            "normalized_text": normalized_text,
            "logged_at": log_request.logged_at,
            "parsed_tasks": [task.model_dump() for task in parsed_tasks],
            "battery_before": battery_before,
            "battery_after": battery_after,
        }
    )

    return LogResponse(
        log_id=log_id,
        parsed_tasks=parsed_tasks,
        battery_before=battery_before,
        battery_after=battery_after,
    )
