"""Authentication API endpoints — login and user identity."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import CurrentUser
from app.core.exceptions import UnauthorizedError
from app.db.session import get_db
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserResponse
from app.services.auth_service import authenticate_user, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse, summary="User login")
async def login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Authenticate user with email and password from PostgreSQL and generate JWT."""
    user = await authenticate_user(db, data.email, data.password)
    if not user:
        raise UnauthorizedError("Invalid email or password.")

    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "department_id": str(user.department_id) if user.department_id else None,
    }
    access_token = create_access_token(token_data)
    user_resp = UserResponse.from_orm_user(user)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_resp,
    )


@router.get("/me", response_model=UserResponse, summary="Get authenticated user profile")
async def get_me(
    current_user: CurrentUser,
) -> UserResponse:
    """Return authenticated profile resolved from JWT."""
    return UserResponse.from_orm_user(current_user)
