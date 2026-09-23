import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.test_case import TestCase
from app.models.test_case_tag import TestCaseTag


class TestCaseRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(
        self,
        test_case_id: uuid.UUID,
        project_id: uuid.UUID,
    ) -> TestCase | None:
        result = await self.db.execute(
            select(TestCase)
            .options(
                selectinload(TestCase.test_case_tags)
                .selectinload(TestCaseTag.tag)
            )
            .where(
                TestCase.id == test_case_id,
                TestCase.project_id == project_id,
            )
        )

        return result.scalar_one_or_none()

    async def get_all(
        self,
        project_id: uuid.UUID,
    ) -> list[TestCase]:
        result = await self.db.execute(
            select(TestCase)
            .options(
                selectinload(TestCase.test_case_tags)
                .selectinload(TestCaseTag.tag)
            )
            .where(
                TestCase.project_id == project_id,
            )
            .order_by(TestCase.created_at.desc())
        )

        return list(result.scalars().all())

    async def create(
        self,
        test_case: TestCase,
    ) -> TestCase:
        self.db.add(test_case)

        await self.db.flush()
        await self.db.refresh(test_case)

        return test_case

    async def update(
        self,
        test_case: TestCase,
    ) -> TestCase:
        await self.db.flush()
        await self.db.refresh(test_case)

        return test_case

    async def delete(
        self,
        test_case: TestCase,
    ) -> None:
        await self.db.delete(test_case)
        await self.db.flush()