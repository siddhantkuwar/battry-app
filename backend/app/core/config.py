import os


def get_database_url() -> str | None:
    return os.getenv("SUPABASE_DATABASE_URL") or os.getenv("DATABASE_URL")


def is_database_configured() -> bool:
    return get_database_url() is not None
