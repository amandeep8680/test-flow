from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.permissions import require_project_permission
from app.schemas.test_execution import (
    TestExecutionCreateRequest,
    TestExecutionListResponse,
    TestExecutionResponse,
    TestExecutionUpdateRequest,
)
from app.services.test_execution import TestExecutionService


router = APIRouter(
    prefix="/projects/{project_id}/test-cycles/{cycle_id}/executions",
    tags=["Test Executions"],
)


@router.post(
    "",
    response_model=TestExecutionResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(require_project_permission("test_execution.create"))
    ],
)
async def create_execution(
    project_id: UUID,
    cycle_id: UUID,
    data: TestExecutionCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    service = TestExecutionService(db)

    return await service.create_execution(
        project_id=project_id,
        cycle_id=cycle_id,
        data=data,
    )


@router.get(
    "",
    response_model=TestExecutionListResponse,
    dependencies=[
        Depends(require_project_permission("test_execution.view"))
    ],
)
async def get_executions(
    project_id: UUID,
    cycle_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    db: AsyncSession = Depends(get_db),
):
    service = TestExecutionService(db)

    return await service.get_executions(
        project_id=project_id,
        cycle_id=cycle_id,
        page=page,
        page_size=page_size,
        status=status,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get(
    "/{execution_id}",
    response_model=TestExecutionResponse,
    dependencies=[
        Depends(require_project_permission("test_execution.view"))
    ],
)
async def get_execution(
    project_id: UUID,
    cycle_id: UUID,
    execution_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    service = TestExecutionService(db)

    return await service.get_execution(
        project_id=project_id,
        cycle_id=cycle_id,
        execution_id=execution_id,
    )


@router.patch(
    "/{execution_id}",
    response_model=TestExecutionResponse,
    dependencies=[
        Depends(require_project_permission("test_execution.edit"))
    ],
)
async def update_execution(
    project_id: UUID,
    cycle_id: UUID,
    execution_id: UUID,
    data: TestExecutionUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    service = TestExecutionService(db)

    return await service.update_execution(
        project_id=project_id,
        cycle_id=cycle_id,
        execution_id=execution_id,
        data=data,
    )


@router.delete(
    "/{execution_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(require_project_permission("test_execution.delete"))
    ],
)
async def delete_execution(
    project_id: UUID,
    cycle_id: UUID,
    execution_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    service = TestExecutionService(db)

    await service.delete_execution(
        project_id=project_id,
        cycle_id=cycle_id,
        execution_id=execution_id,
    )