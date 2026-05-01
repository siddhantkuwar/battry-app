from typing import Annotated

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from .config import get_supabase_api_key, get_supabase_url


bearer_scheme = HTTPBearer(auto_error=False)


class AuthenticatedUser(BaseModel):
    id: str
    email: str | None = None


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> AuthenticatedUser:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    supabase_url = get_supabase_url()
    supabase_api_key = get_supabase_api_key()
    if not supabase_url or not supabase_api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Auth is not configured.",
        )

    auth_url = f"{supabase_url.rstrip('/')}/auth/v1/user"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                auth_url,
                headers={
                    "apikey": supabase_api_key,
                    "Authorization": f"Bearer {credentials.credentials}",
                },
            )
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Auth provider is unavailable.",
        ) from exc

    if response.status_code != status.HTTP_200_OK:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_data = response.json()
    user_id = user_data.get("id")
    if not isinstance(user_id, str) or not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid auth user.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    email = user_data.get("email")
    return AuthenticatedUser(
        id=user_id,
        email=email if isinstance(email, str) else None,
    )
