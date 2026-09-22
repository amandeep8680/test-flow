
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.permissions import require_permission
from app.models.user import User
from app.services.user_role import UserRoleService


router = APIRouter(
    prefix="/users",
    tags=["User Roles"],
)


@router.get(
    "/{user_id}/roles",
)
async def get_user_roles(
    user_id: UUID,
    current_user: User = Depends(
        require_permission("user.view")
    ),
    db: AsyncSession = Depends(get_db),
):
    service = UserRoleService(db)

    roles = await service.get_user_roles(
        user_id=user_id,
        organization_id=current_user.organization_id,
    )

    if roles is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return roles


@router.post(
    "/{user_id}/roles/{role_id}",
    status_code=status.HTTP_201_CREATED,
)
async def assign_role(
    user_id: UUID,
    role_id: UUID,
    current_user: User = Depends(
        require_permission("user.edit")
    ),
    db: AsyncSession = Depends(get_db),
):
    service = UserRoleService(db)

    user_role = await service.assign_role(
        user_id=user_id,
        role_id=role_id,
        organization_id=current_user.organization_id,
    )

    if user_role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User or role not found",
        )

    return user_role


@router.delete(
    "/{user_id}/roles/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_role(
    user_id: UUID,
    role_id: UUID,
    current_user: User = Depends(
        require_permission("user.edit")
    ),
    db: AsyncSession = Depends(get_db),
):
    service = UserRoleService(db)

    removed = await service.remove_role(
        user_id=user_id,
        role_id=role_id,
        organization_id=current_user.organization_id,
    )

    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User or role assignment not found",
        )

    return None
