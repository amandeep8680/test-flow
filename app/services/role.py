
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.role import RoleRepository
from app.schemas.role import RoleCreateRequest, RoleUpdateRequest


class RoleService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.role_repository = RoleRepository(db)

    async def get_roles(
        self,
        organization_id: UUID,
    ):
        return await self.role_repository.get_all(
            organization_id=organization_id,
        )

    async def get_role(
        self,
        role_id: UUID,
        organization_id: UUID,
    ):
        return await self.role_repository.get_by_id(
            role_id=role_id,
            organization_id=organization_id,
        )

    async def create_role(
        self,
        request: RoleCreateRequest,
        organization_id: UUID,
    ):
        existing_role = await self.role_repository.get_by_name(
            name=request.name,
            organization_id=organization_id,
        )

        if existing_role:
            return existing_role

        role = await self.role_repository.create(
            organization_id=organization_id,
            name=request.name,
            description=request.description,
        )

        await self.db.commit()
        await self.db.refresh(role)

        return role

    async def update_role(
        self,
        role_id: UUID,
        organization_id: UUID,
        request: RoleUpdateRequest,
    ):
        role = await self.role_repository.get_by_id(
            role_id=role_id,
            organization_id=organization_id,
        )

        if role is None:
            return None

        if request.name is not None:
            role.name = request.name

        if request.description is not None:
            role.description = request.description

        if request.is_active is not None:
            role.is_active = request.is_active

        await self.db.commit()
        await self.db.refresh(role)

        return role

