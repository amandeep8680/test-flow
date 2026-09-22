
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_role import UserRole


class UserRoleRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_roles_by_user(
        self,
        user_id: UUID,
    ) -> list[UserRole]:
        result = await self.db.execute(
            select(UserRole).where(
                UserRole.user_id == user_id
            )
        )

        return list(result.scalars().all())

    async def get_by_user_and_role(
        self,
        user_id: UUID,
        role_id: UUID,
    ) -> UserRole | None:
        result = await self.db.execute(
            select(UserRole).where(
                UserRole.user_id == user_id,
                UserRole.role_id == role_id,
            )
        )

        return result.scalar_one_or_none()

    async def create(
        self,
        user_id: UUID,
        role_id: UUID,
    ) -> UserRole:
        user_role = UserRole(
            user_id=user_id,
            role_id=role_id,
        )

        self.db.add(user_role)
        await self.db.flush()

        return user_role

    async def delete(
        self,
        user_id: UUID,
        role_id: UUID,
    ) -> None:
        user_role = await self.get_by_user_and_role(
            user_id=user_id,
            role_id=role_id,
        )

        if user_role:
            await self.db.delete(user_role)
            await self.db.flush()

