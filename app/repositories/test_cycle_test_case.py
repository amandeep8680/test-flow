from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.test_case import TestCase
from app.models.test_cycle_test_case import TestCycleTestCase
from app.models.test_module import TestModule


class TestCycleTestCaseRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_mapping(
        self,
        cycle_id: UUID,
        test_case_id: UUID,
    ) -> TestCycleTestCase | None:
        result = await self.db.execute(
            select(TestCycleTestCase).where(
                TestCycleTestCase.test_cycle_id == cycle_id,
                TestCycleTestCase.test_case_id == test_case_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_cycle_test_cases(
        self,
        cycle_id: UUID,
    ):
        result = await self.db.execute(
            select(
                TestCase,
                TestModule.id.label("module_id"),
                TestModule.name.label("module_name"),
            )
            .join(
                TestCycleTestCase,
                TestCycleTestCase.test_case_id == TestCase.id,
            )
            .join(
                TestModule,
                TestModule.id == TestCase.module_id,
            )
            .where(
                TestCycleTestCase.test_cycle_id == cycle_id,
            )
            .order_by(
                TestModule.name.asc(),
                TestCase.created_at.desc(),
            )
        )

        return result.all()

    async def create_mapping(
        self,
        mapping: TestCycleTestCase,
    ) -> TestCycleTestCase:
        self.db.add(mapping)
        await self.db.flush()
        return mapping

    async def delete_mapping(
        self,
        mapping: TestCycleTestCase,
    ) -> None:
        await self.db.delete(mapping)
        await self.db.flush()