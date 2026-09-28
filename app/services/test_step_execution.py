from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.exception.exceptions import NotFoundException
from app.repositories.test_execution import TestExecutionRepository
from app.repositories.test_step_execution import TestStepExecutionRepository
from app.schemas.test_step_execution import TestStepExecutionUpdateRequest


class TestStepExecutionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = TestStepExecutionRepository(db)
        self.execution_repository = TestExecutionRepository(db)

    async def get_step_execution(
        self,
        step_execution_id: UUID,
        execution_id: UUID,
    ):
        step_execution = await self.repository.get_by_id(
            step_execution_id,
            execution_id,
        )

        if step_execution is None:
            raise NotFoundException(
                "Test step execution not found."
            )

        return step_execution

    async def get_step_executions(
        self,
        execution_id: UUID,
    ):
        execution = await self.execution_repository.get_by_id(
            execution_id,
            None,
        )

        if execution is None:
            raise NotFoundException(
                "Test execution not found."
            )

        return await self.repository.get_by_execution(
            execution_id
        )

    async def update_step_execution(
        self,
        step_execution_id: UUID,
        execution_id: UUID,
        data: TestStepExecutionUpdateRequest,
    ):
        step_execution = await self.get_step_execution(
            step_execution_id,
            execution_id,
        )

        step_execution.status = data.status
        step_execution.actual_result = data.actual_result
        step_execution.notes = data.notes

        await self.repository.update(step_execution)
        await self.db.commit()
        await self.db.refresh(step_execution)

        return step_execution