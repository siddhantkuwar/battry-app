from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class LogRequest(BaseModel):
    user_id: str = Field(min_length=1)
    text: str = Field(min_length=1, max_length=500)
    logged_at: datetime


class ParsedTask(BaseModel):
    label: str
    direction: Literal["up", "down"]


class LogResponse(BaseModel):
    log_id: str
    parsed_tasks: list[ParsedTask]
    battery_before: int
    battery_after: int
