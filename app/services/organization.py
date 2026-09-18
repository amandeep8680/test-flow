from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization
from app.repositories.organization import OrganizationRepository


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
            raise ValueError("Organization slug already exists")

        organization = await self.organization_repository.create(
            name=name,
            slug=slug,
        )

        return organization