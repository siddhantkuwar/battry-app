from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class LogRequest(BaseModel):
    """Input body for creating a log from the mobile app."""

    text: str = Field(min_length=1, max_length=500)
    logged_at: datetime


class ParsedTask(BaseModel):
    """One detected energy event inside a free-text log."""

    label: str
    direction: Literal["up", "down"]


class LogResponse(BaseModel):
    """Short response returned right after a new log is submitted."""

    log_id: str
    parsed_tasks: list[ParsedTask]
    battery_before: int
    battery_after: int


class LogEntry(BaseModel):
    """Full log shape returned when the app loads the user's history."""

    log_id: str
    user_id: str
    text: str
    normalized_text: str
    logged_at: datetime
    parsed_tasks: list[ParsedTask]
    battery_before: int
    battery_after: int
