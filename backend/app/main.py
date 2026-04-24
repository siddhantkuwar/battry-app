from fastapi import FastAPI

from .api.health import router as health_router


app = FastAPI(title="Battry API v2")

app.include_router(health_router, prefix="/api")
