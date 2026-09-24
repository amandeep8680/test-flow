from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.test_cycle import TestCycle


class TestCycleRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(
        self,
        cycle_id: UUID,
        project_id: UUID,
    ) -> TestCycle | None:
        result = await self.db.execute(
            select(TestCycle).where(
                TestCycle.id == cycle_id,
                TestCycle.project_id == project_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        project_id: UUID,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
        cycle_type: str | None = None,
        status: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ):
        filters = [TestCycle.project_id == project_id]

        if search:
            search_term = f"%{search}%"
            filters.append(
                or_(
                    TestCycle.name.ilike(search_term),
                    TestCycle.description.ilike(search_term),
                )
            )

        if cycle_type:
            filters.append(TestCycle.type == cycle_type)

        if status:
            filters.append(TestCycle.status == status)

        sort_columns = {
            "created_at": TestCycle.created_at,
            "updated_at": TestCycle.updated_at,
            "name": TestCycle.name,
            "type": TestCycle.type,
            "status": TestCycle.status,
        }

        if sort_by not in sort_columns:
            raise ValueError("Invalid sort field.")

        sort_column = sort_columns[sort_by]

        if sort_order == "desc":
            sort_column = sort_column.desc()
        else:
            sort_column = sort_column.asc()

        count_result = await self.db.execute(
            select(func.count(TestCycle.id)).where(*filters)
        )
        total = count_result.scalar_one()

        offset = (page - 1) * page_size

        result = await self.db.execute(
            select(TestCycle)
            .where(*filters)
            .order_by(sort_column)
            .offset(offset)
            .limit(page_size)
        )

        return result.scalars().all(), total

    async def create(self, test_cycle: TestCycle) -> TestCycle:
        self.db.add(test_cycle)
        await self.db.flush()
        await self.db.refresh(test_cycle)
        return test_cycle

    async def update(self, test_cycle: TestCycle) -> TestCycle:
        await self.db.flush()
        await self.db.refresh(test_cycle)
        return test_cycle

    async def delete(self, test_cycle: TestCycle) -> None:
        await self.db.delete(test_cycle)
        await self.db.flush()