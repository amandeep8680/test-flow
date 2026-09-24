
import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.test_step import TestStep


class TestStepRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(
        self,
        step_id: uuid.UUID,
        test_case_id: uuid.UUID,
    ) -> TestStep | None:
        result = await self.db.execute(
            select(TestStep).where(
                TestStep.id == step_id,
                TestStep.test_case_id == test_case_id,
            )
        )

        return result.scalar_one_or_none()

    async def get_by_step_number(
        self,
        test_case_id: uuid.UUID,
        step_number: int,
    ) -> TestStep | None:
        result = await self.db.execute(
            select(TestStep).where(
                TestStep.test_case_id == test_case_id,
                TestStep.step_number == step_number,
            )
        )

        return result.scalar_one_or_none()

    async def get_all(
        self,
        test_case_id: uuid.UUID,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
        sort_by: str = "step_number",
        sort_order: str = "asc",
    ) -> tuple[list[TestStep], int]:

        filters = [
            TestStep.test_case_id == test_case_id,
        ]

        if search:
            search_pattern = f"%{search}%"

            filters.append(
                or_(
                    TestStep.action.ilike(search_pattern),
                    TestStep.expected_result.ilike(search_pattern),
                )
            )

        sort_columns = {
            "step_number": TestStep.step_number,
            "created_at": TestStep.created_at,
            "updated_at": TestStep.updated_at,
        }

        sort_column = sort_columns.get(sort_by)

        if sort_column is None:
            raise ValueError("Invalid sort field.")

        sort_column = (
            sort_column.asc()
            if sort_order == "asc"
            else sort_column.desc()
        )

        count_result = await self.db.execute(
            select(func.count(TestStep.id)).where(*filters)
        )

        total = count_result.scalar_one()

        offset = (page - 1) * page_size

        result = await self.db.execute(
            select(TestStep)
            .where(*filters)
            .order_by(sort_column)
            .offset(offset)
            .limit(page_size)
        )

        return list(result.scalars().all()), total

    async def get_all_for_reorder(
        self,
        test_case_id: uuid.UUID,
    ) -> list[TestStep]:
        result = await self.db.execute(
            select(TestStep)
            .where(TestStep.test_case_id == test_case_id)
            .order_by(TestStep.step_number.asc())
        )

        return list(result.scalars().all())

    async def create(self, test_step: TestStep) -> TestStep:
        self.db.add(test_step)

        await self.db.flush()
        await self.db.refresh(test_step)

        return test_step

    async def update(self, test_step: TestStep) -> TestStep:
        await self.db.flush()
        await self.db.refresh(test_step)

        return test_step

    async def delete(self, test_step: TestStep) -> None:
        await self.db.delete(test_step)

        await self.db.flush()
