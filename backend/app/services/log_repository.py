from collections.abc import Mapping
from datetime import datetime
from uuid import uuid4

from psycopg.rows import dict_row

from ..core.config import get_database_url
from ..schemas.log import ParsedTask
from .battery_service import get_task_weight


LOGS_DB: list[dict[str, object]] = []


def _get_connection():
    database_url = get_database_url()
    if database_url is None:
        return None

    from psycopg import connect

    return connect(database_url, row_factory=dict_row)


def _serialize_log_row(row: Mapping[str, object]) -> dict[str, object]:
    parsed_tasks = row.get("parsed_tasks")
    if parsed_tasks is None:
        parsed_tasks = []

    return {
        "log_id": str(row["log_id"]),
        "user_id": row["user_id"],
        "text": row["text"],
        "normalized_text": row["normalized_text"],
        "logged_at": row["logged_at"],
        "parsed_tasks": parsed_tasks,
        "battery_before": row["battery_before"],
        "battery_after": row["battery_after"],
    }


def is_persistent_store_enabled() -> bool:
    return get_database_url() is not None


def list_logs(user_id: str | None = None) -> list[dict[str, object]]:
    connection = _get_connection()
    if connection is None:
        logs = LOGS_DB
        if user_id is not None:
            logs = [log for log in LOGS_DB if log["user_id"] == user_id]
        return logs

    with connection:
        with connection.cursor() as cursor:
            if user_id is None:
                cursor.execute(
                    """
                    select
                        dl.log_id,
                        dl.user_id,
                        dl.text,
                        dl.normalized_text,
                        dl.logged_at,
                        coalesce(
                            jsonb_agg(
                                jsonb_build_object(
                                    'label', pe.label,
                                    'direction', pe.direction
                                )
                                order by pe.event_order
                            ) filter (where pe.id is not null),
                            '[]'::jsonb
                        ) as parsed_tasks,
                        dl.battery_before,
                        dl.battery_after
                    from daily_logs dl
                    left join parsed_events pe on pe.log_id = dl.log_id
                    group by dl.log_id
                    order by dl.logged_at asc, dl.created_at asc
                    """
                )
            else:
                cursor.execute(
                    """
                    select
                        dl.log_id,
                        dl.user_id,
                        dl.text,
                        dl.normalized_text,
                        dl.logged_at,
                        coalesce(
                            jsonb_agg(
                                jsonb_build_object(
                                    'label', pe.label,
                                    'direction', pe.direction
                                )
                                order by pe.event_order
                            ) filter (where pe.id is not null),
                            '[]'::jsonb
                        ) as parsed_tasks,
                        dl.battery_before,
                        dl.battery_after
                    from daily_logs dl
                    left join parsed_events pe on pe.log_id = dl.log_id
                    where dl.user_id = %s
                    group by dl.log_id
                    order by dl.logged_at asc, dl.created_at asc
                    """,
                    (user_id,),
                )

            return [_serialize_log_row(row) for row in cursor.fetchall()]


def get_latest_battery_for_user(user_id: str) -> int | None:
    connection = _get_connection()
    if connection is None:
        for log in reversed(LOGS_DB):
            if log["user_id"] == user_id:
                return int(log["battery_after"])
        return None

    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                select battery_after
                from daily_logs
                where user_id = %s
                order by logged_at desc, created_at desc
                limit 1
                """,
                (user_id,),
            )
            row = cursor.fetchone()

    if row is None:
        return None

    return int(row["battery_after"])


def create_log(
    *,
    user_id: str,
    text: str,
    normalized_text: str,
    logged_at: datetime,
    parsed_tasks: list[ParsedTask],
    battery_before: int,
    battery_after: int,
) -> dict[str, object]:
    log_id = str(uuid4())
    task_payload = [task.model_dump() for task in parsed_tasks]

    connection = _get_connection()
    if connection is None:
        log = {
            "log_id": log_id,
            "user_id": user_id,
            "text": text,
            "normalized_text": normalized_text,
            "logged_at": logged_at,
            "parsed_tasks": task_payload,
            "battery_before": battery_before,
            "battery_after": battery_after,
        }
        LOGS_DB.append(log)
        return log

    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                insert into app_users (id)
                values (%s)
                on conflict (id) do nothing
                """,
                (user_id,),
            )
            cursor.execute(
                """
                insert into daily_logs (
                    log_id,
                    user_id,
                    text,
                    normalized_text,
                    logged_at,
                    battery_before,
                    battery_after
                )
                values (%s, %s, %s, %s, %s, %s, %s)
                returning log_id
                """,
                (
                    log_id,
                    user_id,
                    text,
                    normalized_text,
                    logged_at,
                    battery_before,
                    battery_after,
                ),
            )
            cursor.executemany(
                """
                insert into parsed_events (
                    log_id,
                    user_id,
                    label,
                    direction,
                    weight,
                    event_order
                )
                values (%s, %s, %s, %s, %s, %s)
                """,
                [
                    (
                        log_id,
                        user_id,
                        task.label,
                        task.direction,
                        get_task_weight(task),
                        index,
                    )
                    for index, task in enumerate(parsed_tasks)
                ],
            )

    return {
        "log_id": log_id,
        "user_id": user_id,
        "text": text,
        "normalized_text": normalized_text,
        "logged_at": logged_at,
        "parsed_tasks": task_payload,
        "battery_before": battery_before,
        "battery_after": battery_after,
    }
