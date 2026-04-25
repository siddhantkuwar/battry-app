import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.health import router as health_router
from .api.logs import router as logs_router
from .api.reports import router as reports_router


app = FastAPI(title="Battry API v2")

cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "BATTRY_CORS_ORIGINS",
        "http://localhost:8081,http://127.0.0.1:8081,http://localhost:19006,http://127.0.0.1:19006",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_credentials=False,
    allow_headers=["*"],
    allow_methods=["*"],
    allow_origins=cors_origins,
)

app.include_router(health_router, prefix="/api")
app.include_router(logs_router)
app.include_router(reports_router)
