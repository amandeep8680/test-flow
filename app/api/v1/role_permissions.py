from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.permissions import require_permission
from app.models.role import Role
from app.models.user import User
from app.models.user_role import UserRole
from app.services.role_permission import RolePermissionService


router = APIRouter(
    prefix="/roles",
    tags=["Role Permissions"],
)


@router.get(
    "/{role_id}/permissions",
)
async def get_role_permissions(
    role_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    assigned_role = await db.execute(
        select(Role.id).join(
            UserRole,
            UserRole.role_id == Role.id,
        ).where(
            Role.id == role_id,
            Role.organization_id == current_user.organization_id,
            Role.is_active.is_(True),
            UserRole.user_id == current_user.id,
        )
    )

    if assigned_role.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )

    service = RolePermissionService(db)

    return await service.get_role_permissions(
        role_id=role_id,
        organization_id=current_user.organization_id,
    )


@router.post(
    "/{role_id}/permissions/{permission_id}",
    status_code=status.HTTP_201_CREATED,
)
async def assign_permission(
    role_id: UUID,
    permission_id: UUID,
    current_user: User = Depends(
        require_permission("role.edit")
    ),
    db: AsyncSession = Depends(get_db),
):
    service = RolePermissionService(db)

    role_permission = await service.assign_permission(
        role_id=role_id,
        permission_id=permission_id,
        organization_id=current_user.organization_id,
    )

    if role_permission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role or permission not found",
        )

    return role_permission


@router.delete(
    "/{role_id}/permissions/{permission_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_permission(
    role_id: UUID,
    permission_id: UUID,
    current_user: User = Depends(
        require_permission("role.edit")
    ),
    db: AsyncSession = Depends(get_db),
):
    service = RolePermissionService(db)

    removed = await service.remove_permission(
        role_id=role_id,
        permission_id=permission_id,
        organization_id=current_user.organization_id,
    )

    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role or permission assignment not found",
        )

    return None