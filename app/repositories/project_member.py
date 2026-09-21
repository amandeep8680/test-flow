from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project_member import ProjectMember


class ProjectMemberRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        project_id: UUID,
        user_id: UUID,
        role: str,
    ) -> ProjectMember:
        member = ProjectMember(
            project_id=project_id,
            user_id=user_id,
            role=role,
        )

        self.db.add(member)
        await self.db.flush()

        return member

    async def get_by_project_and_user(
        self,
        project_id: UUID,
        user_id: UUID,
    ) -> ProjectMember | None:
        result = await self.db.execute(
            select(ProjectMember).where(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == user_id,
            )
        )

        return result.scalar_one_or_none()

    async def get_by_project(
        self,
        project_id: UUID,
    ) -> list[ProjectMember]:
        result = await self.db.execute(
            select(ProjectMember)
            .where(
                ProjectMember.project_id == project_id,
            )
            .order_by(ProjectMember.created_at.asc())
        )

        return list(result.scalars().all())

    async def update_role(
        self,
        member: ProjectMember,
        role: str,
    ) -> ProjectMember:
        member.role = role

        await self.db.flush()

        return member

    async def delete(
        self,
        member: ProjectMember,
    ) -> None:
        await self.db.delete(member)
        await self.db.flush()

