from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.permission import Permission


class PermissionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, permission_id: UUID) -> Permission | None:
        result = await self.db.execute(
            select(Permission).where(
                Permission.id == permission_id
            )
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Permission | None:
        result = await self.db.execute(
            select(Permission).where(
                Permission.name == name
            )
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> list[Permission]:
        result = await self.db.execute(
            select(Permission)
            .order_by(Permission.name)
        )
        return list(result.scalars().all())

    async def create(
        self,
        name: str,
        description: str | None = None,
    ) -> Permission:
        permission = Permission(
            name=name,
            description=description,
        )

        self.db.add(permission)
        await self.db.flush()

        return permission

