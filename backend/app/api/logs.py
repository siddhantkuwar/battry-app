from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from ..core.auth import AuthenticatedUser, get_current_user
from ..core.rate_limit import check_log_submission_rate_limit
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
async def get_logs(
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> list[LogEntry]:
    """List the signed-in user's logs in the API response shape."""
    return [LogEntry(**log) for log in list_logs(current_user.id)]


@router.post("/logs", response_model=LogResponse)
async def create_log(
    log_request: LogRequest,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
) -> LogResponse:
    """Create one daily log and return the battery change it caused.

    Flow in plain English:
    0. Rate-limit the anonymous device.
    1. Clean the user's raw text.
    2. Parse known energy events out of that text.
    3. Start from the user's previous battery score.
    4. Save the log.
    5. Return only the fields the mobile submit screen needs immediately.
    """
    rate_limit = check_log_submission_rate_limit(current_user.id)
    if not rate_limit.is_allowed:
        raise HTTPException(
            status_code=429,
            detail="Too many logs submitted. Try again soon.",
            headers={"Retry-After": str(rate_limit.retry_after_seconds)},
        )

    normalized_text = normalize_log_text(log_request.text)
    if not normalized_text:
        raise HTTPException(status_code=400, detail="Log text cannot be empty.")

    parsed_tasks = [ParsedTask(**task) for task in parse_log_text(normalized_text)]

    # The database path asks Postgres for the latest score. The fallback path
    # uses the in-memory list so the app still works before infrastructure is
    # configured.
    if is_persistent_store_enabled():
        battery_before = get_latest_battery_for_user(current_user.id) or DEFAULT_BATTERY
    else:
        battery_before = get_previous_battery_for_user(LOGS_DB, current_user.id)
    battery_after = calculate_battery_after(battery_before, parsed_tasks)
    log = save_log(
        user_id=current_user.id,
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
