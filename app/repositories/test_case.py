import uuid
from sqlalchemy import func, or_, select
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
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
        status: str | None = None,
        priority: str | None = None,
        tag_id: uuid.UUID | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[list[TestCase], int]:

        filters = [TestCase.project_id == project_id]

        if search:
            search_pattern = f"%{search}%"
            filters.append(
                or_(
                    TestCase.title.ilike(search_pattern),
                    TestCase.description.ilike(search_pattern),
                )
            )

        if status:
            filters.append(TestCase.status == status)

        if priority:
            filters.append(TestCase.priority == priority)

        if tag_id:
            filters.append(
                TestCase.id.in_(
                    select(TestCaseTag.test_case_id).where(
                        TestCaseTag.tag_id == tag_id
                    )
                )
            )

        count_result = await self.db.execute(
            select(func.count(TestCase.id))
            .where(*filters)
        )
        total = count_result.scalar_one()

        sort_columns = {
            "created_at": TestCase.created_at,
            "updated_at": TestCase.updated_at,
            "title": TestCase.title,
            "priority": TestCase.priority,
            "status": TestCase.status,
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
            select(TestCase)
            .options(
                selectinload(TestCase.test_case_tags)
                .selectinload(TestCaseTag.tag)
            )
            .where(*filters)
            .order_by(sort_column)
            .offset(offset)
            .limit(page_size)
        )

        return list(result.scalars().all()), total


    async def create(self, test_case: TestCase) -> TestCase:
        self.db.add(test_case)
        await self.db.flush()
        await self.db.refresh(test_case)
        return test_case

    async def update(self, test_case: TestCase) -> TestCase:
        await self.db.flush()
        await self.db.refresh(test_case)
        return test_case

    async def delete(self, test_case: TestCase) -> None:
        await self.db.delete(test_case)
        await self.db.flush()