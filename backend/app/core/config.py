import os
from functools import lru_cache
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
LOCAL_ENV_FILES = (
    REPO_ROOT / ".env",
    REPO_ROOT / "mobile" / ".env",
)


@lru_cache(maxsize=1)
def _read_local_env_files() -> dict[str, str]:
    """Read ignored local env files without requiring python-dotenv."""
    values: dict[str, str] = {}

    for path in LOCAL_ENV_FILES:
        if not path.exists():
            continue

        for line in path.read_text().splitlines():
            if not line or line.lstrip().startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            values.setdefault(key.strip(), value.strip())

    return values


def _get_env(*names: str) -> str | None:
    """Read config from process env first, then ignored local env files."""
    local_values = _read_local_env_files()

    for name in names:
        value = os.getenv(name) or local_values.get(name)
        if value:
            return value

    return None


def _get_positive_int_env(name: str, default: int) -> int:
    """Read a positive integer env var without letting bad config crash startup."""
    try:
        value = int(_get_env(name) or str(default))
    except ValueError:
        return default

    return value if value > 0 else default


def get_database_url() -> str | None:
    """Return the Postgres URL when persistent storage is configured.

    The app can run without a database during local development. Returning
    None is intentional: repository code uses it to choose the in-memory store.
    """
    return _get_env("SUPABASE_DATABASE_URL", "DATABASE_URL")


def is_database_configured() -> bool:
    """Tell callers whether the backend should use the database-backed path."""
    return get_database_url() is not None


def get_supabase_url() -> str | None:
    """Return the Supabase project URL used to validate bearer tokens."""
    return _get_env("SUPABASE_URL", "EXPO_PUBLIC_SUPABASE_URL")


def get_supabase_api_key() -> str | None:
    """Return the public Supabase key used by the backend auth check."""
    return _get_env(
        "SUPABASE_ANON_KEY",
        "SUPABASE_PUBLISHABLE_KEY",
        "EXPO_PUBLIC_SUPABASE_ANON_KEY",
        "EXPO_PUBLIC_SUPABASE_PUBLISHABLE_KEY",
    )


def get_log_rate_limit_max_requests() -> int:
    """Return how many log submissions one device can make per window."""
    return _get_positive_int_env("BATTRY_LOG_RATE_LIMIT_MAX", 20)


def get_log_rate_limit_window_seconds() -> int:
    """Return the rate-limit window length for log submissions."""
    return _get_positive_int_env("BATTRY_LOG_RATE_LIMIT_WINDOW_SECONDS", 60)
