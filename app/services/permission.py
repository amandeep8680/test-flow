
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission

from app.repositories.permission import PermissionRepository
from app.schemas.permission import PermissionCreateRequest


class PermissionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.permission_repository = PermissionRepository(db)

    async def get_permissions(self):
        return await self.permission_repository.get_all()

    async def get_permission_by_name(
        self,
        name: str,
    ):
        return await self.permission_repository.get_by_name(name)

    async def create_permission(
        self,
        request: PermissionCreateRequest,
    ):
        name = f"{request.resource}.{request.action}".lower()

        existing = await self.permission_repository.get_by_name(
            name
        )

        if existing:
            return existing

        permission = await self.permission_repository.create(
            name=name,
            description=request.description,
        )

        await self.db.flush()

        # Give the new permission to every ADMIN role.
        result = await self.db.execute(
            select(Role.id).where(
                Role.name == "ADMIN",
                Role.is_active.is_(True),
            )
        )

        admin_role_ids = result.scalars().all()

        for role_id in admin_role_ids:
            self.db.add(
                RolePermission(
                    role_id=role_id,
                    permission_id=permission.id,
                )
            )

        await self.db.commit()
        await self.db.refresh(permission)

        return permission
