
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.exception.exceptions import (
    BadRequestException,
    ConflictException,
    NotFoundException,
)
from app.exception.messages import TestCaseMessages, TestStepMessages
from app.models.test_step import TestStep
from app.repositories.test_case import TestCaseRepository
from app.repositories.test_step import TestStepRepository
from app.schemas.test_step import (
    TestStepCreateRequest,
    TestStepUpdateRequest,
)


class TestStepService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = TestStepRepository(db)
        self.test_case_repository = TestCaseRepository(db)

    async def _validate_test_case(
        self,
        test_case_id: uuid.UUID,
        project_id: uuid.UUID,
    ):
        test_case = await self.test_case_repository.get_by_id(
            test_case_id=test_case_id,
            project_id=project_id,
        )

        if test_case is None:
            raise NotFoundException(
                TestCaseMessages.TEST_CASE_NOT_FOUND
            )

        return test_case

    async def get_test_step(
        self,
        step_id: uuid.UUID,
        test_case_id: uuid.UUID,
        project_id: uuid.UUID,
    ) -> TestStep | None:

        await self._validate_test_case(
            test_case_id=test_case_id,
            project_id=project_id,
        )

        return await self.repository.get_by_id(
            step_id=step_id,
            test_case_id=test_case_id,
        )

    async def get_test_steps(
        self,
        test_case_id: uuid.UUID,
        project_id: uuid.UUID,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
        sort_by: str = "step_number",
        sort_order: str = "asc",
    ):

        await self._validate_test_case(
            test_case_id=test_case_id,
            project_id=project_id,
        )

        try:
            return await self.repository.get_all(
                test_case_id=test_case_id,
                page=page,
                page_size=page_size,
                search=search,
                sort_by=sort_by,
                sort_order=sort_order,
            )
        except ValueError:
            raise BadRequestException(
                TestStepMessages.INVALID_SORT_FIELD
            )

    async def create_test_step(
        self,
        test_case_id: uuid.UUID,
        project_id: uuid.UUID,
        data: TestStepCreateRequest,
    ) -> TestStep:

        await self._validate_test_case(
            test_case_id=test_case_id,
            project_id=project_id,
        )

        existing_step = await self.repository.get_by_step_number(
            test_case_id=test_case_id,
            step_number=data.step_number,
        )

        if existing_step is not None:
            raise ConflictException(
                TestStepMessages.TEST_STEP_ALREADY_EXISTS
            )

        test_step = TestStep(
            test_case_id=test_case_id,
            step_number=data.step_number,
            action=data.action,
            expected_result=data.expected_result,
        )

        test_step = await self.repository.create(test_step)

        await self.db.commit()
        await self.db.refresh(test_step)

        return test_step

    async def update_test_step(
        self,
        step_id: uuid.UUID,
        test_case_id: uuid.UUID,
        project_id: uuid.UUID,
        data: TestStepUpdateRequest,
    ) -> TestStep:

        await self._validate_test_case(
            test_case_id=test_case_id,
            project_id=project_id,
        )

        test_step = await self.repository.get_by_id(
            step_id=step_id,
            test_case_id=test_case_id,
        )

        if test_step is None:
            raise NotFoundException(
                TestStepMessages.TEST_STEP_NOT_FOUND
            )

        if data.step_number is not None:
            existing_step = await self.repository.get_by_step_number(
                test_case_id=test_case_id,
                step_number=data.step_number,
            )

            if (
                existing_step is not None
                and existing_step.id != test_step.id
            ):
                raise ConflictException(
                    TestStepMessages.TEST_STEP_ALREADY_EXISTS
                )

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(test_step, field, value)

        await self.repository.update(test_step)

        await self.db.commit()
        await self.db.refresh(test_step)

        return test_step

    async def delete_test_step(
        self,
        step_id: uuid.UUID,
        test_case_id: uuid.UUID,
        project_id: uuid.UUID,
    ) -> None:

        await self._validate_test_case(
            test_case_id=test_case_id,
            project_id=project_id,
        )

        test_step = await self.repository.get_by_id(
            step_id=step_id,
            test_case_id=test_case_id,
        )

        if test_step is None:
            raise NotFoundException(
                TestStepMessages.TEST_STEP_NOT_FOUND
            )

        await self.repository.delete(test_step)

        await self.db.commit()


                
    async def reorder_test_steps(
            self,
            test_case_id: uuid.UUID,
            project_id: uuid.UUID,
            step_ids: list[uuid.UUID],
        ) -> list[TestStep]:

            await self._validate_test_case(
                test_case_id=test_case_id,
                project_id=project_id,
            )

            steps = await self.repository.get_all_for_reorder(
                test_case_id=test_case_id,
            )

            existing_ids = {step.id for step in steps}
            requested_ids = set(step_ids)

            if existing_ids != requested_ids:
                raise BadRequestException(
                    TestStepMessages.INVALID_REORDER 
                )

            steps_by_id = {
                step.id: step
                for step in steps
            }

            for index, step_id in enumerate(step_ids, start=1):
                steps_by_id[step_id].step_number = index

            await self.db.flush()
            await self.db.commit()

            return await self.repository.get_all_for_reorder(
                test_case_id=test_case_id,
            )

