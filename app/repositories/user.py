from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.user_role import UserRole
from app.models.role import Role


class UserRepository:
    """
    Handles database operations related to users.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(
            select(User).where(
                User.email == email
            )
        )

        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: UUID) -> User | None:
        result = await self.db.execute(
            select(User).where(
                User.id == user_id
            )
        )

        return result.scalar_one_or_none()

    async def get_by_username(
        self,
        username: str,
        organization_id: UUID,
    ) -> User | None:
        result = await self.db.execute(
            select(User).where(
                User.username == username,
                User.organization_id == organization_id,
            )
        )

        return result.scalar_one_or_none()

    async def get_all(
        self,
        organization_id: UUID,
        exclude_user_id: UUID | None = None,
    ) -> list[tuple[User, list[str]]]:
        """
        Get all users within an organization,
        optionally excluding the current user,
        along with their role names.
        """

        query = (
            select(User, Role.name)
            .outerjoin(
                UserRole,
                UserRole.user_id == User.id,
            )
            .outerjoin(
                Role,
                Role.id == UserRole.role_id,
            )
            .where(
                User.organization_id == organization_id
            )
            .order_by(User.created_at.desc())
        )

        if exclude_user_id:
            query = query.where(
                User.id != exclude_user_id
            )

        result = await self.db.execute(query)

        rows = result.all()

        users: dict[UUID, tuple[User, list[str]]] = {}

        for user, role_name in rows:
            if user.id not in users:
                users[user.id] = (user, [])

            if role_name:
                users[user.id][1].append(role_name)

        return list(users.values())

    async def create(
        self,
        organization_id: UUID,
        email: str,
        username: str,
        password_hash: str,
        first_name: str,
        last_name: str,
        must_change_password: bool = True,
    ) -> User:

        user = User(
            organization_id=organization_id,
            email=email,
            username=username,
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name,
            is_active=True,
            must_change_password=must_change_password,
        )

        self.db.add(user)

        await self.db.flush()

        return user