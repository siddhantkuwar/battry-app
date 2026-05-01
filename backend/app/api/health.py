from fastapi import APIRouter


router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Return a tiny response that proves the API process is alive."""
    return {"status": "ok"}
