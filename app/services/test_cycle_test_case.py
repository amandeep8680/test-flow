from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.exception.exceptions import ConflictException, NotFoundException
from app.exception.messages import TestCaseMessages, TestCycleMessages
from app.models.test_cycle_test_case import TestCycleTestCase
from app.repositories.test_case import TestCaseRepository
from app.repositories.test_cycle import TestCycleRepository
from app.repositories.test_cycle_test_case import TestCycleTestCaseRepository
from app.schemas.test_cycle_test_case import TestCycleTestCaseAddRequest


class TestCycleTestCaseService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = TestCycleTestCaseRepository(db)
        self.cycle_repository = TestCycleRepository(db)
        self.test_case_repository = TestCaseRepository(db)

    async def _validate_cycle(
        self,
        cycle_id: UUID,
        project_id: UUID,
    ):
        cycle = await self.cycle_repository.get_by_id(
            cycle_id,
            project_id,
        )

        if cycle is None:
            raise NotFoundException(
                TestCycleMessages.TEST_CYCLE_NOT_FOUND
            )

        return cycle

    async def add_test_cases(
        self,
        cycle_id: UUID,
        project_id: UUID,
        data: TestCycleTestCaseAddRequest,
    ):
        await self._validate_cycle(
            cycle_id,
            project_id,
        )

        if len(data.test_case_ids) != len(set(data.test_case_ids)):
            raise ConflictException(
                TestCaseMessages.TEST_CASE_ALREADY_EXISTS
            )

        added = []

        for test_case_id in data.test_case_ids:
            test_case = await self.test_case_repository.get_by_id(
                test_case_id,
                project_id,
            )

            if test_case is None:
                raise NotFoundException(
                    TestCaseMessages.TEST_CASE_NOT_FOUND
                )

            existing = await self.repository.get_mapping(
                cycle_id,
                test_case_id,
            )

            if existing:
                raise ConflictException(
                    TestCaseMessages.TEST_CASE_ALREADY_EXISTS
                )

            mapping = TestCycleTestCase(
                test_cycle_id=cycle_id,
                test_case_id=test_case_id,
            )

            await self.repository.create_mapping(mapping)
            added.append(test_case)

        await self.db.commit()

        return added

    async def get_test_cases(
        self,
        cycle_id: UUID,
        project_id: UUID,
    ):
        await self._validate_cycle(
            cycle_id,
            project_id,
        )

        return await self.repository.get_cycle_test_cases(
            cycle_id
        )

    async def remove_test_case(
        self,
        cycle_id: UUID,
        project_id: UUID,
        test_case_id: UUID,
    ):
        await self._validate_cycle(
            cycle_id,
            project_id,
        )

        test_case = await self.test_case_repository.get_by_id(
            test_case_id,
            project_id,
        )

        if test_case is None:
            raise NotFoundException(
                TestCaseMessages.TEST_CASE_NOT_FOUND
            )

        mapping = await self.repository.get_mapping(
            cycle_id,
            test_case_id,
        )

        if mapping is None:
            raise NotFoundException(
                TestCaseMessages.TEST_CASE_NOT_FOUND
            )

        await self.repository.delete_mapping(mapping)
        await self.db.commit()