
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    """
    Handles database operations related to users.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_email(self, email: str) -> User | None:
        """
        Find a user by email.
        """

        result = await self.db.execute(
            select(User).where(
                User.email == email
            )
        )

        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: UUID) -> User | None:
        """
        Find a user by ID.
        """

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
        """
        Find a user by username within an organization.
        """

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
    ) -> list[User]:
        """
        Get all users within an organization.
        """

        result = await self.db.execute(
            select(User)
            .where(
                User.organization_id == organization_id
            )
            .order_by(User.created_at.desc())
        )

        return list(result.scalars().all())

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
        """
        Create a new user.

        This method does not commit the transaction.
        The service layer controls the transaction.
        """

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

