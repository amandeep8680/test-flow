
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.role import Role
from app.models.user import User

from app.repositories.role import RoleRepository
from app.repositories.user_role import UserRoleRepository


class UserRoleService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.role_repository = RoleRepository(db)
        self.user_role_repository = UserRoleRepository(db)

    async def assign_role(
        self,
        user_id: UUID,
        role_id: UUID,
        organization_id: UUID,
    ):
        # Make sure the target user belongs to the same organization.
        result = await self.db.execute(
            select(User).where(
                User.id == user_id,
                User.organization_id == organization_id,
            )
        )

        user = result.scalar_one_or_none()

        if user is None:
            return None

        # Make sure the role belongs to the same organization.
        role = await self.role_repository.get_by_id(
            role_id=role_id,
            organization_id=organization_id,
        )

        if role is None:
            return None

        existing = await self.user_role_repository.get_by_user_and_role(
            user_id=user_id,
            role_id=role_id,
        )

        if existing:
            return existing

        user_role = await self.user_role_repository.create(
            user_id=user_id,
            role_id=role_id,
        )

        await self.db.commit()
        await self.db.refresh(user_role)

        return user_role

    async def remove_role(
        self,
        user_id: UUID,
        role_id: UUID,
        organization_id: UUID,
    ) -> bool:
        # Make sure the target user belongs to the same organization.
        result = await self.db.execute(
            select(User).where(
                User.id == user_id,
                User.organization_id == organization_id,
            )
        )

        user = result.scalar_one_or_none()

        if user is None:
            return False

        # Make sure the role belongs to the same organization.
        role = await self.role_repository.get_by_id(
            role_id=role_id,
            organization_id=organization_id,
        )

        if role is None:
            return False

        existing = await self.user_role_repository.get_by_user_and_role(
            user_id=user_id,
            role_id=role_id,
        )

        if existing is None:
            return False

        await self.user_role_repository.delete(
            user_id=user_id,
            role_id=role_id,
        )

        await self.db.commit()

        return True

    async def get_user_roles(
        self,
        user_id: UUID,
        organization_id: UUID,
    ):
        # Make sure the target user belongs to the same organization.
        result = await self.db.execute(
            select(User).where(
                User.id == user_id,
                User.organization_id == organization_id,
            )
        )

        user = result.scalar_one_or_none()

        if user is None:
            return None

        return await self.user_role_repository.get_roles_by_user(
            user_id=user_id,
        )
