
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_user

from app.models.permission import Permission
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.project_member_permission import ProjectMemberPermission
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.user import User
from app.models.user_role import UserRole


def require_permission(permission_name: str):
    """
    Check a normal organization-level permission.

    Example:
        Depends(require_permission("user.create"))
    """

    async def permission_dependency(
        current_user: Annotated[User, Depends(get_current_user)],
        db: Annotated[AsyncSession, Depends(get_db)],
    ):
        result = await db.execute(
            select(Permission.id)
            .join(
                RolePermission,
                RolePermission.permission_id == Permission.id,
            )
            .join(
                Role,
                Role.id == RolePermission.role_id,
            )
            .join(
                UserRole,
                UserRole.role_id == Role.id,
            )
            .where(
                UserRole.user_id == current_user.id,
                Role.organization_id == current_user.organization_id,
                Role.is_active.is_(True),
                Permission.name == permission_name,
            )
        )

        permission_id = result.scalar_one_or_none()

        if permission_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )

        return current_user

    return permission_dependency



def require_project_permission(permission_name: str):
    """
    Check permission with project-level override support.

    Resolution order:

        Project override DENY
            -> DENY

        Project override ALLOW
            -> ALLOW

        No project override
            -> Check organization role permission

    Project must belong to the current user's organization.
    """

    async def project_permission_dependency(
        project_id: UUID,
        current_user: Annotated[User, Depends(get_current_user)],
        db: Annotated[AsyncSession, Depends(get_db)],
    ):
        # ---------------------------------------------------------
        # 1. Verify project belongs to current user's organization
        # ---------------------------------------------------------

        project_result = await db.execute(
            select(Project.id).where(
                Project.id == project_id,
                Project.organization_id == current_user.organization_id,
            )
        )

        existing_project_id = project_result.scalar_one_or_none()

        if existing_project_id is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )

        # ---------------------------------------------------------
        # 2. Get permission
        # ---------------------------------------------------------

        permission_result = await db.execute(
            select(Permission.id).where(
                Permission.name == permission_name,
            )
        )

        permission_id = permission_result.scalar_one_or_none()

        if permission_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission does not exist",
            )

        # ---------------------------------------------------------
        # 3. Find user's membership in this project
        # ---------------------------------------------------------

        member_result = await db.execute(
            select(ProjectMember.id).where(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == current_user.id,
            )
        )

        project_member_id = member_result.scalar_one_or_none()

        # ---------------------------------------------------------
        # 4. Project-specific override
        # ---------------------------------------------------------

        if project_member_id is not None:
            override_result = await db.execute(
                select(ProjectMemberPermission.is_allowed).where(
                    ProjectMemberPermission.project_member_id
                    == project_member_id,
                    ProjectMemberPermission.permission_id
                    == permission_id,
                )
            )

            override = override_result.scalar_one_or_none()

            if override is True:
                return current_user

            if override is False:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=(
                        "You do not have permission to perform "
                        "this action in this project"
                    ),
                )

        # ---------------------------------------------------------
        # 5. No override -> check organization role permission
        # ---------------------------------------------------------

        role_permission_result = await db.execute(
            select(Permission.id)
            .join(
                RolePermission,
                RolePermission.permission_id == Permission.id,
            )
            .join(
                Role,
                Role.id == RolePermission.role_id,
            )
            .join(
                UserRole,
                UserRole.role_id == Role.id,
            )
            .where(
                UserRole.user_id == current_user.id,
                Role.organization_id == current_user.organization_id,
                Role.is_active.is_(True),
                Permission.id == permission_id,
            )
        )

        global_permission = role_permission_result.scalar_one_or_none()

        if global_permission is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )

        return current_user

    return project_permission_dependency

