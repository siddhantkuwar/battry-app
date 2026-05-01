from dataclasses import dataclass
from threading import Lock
from time import monotonic

from .config import (
    get_log_rate_limit_max_requests,
    get_log_rate_limit_window_seconds,
)


@dataclass
class RateLimitDecision:
    """Result of checking one user's current rate-limit bucket."""

    is_allowed: bool
    retry_after_seconds: int


@dataclass
class _RateLimitBucket:
    """In-memory fixed-window counter for one anonymous device."""

    count: int
    reset_at: float


_LOG_SUBMISSION_BUCKETS: dict[str, _RateLimitBucket] = {}
_LOCK = Lock()


def check_log_submission_rate_limit(user_id: str) -> RateLimitDecision:
    """Limit how quickly one anonymous device can submit logs.

    This is intentionally in-memory for the current single-process app. When
    Battry runs multiple API workers or instances, move this counter to Redis,
    Postgres, or an edge rate limiter so every process shares the same state.
    """
    max_requests = get_log_rate_limit_max_requests()
    window_seconds = get_log_rate_limit_window_seconds()
    now = monotonic()

    with _LOCK:
        bucket = _LOG_SUBMISSION_BUCKETS.get(user_id)
        if bucket is None or now >= bucket.reset_at:
            _LOG_SUBMISSION_BUCKETS[user_id] = _RateLimitBucket(
                count=1,
                reset_at=now + window_seconds,
            )
            return RateLimitDecision(is_allowed=True, retry_after_seconds=0)

        if bucket.count >= max_requests:
            retry_after = max(1, int(bucket.reset_at - now))
            return RateLimitDecision(
                is_allowed=False,
                retry_after_seconds=retry_after,
            )

        bucket.count += 1
        return RateLimitDecision(is_allowed=True, retry_after_seconds=0)
