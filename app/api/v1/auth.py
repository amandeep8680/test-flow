from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User

from app.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    OrganizationSignupRequest,
    RefreshTokenRequest,
    TokenResponse,
)

from app.schemas.organization import OrganizationResponse

from app.services.auth import AuthService
from app.services.token import TokenService

from app.exception.messages import AuthMessages


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
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

    organization, _admin_user = (
        await auth_service.register_organization(request)
    )

    return organization


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

    return await auth_service.login(request)


@router.post(
    "/change-password",
    status_code=status.HTTP_200_OK,
)
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Change the current user's password.
    """

    auth_service = AuthService(db)

    await auth_service.change_password(
        user=current_user,
        current_password=request.current_password,
        new_password=request.new_password,
    )

    return {
        "message": AuthMessages.PASSWORD_CHANGED_SUCCESSFULLY
    }


@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Generate a new access token using a valid refresh token.
    """

    token_service = TokenService(db)

    return await token_service.refresh_access_token(
        request.refresh_token
    )


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
)
async def logout(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Revoke the refresh token and logout the user.
    """

    token_service = TokenService(db)

    return await token_service.logout(
        request.refresh_token
    )