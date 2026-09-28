from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.test_step_execution import TestStepExecution


class TestStepExecutionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(
        self,
        step_execution_id: UUID,
        execution_id: UUID,
    ):
        result = await self.db.execute(
            select(TestStepExecution).where(
                TestStepExecution.id == step_execution_id,
                TestStepExecution.test_execution_id == execution_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_execution(
        self,
        execution_id: UUID,
    ):
        result = await self.db.execute(
            select(TestStepExecution)
            .where(
                TestStepExecution.test_execution_id == execution_id
            )
            .order_by(TestStepExecution.step_number.asc())
        )
        return result.scalars().all()

    async def create(
        self,
        step_execution: TestStepExecution,
    ):
        self.db.add(step_execution)
        await self.db.flush()
        await self.db.refresh(step_execution)
        return step_execution

    async def update(
        self,
        step_execution: TestStepExecution,
    ):
        await self.db.flush()
        await self.db.refresh(step_execution)
        return step_execution

    async def delete(
        self,
        step_execution: TestStepExecution,
    ):
        await self.db.delete(step_execution)
        await self.db.flush()