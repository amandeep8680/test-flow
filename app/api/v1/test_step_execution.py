from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.permissions import require_project_permission
from app.schemas.test_step_execution import (
    TestStepExecutionResponse,
    TestStepExecutionUpdateRequest,
)
from app.services.test_step_execution import TestStepExecutionService


router = APIRouter(
    prefix="/projects/{project_id}/test-cycles/{cycle_id}/executions/{execution_id}/steps",
    tags=["Test Step Executions"],
)


@router.get(
    "",
    response_model=list[TestStepExecutionResponse],
    dependencies=[
        Depends(require_project_permission("test_execution.view"))
    ],
)
async def get_step_executions(
    project_id: UUID,
    cycle_id: UUID,
    execution_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    service = TestStepExecutionService(db)

    return await service.get_step_executions(
        execution_id=execution_id,
    )


@router.patch(
    "/{step_execution_id}",
    response_model=TestStepExecutionResponse,
    dependencies=[
        Depends(require_project_permission("test_execution.edit"))
    ],
)
async def update_step_execution(
    project_id: UUID,
    cycle_id: UUID,
    execution_id: UUID,
    step_execution_id: UUID,
    data: TestStepExecutionUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    service = TestStepExecutionService(db)

    return await service.update_step_execution(
        step_execution_id=step_execution_id,
        execution_id=execution_id,
        data=data,
    )