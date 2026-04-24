from fastapi import FastAPI

from .api.health import router as health_router
from .api.logs import router as logs_router
from .api.reports import router as reports_router


app = FastAPI(title="Battry API v2")

app.include_router(health_router, prefix="/api")
app.include_router(logs_router)
app.include_router(reports_router)
