"""FastAPI auth dependencies — extract and validate the current user from PostgreSQL."""

from typing import Annotated, Any
import uuid

from fastapi import Depends, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth.jwt import decode_token as decode_keycloak_token
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.db.models.user import User
from app.db.session import get_db
from app.services.auth_service import decode_access_token

_bearer = HTTPBearer(auto_error=False)


async def get_token_payload(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Security(_bearer)],
) -> dict[str, Any]:
    """Extract and validate the Bearer token from the Authorization header."""
    if credentials is None:
        raise UnauthorizedError("No authorization token provided")

    token = credentials.credentials
    # First attempt to decode as a local JWT
    try:
        return decode_access_token(token)
    except Exception:
        pass

    # Fallback to Keycloak JWKS RS256 token
    try:
        return await decode_keycloak_token(token)
    except Exception as exc:
        raise UnauthorizedError("Invalid or expired token") from exc


async def get_current_user(
    payload: Annotated[dict[str, Any], Depends(get_token_payload)],
    db: AsyncSession = Depends(get_db),
) -> User:
    """Resolve and return the real User entity from PostgreSQL."""
    sub: str | None = payload.get("sub")
    email: str | None = payload.get("email")

    if not sub and not email:
        raise UnauthorizedError("Token missing subject or email claim")

    user: User | None = None

    # Try lookup by UUID sub
    try:
        user_uuid = uuid.UUID(sub)
        query = select(User).where(User.id == user_uuid).options(selectinload(User.department))
        res = await db.execute(query)
        user = res.scalar_one_or_none()
    except (ValueError, TypeError):
        user = None

    # Fallback lookup by email
    if not user and email:
        query = select(User).where(User.email == email.strip().lower()).options(selectinload(User.department))
        res = await db.execute(query)
        user = res.scalar_one_or_none()

    # Fallback lookup by keycloak_id
    if not user and sub:
        query = select(User).where(User.keycloak_id == sub).options(selectinload(User.department))
        res = await db.execute(query)
        user = res.scalar_one_or_none()

    if not user:
        raise UnauthorizedError("User not found in system")

    if not user.is_active:
        raise UnauthorizedError("User account is deactivated")

    return user


def require_role(*roles: str):  # noqa: ANN201
    """Dependency factory — raises 403 if the user lacks any of the required roles.

    Usage:
        @router.get("/admin/users", dependencies=[Depends(require_role("ADMIN"))])
    """
    normalized_roles = [r.upper() for r in roles]

    async def _check(
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        if current_user.is_superuser:
            return current_user

        user_role = (current_user.role or "").upper()
        if user_role not in normalized_roles:
            raise ForbiddenError(f"Access denied. Required role: {', '.join(roles)}")
        return current_user

    return _check


# ── Convenience type aliases ─────────────────────────────────────────────────
CurrentUser = Annotated[User, Depends(get_current_user)]
