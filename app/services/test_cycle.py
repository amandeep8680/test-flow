import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.exception.exceptions import BadRequestException, NotFoundException
from app.exception.messages import TestCycleMessages
from app.models.test_cycle import TestCycle
from app.repositories.test_cycle import TestCycleRepository
from app.schemas.test_cycle import (
    TestCycleCreateRequest,
    TestCycleUpdateRequest,
)


class TestCycleService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = TestCycleRepository(db)

    async def get_test_cycle(
        self,
        cycle_id: uuid.UUID,
        project_id: uuid.UUID,
    ):
        test_cycle = await self.repository.get_by_id(
            cycle_id,
            project_id,
        )

        if test_cycle is None:
            raise NotFoundException(
                TestCycleMessages.TEST_CYCLE_NOT_FOUND
            )

        return test_cycle

    async def get_test_cycles(
        self,
        project_id: uuid.UUID,
        page: int,
        page_size: int,
        search: str | None,
        cycle_type: str | None,
        status: str | None,
        sort_by: str,
        sort_order: str,
    ):
        try:
            return await self.repository.get_all(
                project_id=project_id,
                page=page,
                page_size=page_size,
                search=search,
                cycle_type=cycle_type,
                status=status,
                sort_by=sort_by,
                sort_order=sort_order,
            )
        except ValueError:
            raise BadRequestException(
                TestCycleMessages.INVALID_SORT_FIELD
            )

    async def create_test_cycle(
        self,
        project_id: uuid.UUID,
        data: TestCycleCreateRequest,
    ):
        test_cycle = TestCycle(
            project_id=project_id,
            name=data.name,
            description=data.description,
            type=data.type,
            status=data.status,
        )

        test_cycle = await self.repository.create(test_cycle)

        await self.db.commit()
        await self.db.refresh(test_cycle)

        return test_cycle

    async def update_test_cycle(
        self,
        cycle_id: uuid.UUID,
        project_id: uuid.UUID,
        data: TestCycleUpdateRequest,
    ):
        test_cycle = await self.get_test_cycle(
            cycle_id,
            project_id,
        )

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(test_cycle, field, value)

        test_cycle = await self.repository.update(test_cycle)

        await self.db.commit()
        await self.db.refresh(test_cycle)

        return test_cycle

    async def delete_test_cycle(
        self,
        cycle_id: uuid.UUID,
        project_id: uuid.UUID,
    ):
        test_cycle = await self.get_test_cycle(
            cycle_id,
            project_id,
        )

        await self.repository.delete(test_cycle)
        await self.db.commit()