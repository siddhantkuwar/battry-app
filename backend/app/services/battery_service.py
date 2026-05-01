from collections.abc import Iterable, Mapping
from typing import Protocol


DEFAULT_BATTERY = 50
MIN_BATTERY = 0
MAX_BATTERY = 100

DEFAULT_RECHARGE_WEIGHT = 10
DEFAULT_DRAIN_WEIGHT = -10

# Known labels get product-specific weights. Unknown labels can still move the
# score by direction through the default recharge/drain constants.
TASK_WEIGHTS = {
    "bad_sleep": -12,
    "small_talk": -8,
    "doomscrolling": -10,
    "quiet_time": 12,
    "music_session": 8,
}


class BatteryTask(Protocol):
    """The minimum shape needed by the battery scoring functions."""

    label: str
    direction: str


def clamp_score(score: int) -> int:
    """Keep a battery score inside the user-facing 0-100 range."""
    return max(MIN_BATTERY, min(MAX_BATTERY, score))


def get_task_weight(task: BatteryTask) -> int:
    """Translate one parsed event into a battery score change."""
    if task.label in TASK_WEIGHTS:
        return TASK_WEIGHTS[task.label]

    if task.direction == "up":
        return DEFAULT_RECHARGE_WEIGHT
    if task.direction == "down":
        return DEFAULT_DRAIN_WEIGHT

    return 0


def calculate_battery_after(battery_before: int, tasks: Iterable[BatteryTask]) -> int:
    """Apply all parsed events to the previous battery score."""
    battery_delta = sum(get_task_weight(task) for task in tasks)
    return clamp_score(battery_before + battery_delta)


def get_previous_battery_for_user(
    logs: Iterable[Mapping[str, object]],
    user_id: str,
) -> int:
    """Find the latest in-memory battery score for a user.

    This helper is only for the no-database fallback. The database path uses a
    SQL query because it should not load every historical log into Python.
    """
    for log in reversed(list(logs)):
        if log.get("user_id") == user_id:
            battery_after = log.get("battery_after", DEFAULT_BATTERY)
            if isinstance(battery_after, int):
                return clamp_score(battery_after)
            return DEFAULT_BATTERY

    return DEFAULT_BATTERY
