from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.test_module import TestModule


class TestModuleRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(
        self,
        module_id: UUID,
        project_id: UUID,
    ) -> TestModule | None:
        result = await self.db.execute(
            select(TestModule).where(
                TestModule.id == module_id,
                TestModule.project_id == project_id,
            )
        )

        return result.scalar_one_or_none()

    async def get_all(
        self,
        project_id: UUID,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[list[TestModule], int]:

        filters = [
            TestModule.project_id == project_id,
        ]

        if search:
            filters.append(
                TestModule.name.ilike(f"%{search}%")
            )

        sort_columns = {
            "name": TestModule.name,
            "created_at": TestModule.created_at,
            "updated_at": TestModule.updated_at,
        }

        sort_column = sort_columns.get(sort_by)

        if sort_column is None:
            raise ValueError

        order = (
            sort_column.asc()
            if sort_order.lower() == "asc"
            else sort_column.desc()
        )

        count_result = await self.db.execute(
            select(func.count(TestModule.id))
            .where(*filters)
        )

        total = count_result.scalar_one()

        result = await self.db.execute(
            select(TestModule)
            .where(*filters)
            .order_by(order)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        return list(result.scalars().all()), total

    async def create(
        self,
        module: TestModule,
    ) -> TestModule:
        self.db.add(module)
        await self.db.flush()
        await self.db.refresh(module)

        return module

    async def update(
        self,
        module: TestModule,
    ) -> TestModule:
        await self.db.flush()
        await self.db.refresh(module)

        return module

    async def delete(
        self,
        module: TestModule,
    ) -> None:
        await self.db.delete(module)
        await self.db.flush()