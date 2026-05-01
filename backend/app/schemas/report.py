from pydantic import BaseModel


class WeeklyReportResponse(BaseModel):
    """Summary numbers shown on the mobile report screen."""

    user_id: str
    log_count: int
    average_battery: float
    min_battery: int
    max_battery: int
    top_drainer: str | None
    top_recharger: str | None
    risk: str
