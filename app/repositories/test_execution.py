from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.test_execution import TestExecution


class TestExecutionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(
        self,
        execution_id: UUID,
        test_cycle_id: UUID,
    ):
        result = await self.db.execute(
            select(TestExecution).where(
                TestExecution.id == execution_id,
                TestExecution.test_cycle_id == test_cycle_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        test_cycle_id: UUID,
        page: int = 1,
        page_size: int = 20,
        status: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ):
        filters = [
            TestExecution.test_cycle_id == test_cycle_id,
        ]

        if status:
            filters.append(TestExecution.status == status)

        sort_columns = {
            "created_at": TestExecution.created_at,
            "updated_at": TestExecution.updated_at,
            "executed_at": TestExecution.executed_at,
            "status": TestExecution.status,
        }

        sort_column = sort_columns.get(sort_by)

        if sort_column is None:
            raise ValueError

        sort_column = (
            sort_column.desc()
            if sort_order.lower() == "desc"
            else sort_column.asc()
        )

        count_result = await self.db.execute(
            select(func.count(TestExecution.id)).where(*filters)
        )

        total = count_result.scalar_one()

        offset = (page - 1) * page_size

        result = await self.db.execute(
            select(TestExecution)
            .where(*filters)
            .order_by(sort_column)
            .offset(offset)
            .limit(page_size)
        )

        return list(result.scalars().all()), total

    async def create(
        self,
        execution: TestExecution,
    ):
        self.db.add(execution)
        await self.db.flush()
        await self.db.refresh(execution)
        return execution

    async def update(
        self,
        execution: TestExecution,
    ):
        await self.db.flush()
        await self.db.refresh(execution)
        return execution

    async def delete(
        self,
        execution: TestExecution,
    ):
        await self.db.delete(execution)
        await self.db.flush()