from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.role_permission import RolePermission


class RolePermissionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_permissions_by_role(
        self,
        role_id: UUID,
    ) -> list[RolePermission]:
        result = await self.db.execute(
            select(RolePermission).where(
                RolePermission.role_id == role_id
            )
        )
        return list(result.scalars().all())

    async def get_by_role_and_permission(
        self,
        role_id: UUID,
        permission_id: UUID,
    ) -> RolePermission | None:
        result = await self.db.execute(
            select(RolePermission).where(
                RolePermission.role_id == role_id,
                RolePermission.permission_id == permission_id,
            )
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        role_id: UUID,
        permission_id: UUID,
    ) -> RolePermission:
        role_permission = RolePermission(
            role_id=role_id,
            permission_id=permission_id,
        )

        self.db.add(role_permission)
        await self.db.flush()

        return role_permission

    async def delete(
        self,
        role_id: UUID,
        permission_id: UUID,
    ) -> None:
        await self.db.execute(
            delete(RolePermission).where(
                RolePermission.role_id == role_id,
                RolePermission.permission_id == permission_id,
            )
        )
