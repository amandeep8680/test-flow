from uuid import UUID

from sqlalchemy import func, select
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
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
        is_active: bool | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[list[Project], int]:

        filters = [
            Project.organization_id == organization_id
        ]

        if search:
            search_pattern = f"%{search}%"

            filters.append(
                Project.name.ilike(search_pattern)
                | Project.key.ilike(search_pattern)
            )

        if is_active is not None:
            filters.append(
                Project.is_active.is_(is_active)
            )

        count_result = await self.db.execute(
            select(func.count(Project.id))
            .where(*filters)
        )

        total = count_result.scalar_one()

        sort_columns = {
            "created_at": Project.created_at,
            "updated_at": Project.updated_at,
            "name": Project.name,
            "key": Project.key,
        }

        sort_column = sort_columns.get(sort_by)

        if sort_column is None:
            raise ValueError("Invalid sort field.")

        sort_column = (
            sort_column.asc()
            if sort_order == "asc"
            else sort_column.desc()
        )

        offset = (page - 1) * page_size

        result = await self.db.execute(
            select(Project)
            .where(*filters)
            .order_by(sort_column)
            .offset(offset)
            .limit(page_size)
        )

        return list(result.scalars().all()), total

    # async def get_active_by_organization(
    #     self,
    #     organization_id: UUID,
    # ) -> list[Project]:
    #     result = await self.db.execute(
    #         select(Project)
    #         .where(
    #             Project.organization_id == organization_id,
    #             Project.is_active.is_(True),
    #         )
    #         .order_by(Project.created_at.desc())
    #     )

    #     return list(result.scalars().all())

    # async def get_inactive_by_organization(
    #     self,
    #     organization_id: UUID,
    # ) -> list[Project]:
    #     result = await self.db.execute(
    #         select(Project)
    #         .where(
    #             Project.organization_id == organization_id,
    #             Project.is_active.is_(False),
    #         )
    #         .order_by(Project.created_at.desc())
    #     )

    #     return list(result.scalars().all())

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
        project.is_active = False

        await self.db.flush()

        return project

    async def activate(
        self,
        project: Project,
    ) -> Project:
        project.is_active = True

        await self.db.flush()

        return project

    async def delete_permanently(
        self,
        project: Project,
    ) -> None:
        await self.db.delete(project)
        await self.db.flush()