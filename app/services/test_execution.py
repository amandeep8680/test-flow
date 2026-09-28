from datetime import datetime, timezone
from math import ceil
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.exception.exceptions import BadRequestException, NotFoundException
from app.exception.messages import (
    TestCaseMessages,
    TestCycleMessages,
    TestExecutionMessages,
)
from app.models.test_execution import TestExecution
from app.models.test_step_execution import TestStepExecution
from app.repositories.test_case import TestCaseRepository
from app.repositories.test_cycle import TestCycleRepository
from app.repositories.test_execution import TestExecutionRepository
from app.repositories.test_step import TestStepRepository
from app.repositories.test_step_execution import TestStepExecutionRepository
from app.schemas.test_execution import (
    TestExecutionCreateRequest,
    TestExecutionUpdateRequest,
)


class TestExecutionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = TestExecutionRepository(db)
        self.step_repository = TestStepExecutionRepository(db)
        self.test_cycle_repository = TestCycleRepository(db)
        self.test_case_repository = TestCaseRepository(db)
        self.test_step_repository = TestStepRepository(db)

    async def _validate_cycle(
        self,
        cycle_id: UUID,
        project_id: UUID,
    ):
        cycle = await self.test_cycle_repository.get_by_id(
            cycle_id,
            project_id,
        )

        if cycle is None:
            raise NotFoundException(
                TestCycleMessages.TEST_CYCLE_NOT_FOUND
            )

        return cycle

    async def _validate_test_case(
        self,
        test_case_id: UUID,
        project_id: UUID,
    ):
        test_case = await self.test_case_repository.get_by_id(
            test_case_id,
            project_id,
        )

        if test_case is None:
            raise NotFoundException(
                TestCaseMessages.TEST_CASE_NOT_FOUND
            )

        return test_case

    async def create_execution(
        self,
        project_id: UUID,
        cycle_id: UUID,
        data: TestExecutionCreateRequest,
    ):
        await self._validate_cycle(
            cycle_id,
            project_id,
        )

        test_case = await self._validate_test_case(
            data.test_case_id,
            project_id,
        )

        execution = TestExecution(
            test_cycle_id=cycle_id,
            test_case_id=test_case.id,
            status=data.status,
            actual_result=data.actual_result,
            notes=data.notes,
            executed_at=(
                datetime.now(timezone.utc)
                if data.status != "not_run"
                else None
            ),
        )

        execution = await self.repository.create(execution)

        steps = await self.test_step_repository.get_all_for_reorder(
            test_case.id
        )

        for step in steps:
            self.db.add(
                TestStepExecution(
                    test_execution_id=execution.id,
                    test_step_id=step.id,
                    step_number=step.step_number,
                    status="not_run",
                )
            )

        await self.db.commit()
        await self.db.refresh(execution)

        return execution

    async def get_execution(
        self,
        project_id: UUID,
        cycle_id: UUID,
        execution_id: UUID,
    ):
        await self._validate_cycle(
            cycle_id,
            project_id,
        )

        execution = await self.repository.get_by_id(
            execution_id,
            cycle_id,
        )

        if execution is None:
            raise NotFoundException(
                TestExecutionMessages.TEST_EXECUTION_NOT_FOUND
            )

        return execution

    async def get_executions(
        self,
        project_id: UUID,
        cycle_id: UUID,
        page: int = 1,
        page_size: int = 20,
        status: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ):
        await self._validate_cycle(
            cycle_id,
            project_id,
        )

        try:
            items, total = await self.repository.get_all(
                test_cycle_id=cycle_id,
                page=page,
                page_size=page_size,
                status=status,
                sort_by=sort_by,
                sort_order=sort_order,
            )
        except ValueError:
            raise BadRequestException(
                TestExecutionMessages.INVALID_SORT_FIELD
            )

        return {
            "items": items,
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": ceil(total / page_size) if total else 0,
        }

    async def update_execution(
        self,
        project_id: UUID,
        cycle_id: UUID,
        execution_id: UUID,
        data: TestExecutionUpdateRequest,
    ):
        execution = await self.get_execution(
            project_id,
            cycle_id,
            execution_id,
        )

        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(execution, field, value)

        if data.status is not None:
            execution.executed_at = (
                datetime.now(timezone.utc)
                if data.status != "not_run"
                else None
            )

        await self.repository.update(execution)
        await self.db.commit()
        await self.db.refresh(execution)

        return execution

    async def delete_execution(
        self,
        project_id: UUID,
        cycle_id: UUID,
        execution_id: UUID,
    ):
        execution = await self.get_execution(
            project_id,
            cycle_id,
            execution_id,
        )

        await self.repository.delete(execution)
        await self.db.commit()