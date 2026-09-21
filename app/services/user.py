from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import hash_password
from app.models.role import Role
from app.models.user import User
from app.models.user_role import UserRole
from app.repositories.user import UserRepository
from app.schemas.user import CreateUserRequest

from app.exception.exceptions import (
    ConflictException,
    BadRequestException,
)
from app.exception.messages import UserMessages


settings = get_settings()


class UserService:
    """
    Handles user management business logic.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repository = UserRepository(db)

    async def create_user(
        self,
        request: CreateUserRequest,
        organization_id,
    ):
        """
        Create a user inside the ADMIN's organization
        and assign the requested role.
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

        # 3. Find requested role.
        result = await self.db.execute(
            select(Role).where(
                Role.name == request.role.upper()
            )
        )

        role = result.scalar_one_or_none()

        if role is None:
            raise BadRequestException(
                UserMessages.INVALID_ROLE
            )

        # 4. Normal users cannot assign ADMIN.
        #
        # ADMIN creation is handled separately during
        # organization signup.
        if role.name == "ADMIN":
            raise BadRequestException(
                UserMessages.ADMIN_ROLE_NOT_ALLOWED
            )

        # 5. Get temporary password from environment.
        temporary_password = settings.default_temp_password

        # 6. Hash temporary password.
        password_hash = hash_password(
            temporary_password
        )

        # 7. Create user in the ADMIN's organization.
        # New users must change the temporary password.
        user = await self.user_repository.create(
            organization_id=organization_id,
            email=str(request.email).lower(),
            username=request.username,
            password_hash=password_hash,
            first_name=request.first_name,
            last_name=request.last_name,
            must_change_password=True,
        )

        # 8. Assign role.
        user_role = UserRole(
            user_id=user.id,
            role_id=role.id,
        )

        self.db.add(user_role)

        # 9. Commit user + role assignment together.
        await self.db.commit()

        await self.db.refresh(user)

        return user, role.name, temporary_password

