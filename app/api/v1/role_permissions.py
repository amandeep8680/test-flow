
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.permissions import require_permission
from app.models.user import User
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
    current_user: User = Depends(
        require_permission("role.view")
    ),
    db: AsyncSession = Depends(get_db),
):
    service = RolePermissionService(db)

    permissions = await service.get_role_permissions(
        role_id=role_id,
        organization_id=current_user.organization_id,
    )

    if permissions is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )

    return permissions


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

