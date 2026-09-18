from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization


class OrganizationRepository:
    """
    Handles database operations related to organizations.

    Business rules and application logic should stay
    in the service layer.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_slug(self, slug: str) -> Organization | None:
        """
        Find an organization by its unique slug.
        """

        result = await self.db.execute(
            select(Organization).where(
                Organization.slug == slug
            )
        )

        return result.scalar_one_or_none()

    async def get_by_id(self, organization_id: UUID) -> Organization | None:
        """
        Find an organization by its ID.
        """

        result = await self.db.execute(
            select(Organization).where(
                Organization.id == organization_id
            )
        )

        return result.scalar_one_or_none()

    async def create(
        self,
        name: str,
        slug: str,
    ) -> Organization:
        """
        Create a new organization.

        This method does not commit the transaction.
        The service layer controls the transaction.
        """

        organization = Organization(
            name=name,
            slug=slug,
        )

        self.db.add(organization)

        await self.db.flush()

        return organization