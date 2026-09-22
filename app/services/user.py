from app.core.config import get_settings
from app.core.security import hash_password

from app.repositories.user import UserRepository

from app.schemas.user import CreateUserRequest

from app.exception.exceptions import ConflictException
from app.exception.messages import UserMessages

from uuid import UUID

from sqlalchemy import select

from app.models.role import Role
from app.models.user_role import UserRole
settings = get_settings()


class UserService:
    """
    Handles user management business logic.
    """

    def __init__(self, db):
        self.db = db
        self.user_repository = UserRepository(db)

    async def create_user(
        self,
        request: CreateUserRequest,
        organization_id,
    ):
        """
        Create a user inside the ADMIN's organization.

        Role assignment is handled separately through
        the User Role API.
        """

        # 1. Check duplicate email.
        existing_user = await self.user_repository.get_by_email(
            str(request.email).lower()
        )

        if existing_user:
            raise ConflictException(
                UserMessages.EMAIL_ALREADY_EXISTS
            )

        # 2. Check duplicate username within organization.
        existing_username = await self.user_repository.get_by_username(
            username=request.username,
            organization_id=organization_id,
        )

        if existing_username:
            raise ConflictException(
                UserMessages.USERNAME_ALREADY_EXISTS
            )

        # 3. Get temporary password.
        temporary_password = settings.default_temp_password

        # 4. Hash temporary password.
        password_hash = hash_password(
            temporary_password
        )

        # 5. Create user.
        user = await self.user_repository.create(
            organization_id=organization_id,
            email=str(request.email).lower(),
            username=request.username,
            password_hash=password_hash,
            first_name=request.first_name,
            last_name=request.last_name,
            must_change_password=True,
        )

        # 6. Commit user creation only.
        await self.db.commit()

        await self.db.refresh(user)

        return user, temporary_password

    async def get_users(
        self,
        organization_id,
        exclude_user_id,
    ):
        users = await self.user_repository.get_all(
            organization_id=organization_id,
            exclude_user_id=exclude_user_id,
        )

        return users

    async def get_user_with_roles(
    self,
    user_id: UUID,
    ):
        user = await self.user_repository.get_by_id(user_id)

        if user is None:
            return None

        result = await self.db.execute(
            select(Role.name)
            .join(
                UserRole,
                UserRole.role_id == Role.id,
            )
            .where(
                UserRole.user_id == user.id
        )
    )

        roles = list(result.scalars().all())

        return user, roles