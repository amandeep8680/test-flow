
from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.permissions import require_admin
from app.models.role import Role
from app.models.user import User
from app.schemas.auth import UserResponse
from app.schemas.user import (
    CreateUserRequest,
    CreateUserResponse,
)
from app.services.user import UserService


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get(
    "/me",
    response_model=UserResponse,
)
async def get_user_info(
    current_user: User = Depends(get_current_user),
):
    """
    Return information about the currently authenticated user.
    """

    return current_user


@router.get(
    "/roles",
    response_model=list[str],
)
async def get_roles(
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Role.name).order_by(Role.name)
    )

    return result.scalars().all()


@router.get(
    "",
    response_model=list[UserResponse],
)
async def get_users(
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Return all users from the ADMIN's organization.
    """

    user_service = UserService(db)

    return await user_service.get_users(
        organization_id=current_admin.organization_id,
    )


@router.post(
    "",
    response_model=CreateUserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    request: CreateUserRequest,
    current_admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new user inside the ADMIN's organization.
    """

    user_service = UserService(db)

    user, role_name, temporary_password = (
        await user_service.create_user(
            request=request,
            organization_id=current_admin.organization_id,
        )
    )

    return CreateUserResponse(
        id=user.id,
        organization_id=user.organization_id,
        email=user.email,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        role=role_name,
        is_active=user.is_active,
        must_change_password=user.must_change_password,
        temporary_password=temporary_password,
    )

