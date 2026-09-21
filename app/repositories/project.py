from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project


class ProjectRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        organization_id: UUID,
        name: str,
        key: str,
        description: str | None = None,
    ) -> Project:
        project = Project(
            organization_id=organization_id,
            name=name,
            key=key,
            description=description,
        )

        self.db.add(project)
        await self.db.flush()

        return project

    async def get_by_id(
        self,
        project_id: UUID,
    ) -> Project | None:
        result = await self.db.execute(
            select(Project).where(
                Project.id == project_id
            )
        )

        return result.scalar_one_or_none()

    async def get_by_key(
        self,
        organization_id: UUID,
        key: str,
    ) -> Project | None:
        result = await self.db.execute(
            select(Project).where(
                Project.organization_id == organization_id,
                Project.key == key,
            )
        )

        return result.scalar_one_or_none()

    async def get_all_by_organization(
        self,
        organization_id: UUID,
        search: str | None = None,
        is_active: bool | None = None,
    ) -> list[Project]:
        """
        Get projects for the organization.

        Optional filters:
        - search: Search by project name or key.
        - is_active: Filter by active/inactive status.
        """

        query = select(Project).where(
            Project.organization_id == organization_id,
        )

        if search:
            search_pattern = f"%{search}%"

            query = query.where(
                Project.name.ilike(search_pattern)
                | Project.key.ilike(search_pattern)
            )

        if is_active is not None:
            query = query.where(
                Project.is_active.is_(is_active)
            )

        query = query.order_by(
            Project.created_at.desc()
        )

        result = await self.db.execute(query)

        return list(result.scalars().all())

    async def get_active_by_organization(
        self,
        organization_id: UUID,
    ) -> list[Project]:
        """
        Get only active projects for the organization.
        """

        result = await self.db.execute(
            select(Project)
            .where(
                Project.organization_id == organization_id,
                Project.is_active.is_(True),
            )
            .order_by(Project.created_at.desc())
        )

        return list(result.scalars().all())

    async def get_inactive_by_organization(
        self,
        organization_id: UUID,
    ) -> list[Project]:
        """
        Get only inactive projects for the organization.
        """

        result = await self.db.execute(
            select(Project)
            .where(
                Project.organization_id == organization_id,
                Project.is_active.is_(False),
            )
            .order_by(Project.created_at.desc())
        )

        return list(result.scalars().all())

    async def update(
        self,
        project: Project,
        name: str | None = None,
        description: str | None = None,
    ) -> Project:
        if name is not None:
            project.name = name

        if description is not None:
            project.description = description

        await self.db.flush()

        return project

    async def deactivate(
        self,
        project: Project,
    ) -> Project:
        """
        Mark project as inactive.
        """

        project.is_active = False

        await self.db.flush()

        return project

    async def activate(
        self,
        project: Project,
    ) -> Project:
        """
        Mark project as active.
        """

        project.is_active = True

        await self.db.flush()

        return project

    async def delete_permanently(
        self,
        project: Project,
    ) -> None:
        """
        Permanently delete the project from the database.
        """

        await self.db.delete(project)
        await self.db.flush()

