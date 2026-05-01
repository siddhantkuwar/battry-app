import os


def get_database_url() -> str | None:
    return os.getenv("SUPABASE_DATABASE_URL") or os.getenv("DATABASE_URL")


def is_database_configured() -> bool:
    return get_database_url() is not None


def get_supabase_url() -> str | None:
    return os.getenv("SUPABASE_URL")


def get_supabase_api_key() -> str | None:
    return os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_PUBLISHABLE_KEY")
