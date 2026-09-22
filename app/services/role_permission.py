
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.permission import PermissionRepository
from app.repositories.role import RoleRepository
from app.repositories.role_permission import RolePermissionRepository


class RolePermissionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.role_repository = RoleRepository(db)
        self.permission_repository = PermissionRepository(db)
        self.role_permission_repository = RolePermissionRepository(db)

    async def assign_permission(
        self,
        role_id: UUID,
        permission_id: UUID,
        organization_id: UUID,
    ):
        role = await self.role_repository.get_by_id(
            role_id=role_id,
            organization_id=organization_id,
        )

        if role is None:
            return None

        permission = await self.permission_repository.get_by_id(
            permission_id=permission_id,
        )

        if permission is None:
            return None

        existing = await self.role_permission_repository.get_by_role_and_permission(
            role_id=role_id,
            permission_id=permission_id,
        )

        if existing:
            return existing

        role_permission = await self.role_permission_repository.create(
            role_id=role_id,
            permission_id=permission_id,
        )

        await self.db.commit()
        await self.db.refresh(role_permission)

        return role_permission

    async def remove_permission(
        self,
        role_id: UUID,
        permission_id: UUID,
        organization_id: UUID,
    ) -> bool:
        role = await self.role_repository.get_by_id(
            role_id=role_id,
            organization_id=organization_id,
        )

        if role is None:
            return False

        existing = await self.role_permission_repository.get_by_role_and_permission(
            role_id=role_id,
            permission_id=permission_id,
        )

        if existing is None:
            return False

        await self.role_permission_repository.delete(
            role_id=role_id,
            permission_id=permission_id,
        )

        await self.db.commit()

        return True

    async def get_role_permissions(
        self,
        role_id: UUID,
        organization_id: UUID,
    ):
        role = await self.role_repository.get_by_id(
            role_id=role_id,
            organization_id=organization_id,
        )

        if role is None:
            return None

        return await self.role_permission_repository.get_permissions_by_role(
            role_id=role_id,
        )

