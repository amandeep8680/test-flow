from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.auth import (
    LoginRequest,
    OrganizationSignupRequest,
    TokenResponse,
)
from app.schemas.organization import OrganizationResponse
from app.services.auth import AuthService
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)
from app.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    OrganizationSignupRequest,
    TokenResponse,
)

@router.post(
    "/register-organization",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_organization(
    request: OrganizationSignupRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new organization and its initial ADMIN user.
    """

    auth_service = AuthService(db)

    try:
        organization, _admin_user = (
            await auth_service.register_organization(request)
        )

        return organization

    except ValueError as exc:
        await db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticate a user and return access and refresh tokens.
    """

    auth_service = AuthService(db)

    try:
        return await auth_service.login(request)

    except ValueError as exc:
        await db.rollback()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        )

@router.post(
    "/change-password",
    status_code=status.HTTP_200_OK,
)
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    auth_service = AuthService(db)

    try:
        await auth_service.change_password(
            user=current_user,
            current_password=request.current_password,
            new_password=request.new_password,
        )

        return {
            "message": "Password changed successfully"
        }

    except ValueError as exc:
        await db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )