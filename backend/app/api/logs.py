from uuid import uuid4

from fastapi import APIRouter, HTTPException

from ..schemas.log import LogRequest, LogResponse, ParsedTask
from ..services.parser_service import normalize_log_text, parse_log_text


router = APIRouter(tags=["logs"])

LOGS_DB = []
DEFAULT_BATTERY = 50
BATTERY_STEP = 10


def get_latest_battery_for_user(user_id: str) -> int:
    for log in reversed(LOGS_DB):
        if log["user_id"] == user_id:
            return log["battery_after"]
    return DEFAULT_BATTERY


def compute_battery_after(battery_before: int, parsed_tasks: list[ParsedTask]) -> int:
    battery_delta = 0

    for task in parsed_tasks:
        if task.direction == "up":
            battery_delta += BATTERY_STEP
        elif task.direction == "down":
            battery_delta -= BATTERY_STEP

    return max(0, min(100, battery_before + battery_delta))


@router.post("/logs", response_model=LogResponse)
async def create_log(log_request: LogRequest) -> LogResponse:
    normalized_text = normalize_log_text(log_request.text)
    if not normalized_text:
        raise HTTPException(status_code=400, detail="Log text cannot be empty.")

    parsed_tasks = [ParsedTask(**task) for task in parse_log_text(normalized_text)]
    battery_before = get_latest_battery_for_user(log_request.user_id)
    battery_after = compute_battery_after(battery_before, parsed_tasks)
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
