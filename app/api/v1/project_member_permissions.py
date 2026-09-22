
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.permissions import require_permission
from app.models.user import User
from app.services.project_member_permission import (
    ProjectMemberPermissionService,
)


router = APIRouter(
    prefix="/projects",
    tags=["Project Member Permissions"],
)


@router.get("/{project_id}/members/{user_id}/permissions")
async def get_project_member_permissions(
    project_id: UUID,
    user_id: UUID,
    current_user: User = Depends(
        require_permission("project.manage_members")
    ),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectMemberPermissionService(db)

    permissions = await service.get_permissions(
        project_id=project_id,
        user_id=user_id,
        organization_id=current_user.organization_id,
    )

    if permissions is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project member not found",
        )

    return permissions


@router.put(
    "/{project_id}/members/{user_id}/permissions/{permission_id}"
)
async def set_project_member_permission(
    project_id: UUID,
    user_id: UUID,
    permission_id: UUID,
    is_allowed: bool,
    current_user: User = Depends(
        require_permission("project.manage_members")
    ),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectMemberPermissionService(db)

    override = await service.set_permission(
        project_id=project_id,
        user_id=user_id,
        permission_id=permission_id,
        is_allowed=is_allowed,
        organization_id=current_user.organization_id,
    )

    if override is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project member or permission not found",
        )

    return override


@router.delete(
    "/{project_id}/members/{user_id}/permissions/{permission_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_project_member_permission(
    project_id: UUID,
    user_id: UUID,
    permission_id: UUID,
    current_user: User = Depends(
        require_permission("project.manage_members")
    ),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectMemberPermissionService(db)

    removed = await service.remove_permission(
        project_id=project_id,
        user_id=user_id,
        permission_id=permission_id,
        organization_id=current_user.organization_id,
    )

    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project permission override not found",
        )

    return None
