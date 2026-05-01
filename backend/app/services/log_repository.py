from collections.abc import Mapping
from datetime import datetime
from uuid import uuid4

from psycopg.rows import dict_row

from ..core.config import get_database_url
from ..schemas.log import ParsedTask
from .battery_service import get_task_weight


# In-memory storage keeps local development working before Postgres is set up.
# It resets whenever the API process restarts and should not be treated as
# production storage.
LOGS_DB: list[dict[str, object]] = []


def _get_connection():
    """Open a Postgres connection when database mode is configured.

    Returning None is the signal for callers to use the in-memory fallback.
    Importing psycopg inside the function keeps no-database local runs lighter.
    """
    database_url = get_database_url()
    if database_url is None:
        return None

    from psycopg import connect

    return connect(database_url, row_factory=dict_row)


def _serialize_log_row(row: Mapping[str, object]) -> dict[str, object]:
    """Turn a SQL row into the same dictionary shape as the in-memory store."""
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
    """Tell route code whether log writes will go to Postgres."""
    return get_database_url() is not None


def list_logs(user_id: str) -> list[dict[str, object]]:
    """Return all logs for a user from the active storage backend."""
    connection = _get_connection()
    if connection is None:
        return [log for log in LOGS_DB if log["user_id"] == user_id]

    with connection:
        with connection.cursor() as cursor:
            # The JSON aggregation rebuilds the parsed_tasks list that the API
            # already returns in memory mode, so callers do not care where the
            # data came from.
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
    """Fetch the user's newest stored battery score, if one exists."""
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
    """Persist a parsed log and return it in API-friendly dictionary form."""
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
            # app_users is a lightweight mirror of Supabase user ids so foreign
            # keys can protect daily_logs and parsed_events.
            cursor.execute(
                """
                insert into app_users (id)
                values (%s)
                on conflict (id) do nothing
                """,
                (user_id,),
            )
            # Store the original text for display and the normalized text for
            # future parser/debug work.
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
            # Each parsed event gets its own row so later reports can ask
            # database-level questions about labels and weights.
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
