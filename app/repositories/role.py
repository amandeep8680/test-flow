from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.role import Role


class RoleRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(
        self,
        role_id: UUID,
        organization_id: UUID,
    ) -> Role | None:
        result = await self.db.execute(
            select(Role).where(
                Role.id == role_id,
                Role.organization_id == organization_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_name(
        self,
        name: str,
        organization_id: UUID,
    ) -> Role | None:
        result = await self.db.execute(
            select(Role).where(
                Role.name == name,
                Role.organization_id == organization_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        organization_id: UUID,
    ) -> list[Role]:
        result = await self.db.execute(
            select(Role)
            .where(
                Role.organization_id == organization_id
            )
            .order_by(Role.name)
        )
        return list(result.scalars().all())

    async def create(
        self,
        organization_id: UUID,
        name: str,
        description: str | None = None,
    ) -> Role:
        role = Role(
            organization_id=organization_id,
            name=name,
            description=description,
            is_active=True,
        )

        self.db.add(role)
        await self.db.flush()

        return role

