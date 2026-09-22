
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission

from app.repositories.organization import OrganizationRepository
from app.exception.exceptions import ConflictException
from app.exception.messages import OrganizationMessages


class OrganizationService:
    """
    Handles business logic related to organizations.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.organization_repository = OrganizationRepository(db)

    async def create_organization(
        self,
        name: str,
        slug: str,
    ) -> Organization:
        """
        Create a new organization.

        Organization slug must be unique.
        """

        existing_organization = (
            await self.organization_repository.get_by_slug(slug)
        )

        if existing_organization:
            raise ConflictException(
                OrganizationMessages.SLUG_ALREADY_EXISTS
            )

        # Create organization
        organization = await self.organization_repository.create(
            name=name,
            slug=slug,
        )

        await self.db.flush()

        # Create default ADMIN role
        admin_role = Role(
            organization_id=organization.id,
            name="ADMIN",
            description="Organization administrator",
            is_active=True,
        )

        self.db.add(admin_role)

        await self.db.flush()

        # Get all registered permissions
        result = await self.db.execute(
            select(Permission)
        )

        permissions = result.scalars().all()

        # Give ADMIN all permissions
        for permission in permissions:
            self.db.add(
                RolePermission(
                    role_id=admin_role.id,
                    permission_id=permission.id,
                )
            )

        await self.db.commit()
        await self.db.refresh(organization)

        return organization

