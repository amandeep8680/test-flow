from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.models.role import Role
from app.models.user import User
from app.models.user_role import UserRole
from app.repositories.organization import OrganizationRepository
from app.repositories.user import UserRepository
from app.schemas import user
from app.schemas import user
from app.schemas.auth import LoginRequest, OrganizationSignupRequest
from app.security.token import (
    create_access_token,
    create_refresh_token,
)

class AuthService:
    """
    Handles authentication-related business logic.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.organization_repository = OrganizationRepository(db)
        self.user_repository = UserRepository(db)

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
            raise ValueError("Organization slug already exists")

        # 2. Create organization.
        organization = await self.organization_repository.create(
            name=request.organization_name,
            slug=request.organization_slug,
        )

        # 3. Hash admin password using Argon2.
        password_hash = hash_password(request.admin_password)

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

        # Make sure admin_user.id is available before creating user_roles.
        await self.db.flush()

        # 5. Find the system ADMIN role.
        result = await self.db.execute(
            select(Role).where(Role.name == "ADMIN")
        )

        admin_role = result.scalar_one_or_none()

        if admin_role is None:
            raise ValueError("ADMIN role is not configured")

        # 6. Assign ADMIN role to initial user.
        user_role = UserRole(
            user_id=admin_user.id,
            role_id=admin_role.id,
        )

        self.db.add(user_role)

        # 7. Commit organization + user + role assignment together.
        await self.db.commit()

        # Refresh objects after commit.
        await self.db.refresh(organization)
        await self.db.refresh(admin_user)

        return organization, admin_user




    async def login(self, request: LoginRequest):
        """
        Authenticate a user and generate access and refresh tokens.
        """

        # 1. Find user by email.
        user = await self.user_repository.get_by_email(
            str(request.email).lower()
        )

        # Do not reveal whether the email exists.
        if user is None:
            raise ValueError("Invalid email or password")

        # 2. Check whether user is active.
        if not user.is_active:
            raise ValueError("User account is inactive")

        # 3. Verify password against Argon2 hash.
        if not verify_password(
            request.password,
            user.password_hash,
        ):
            raise ValueError("Invalid email or password")

        # 4. Check whether user's organization is active.
        organization = await self.organization_repository.get_by_id(
            user.organization_id
        )

        if organization is None or not organization.is_active:
            raise ValueError("Organization is inactive")

        # 5. Load user's roles.
        result = await self.db.execute(
            select(Role)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user.id)
        )

        roles = result.scalars().all()

        role_names = [role.name for role in roles]

        # 6. Update last successful login time.
        user.last_login_at = datetime.now(timezone.utc)

        # 7. Generate access token.
        access_token = create_access_token(
            user_id=user.id,
            organization_id=user.organization_id,
        )

        # 8. Generate refresh token.
        refresh_token = create_refresh_token(
            user_id=user.id,
            organization_id=user.organization_id,
        )

        # 9. Persist last_login_at.
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
        if not verify_password(current_password, user.password_hash):
            raise ValueError("Current password is incorrect")

        if current_password == new_password:
            raise ValueError("New password must be different from current password")

        user.password_hash = hash_password(new_password)

        # Password successfully changed
        user.must_change_password = True

        await self.db.commit()
        await self.db.refresh(user)

        return user