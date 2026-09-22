

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project_member_permission import ProjectMemberPermission


class ProjectMemberPermissionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(
        self,
        permission_id: UUID,
    ) -> ProjectMemberPermission | None:
        result = await self.db.execute(
            select(ProjectMemberPermission).where(
                ProjectMemberPermission.id == permission_id
            )
        )
        return result.scalar_one_or_none()

    async def get_by_member_and_permission(
        self,
        project_member_id: UUID,
        permission_id: UUID,
    ) -> ProjectMemberPermission | None:
        result = await self.db.execute(
            select(ProjectMemberPermission).where(
                ProjectMemberPermission.project_member_id == project_member_id,
                ProjectMemberPermission.permission_id == permission_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_project_member(
        self,
        project_member_id: UUID,
    ) -> list[ProjectMemberPermission]:
        result = await self.db.execute(
            select(ProjectMemberPermission).where(
                ProjectMemberPermission.project_member_id == project_member_id
            )
        )
        return list(result.scalars().all())

    async def create(
        self,
        project_member_id: UUID,
        permission_id: UUID,
        is_allowed: bool,
    ) -> ProjectMemberPermission:
        override = ProjectMemberPermission(
            project_member_id=project_member_id,
            permission_id=permission_id,
            is_allowed=is_allowed,
        )

        self.db.add(override)

        await self.db.flush()

        return override

    async def delete(
        self,
        project_member_id: UUID,
        permission_id: UUID,
    ) -> None:
        override = await self.get_by_member_and_permission(
            project_member_id=project_member_id,
            permission_id=permission_id,
        )

        if override:
            await self.db.delete(override)
            await self.db.flush()
