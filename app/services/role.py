
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.repositories.role import RoleRepository
from app.schemas.role import RoleCreateRequest, RoleUpdateRequest
from app.models.user_role import UserRole
from app.exception.exceptions import BadRequestException
from app.exception.messages import RoleMessages
from app.models.user_role import UserRole
from sqlalchemy import select


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

    async def delete_role(
            self,
            role_id: UUID,
            organization_id: UUID,
            current_user_id: UUID,
        ):
            role = await self.role_repository.get_by_id(
                role_id=role_id,
                organization_id=organization_id,
            )

            if role is None:
                raise NotFoundException(
                    RoleMessages.ROLE_NOT_FOUND
                )

            result = await self.db.execute(
                select(UserRole).where(
                    UserRole.role_id == role_id,
                    UserRole.user_id == current_user_id,
                )
            )

            if result.scalar_one_or_none():
                raise BadRequestException(
                    RoleMessages.ROLE_CANNOT_DELETE_OWN
                )

            await self.role_repository.delete(role)

            await self.db.commit()