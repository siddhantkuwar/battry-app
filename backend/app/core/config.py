import os


def get_database_url() -> str | None:
    """Return the Postgres URL when persistent storage is configured.

    The app can run without a database during local development. Returning
    None is intentional: repository code uses it to choose the in-memory store.
    """
    return os.getenv("SUPABASE_DATABASE_URL") or os.getenv("DATABASE_URL")


def is_database_configured() -> bool:
    """Tell callers whether the backend should use the database-backed path."""
    return get_database_url() is not None


def get_supabase_url() -> str | None:
    """Return the Supabase project URL used to validate bearer tokens."""
    return os.getenv("SUPABASE_URL")


def get_supabase_api_key() -> str | None:
    """Return the public Supabase key used by the backend auth check."""
    return os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_PUBLISHABLE_KEY")
