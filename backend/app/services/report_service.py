from collections import defaultdict
from collections.abc import Iterable, Mapping
from datetime import timedelta

from .battery_service import DEFAULT_BATTERY, TASK_WEIGHTS


def get_logs_for_user(
    logs: Iterable[Mapping[str, object]],
    user_id: str,
) -> list[Mapping[str, object]]:
    """Keep only logs that belong to the requested user."""
    return [log for log in logs if log.get("user_id") == user_id]


def get_weekly_logs(
    logs: Iterable[Mapping[str, object]],
    user_id: str,
) -> list[Mapping[str, object]]:
    """Select the last seven days of logs relative to the user's newest log.

    This intentionally uses the latest log as the anchor instead of today's
    date so sample data and manual tests keep producing useful reports.
    """
    user_logs = get_logs_for_user(logs, user_id)
    dated_logs = [log for log in user_logs if log.get("logged_at") is not None]
    if not dated_logs:
        return []

    latest_logged_at = max(log["logged_at"] for log in dated_logs)
    week_start = latest_logged_at - timedelta(days=7)

    return [
        log
        for log in dated_logs
        if week_start <= log["logged_at"] <= latest_logged_at
    ]


def calculate_battery_stats(logs: Iterable[Mapping[str, object]]) -> dict[str, float | int]:
    """Calculate average, minimum, and maximum battery scores for a log set."""
    battery_scores = [
        log["battery_after"]
        for log in logs
        if isinstance(log.get("battery_after"), int)
    ]

    if not battery_scores:
        return {
            "average_battery": float(DEFAULT_BATTERY),
            "min_battery": DEFAULT_BATTERY,
            "max_battery": DEFAULT_BATTERY,
        }

    return {
        "average_battery": round(sum(battery_scores) / len(battery_scores), 2),
        "min_battery": min(battery_scores),
        "max_battery": max(battery_scores),
    }


def find_top_energy_events(
    logs: Iterable[Mapping[str, object]],
) -> tuple[str | None, str | None]:
    """Find the strongest repeated drainer and recharger labels."""
    drainer_scores: dict[str, int] = defaultdict(int)
    recharger_scores: dict[str, int] = defaultdict(int)

    for log in logs:
        parsed_tasks = log.get("parsed_tasks", [])
        if not isinstance(parsed_tasks, list):
            continue

        for task in parsed_tasks:
            if not isinstance(task, dict):
                continue

            label = task.get("label")
            direction = task.get("direction")
            if not isinstance(label, str):
                continue

            weight = TASK_WEIGHTS.get(label, 0)
            if direction == "down" or weight < 0:
                drainer_scores[label] += abs(weight)
            elif direction == "up" or weight > 0:
                recharger_scores[label] += abs(weight)

    top_drainer = max(drainer_scores, key=drainer_scores.get, default=None)
    top_recharger = max(recharger_scores, key=recharger_scores.get, default=None)

    return top_drainer, top_recharger


def calculate_risk(average_battery: float, min_battery: int) -> str:
    """Convert report numbers into a simple risk label for the UI."""
    if min_battery <= 20 or average_battery < 35:
        return "high"
    if min_battery <= 40 or average_battery < 55:
        return "medium"
    return "low"


def build_weekly_report(
    logs: Iterable[Mapping[str, object]],
    user_id: str,
) -> dict[str, object]:
    """Build the complete weekly report response for one user."""
    weekly_logs = get_weekly_logs(logs, user_id)
    stats = calculate_battery_stats(weekly_logs)
    top_drainer, top_recharger = find_top_energy_events(weekly_logs)

    return {
        "user_id": user_id,
        "log_count": len(weekly_logs),
        **stats,
        "top_drainer": top_drainer,
        "top_recharger": top_recharger,
        "risk": calculate_risk(
            float(stats["average_battery"]),
            int(stats["min_battery"]),
        ),
    }
