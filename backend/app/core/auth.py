from typing import Annotated

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from .config import get_supabase_api_key, get_supabase_url


bearer_scheme = HTTPBearer(auto_error=False)


class AuthenticatedUser(BaseModel):
    """The small user object the rest of the API is allowed to trust.

    We only expose fields that came back from Supabase after token validation.
    Routes should use this instead of accepting a user id from the client.
    """

    id: str
    is_anonymous: bool


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> AuthenticatedUser:
    """Validate the request's bearer token with Supabase Auth.

    FastAPI runs this as a dependency before protected routes. If anything is
    missing, expired, or misconfigured, it raises an HTTP error and the route
    handler never receives control.
    """
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

    # Supabase exposes the current user at /auth/v1/user when we pass the
    # mobile app's access token in the Authorization header.
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

    # We only trust the request after Supabase returns a concrete user id.
    user_data = response.json()
    user_id = user_data.get("id")
    if not isinstance(user_id, str) or not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid auth user.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Battry is privacy-first right now. We only accept Supabase anonymous
    # device users, not permanent email/OAuth users.
    is_anonymous = user_data.get("is_anonymous")
    if is_anonymous is not True:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Battry only accepts anonymous device sessions.",
        )

    return AuthenticatedUser(
        id=user_id,
        is_anonymous=True,
    )
