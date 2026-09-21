from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password

from app.models.role import Role
from app.models.user import User
from app.models.user_role import UserRole

from app.repositories.organization import OrganizationRepository
from app.repositories.user import UserRepository

from app.schemas.auth import (
    LoginRequest,
    OrganizationSignupRequest,
)

from app.services.token import TokenService

from app.exception.exceptions import (
    UnauthorizedException,
    ForbiddenException,
    ConflictException,
)

from app.exception.messages import (
    AuthMessages,
    OrganizationMessages,
)


class AuthService:
    """
    Handles authentication-related business logic.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.organization_repository = OrganizationRepository(db)
        self.user_repository = UserRepository(db)
        self.token_service = TokenService(db)

    async def register_organization(
        self,
        request: OrganizationSignupRequest,
    ):
        """
        Create an organization and its initial ADMIN user
        in a single database transaction.
        """

        # 1. Check whether organization slug already exists.
        existing_organization = (
            await self.organization_repository.get_by_slug(
                request.organization_slug
            )
        )

        if existing_organization:
            raise ConflictException(
                OrganizationMessages.SLUG_ALREADY_EXISTS
            )

        # 2. Create organization.
        organization = await self.organization_repository.create(
            name=request.organization_name,
            slug=request.organization_slug,
        )

        # 3. Hash admin password using Argon2.
        password_hash = hash_password(
            request.admin_password
        )

        # 4. Create initial admin user.
        admin_user = User(
            organization_id=organization.id,
            email=str(request.admin_email).lower(),
            username=request.admin_username,
            password_hash=password_hash,
            first_name=request.admin_first_name,
            last_name=request.admin_last_name,
            is_active=True,
            must_change_password=False,
        )

        self.db.add(admin_user)

        await self.db.flush()

        # 5. Find the system ADMIN role.
        result = await self.db.execute(
            select(Role).where(Role.name == "ADMIN")
        )

        admin_role = result.scalar_one_or_none()

        if admin_role is None:
            raise ConflictException(
                AuthMessages.ADMIN_ROLE_NOT_CONFIGURED
            )

        # 6. Assign ADMIN role to initial user.
        user_role = UserRole(
            user_id=admin_user.id,
            role_id=admin_role.id,
        )

        self.db.add(user_role)

        # 7. Commit organization + user + role assignment.
        await self.db.commit()

        await self.db.refresh(organization)
        await self.db.refresh(admin_user)

        return organization, admin_user

    async def login(
        self,
        request: LoginRequest,
    ):
        """
        Authenticate a user and generate
        access and refresh tokens.
        """

        # 1. Find user by email.
        user = await self.user_repository.get_by_email(
            str(request.email).lower()
        )

        if user is None:
            raise UnauthorizedException(
                AuthMessages.INVALID_CREDENTIALS
            )

        # 2. Check whether user is active.
        if not user.is_active:
            raise ForbiddenException(
                AuthMessages.USER_INACTIVE
            )

        # 3. Verify password.
        if not verify_password(
            request.password,
            user.password_hash,
        ):
            raise UnauthorizedException(
                AuthMessages.INVALID_CREDENTIALS
            )

        # 4. Check organization status.
        organization = await self.organization_repository.get_by_id(
            user.organization_id
        )

        if organization is None or not organization.is_active:
            raise ForbiddenException(
                AuthMessages.ORGANIZATION_INACTIVE
            )

        # 5. Load user's roles.
        result = await self.db.execute(
            select(Role)
            .join(
                UserRole,
                UserRole.role_id == Role.id,
            )
            .where(
                UserRole.user_id == user.id
            )
        )

        roles = result.scalars().all()

        role_names = [
            role.name
            for role in roles
        ]

        # 6. Update last successful login.
        user.last_login_at = datetime.now(
            timezone.utc
        )

        # 7. Create and save tokens.
        access_token, refresh_token = (
            await self.token_service.create_tokens(
                user_id=user.id,
                organization_id=user.organization_id,
            )
        )

        # 8. Commit login changes + refresh token.
        await self.db.commit()

        await self.db.refresh(user)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": user,
            "roles": role_names,
        }

    async def change_password(
        self,
        user: User,
        current_password: str,
        new_password: str,
    ):
        """
        Change the user's password.
        """

        if not verify_password(
            current_password,
            user.password_hash,
        ):
            raise UnauthorizedException(
                AuthMessages.CURRENT_PASSWORD_INCORRECT
            )

        if current_password == new_password:
            raise ConflictException(
                AuthMessages.NEW_PASSWORD_SAME_AS_CURRENT
            )

        user.password_hash = hash_password(
            new_password
        )

        # Keep existing application behavior.
        user.must_change_password = False

        await self.db.commit()
        await self.db.refresh(user)

        return user