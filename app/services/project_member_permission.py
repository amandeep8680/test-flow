from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.permission import Permission
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.user import User

from app.repositories.project_member_permission import (
    ProjectMemberPermissionRepository,
)


class ProjectMemberPermissionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = ProjectMemberPermissionRepository(db)

    async def _get_project_member(
        self,
        project_id: UUID,
        user_id: UUID,
        organization_id: UUID,
    ) -> ProjectMember | None:
        result = await self.db.execute(
            select(ProjectMember)
            .join(
                Project,
                Project.id == ProjectMember.project_id,
            )
            .join(
                User,
                User.id == ProjectMember.user_id,
            )
            .where(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == user_id,
                Project.organization_id == organization_id,
                User.organization_id == organization_id,
            )
        )

        return result.scalar_one_or_none()

    async def get_permissions(
        self,
        project_id: UUID,
        user_id: UUID,
        organization_id: UUID,
    ):
        project_member = await self._get_project_member(
            project_id=project_id,
            user_id=user_id,
            organization_id=organization_id,
        )

        if project_member is None:
            return None

        return await self.repository.get_by_project_member(
            project_member_id=project_member.id,
        )

    async def set_permission(
        self,
        project_id: UUID,
        user_id: UUID,
        permission_id: UUID,
        is_allowed: bool,
        organization_id: UUID,
    ):
        # 1. Verify project member belongs to current organization.
        project_member = await self._get_project_member(
            project_id=project_id,
            user_id=user_id,
            organization_id=organization_id,
        )

        if project_member is None:
            return None

        # 2. Verify permission exists.
        result = await self.db.execute(
            select(Permission).where(
                Permission.id == permission_id,
            )
        )

        permission = result.scalar_one_or_none()

        if permission is None:
            return None

        # 3. Check whether override already exists.
        existing = await self.repository.get_by_member_and_permission(
            project_member_id=project_member.id,
            permission_id=permission_id,
        )

        if existing:
            existing.is_allowed = is_allowed

            await self.db.commit()
            await self.db.refresh(existing)

            return existing

        # 4. Create new project-specific override.
        override = await self.repository.create(
            project_member_id=project_member.id,
            permission_id=permission_id,
            is_allowed=is_allowed,
        )

        await self.db.commit()
        await self.db.refresh(override)

        return override

    async def remove_permission(
        self,
        project_id: UUID,
        user_id: UUID,
        permission_id: UUID,
        organization_id: UUID,
    ) -> bool:
        # 1. Verify project member.
        project_member = await self._get_project_member(
            project_id=project_id,
            user_id=user_id,
            organization_id=organization_id,
        )

        if project_member is None:
            return False

        # 2. Check override exists.
        existing = await self.repository.get_by_member_and_permission(
            project_member_id=project_member.id,
            permission_id=permission_id,
        )

        if existing is None:
            return False

        # 3. Remove override.
        await self.repository.delete(
            project_member_id=project_member.id,
            permission_id=permission_id,
        )

        await self.db.commit()

        return True
