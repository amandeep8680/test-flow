import uuid
from math import ceil

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.permissions import require_project_permission
from app.models.user import User
from app.schemas.test_step import (
    TestStepCreateRequest,
    TestStepListResponse,
    TestStepReorderRequest,
    TestStepResponse,
    TestStepUpdateRequest,
)
from app.services.test_step import TestStepService


router = APIRouter(
    prefix="/projects/{project_id}/test-cases/{test_case_id}/steps",
    tags=["Test Steps"],
)


@router.post(
    "",
    response_model=TestStepResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_test_step(
    project_id: uuid.UUID,
    test_case_id: uuid.UUID,
    data: TestStepCreateRequest,
    current_user: User = Depends(
        require_project_permission("test_case.edit")
    ),
    db: AsyncSession = Depends(get_db),
):
    service = TestStepService(db)

    return await service.create_test_step(
        test_case_id=test_case_id,
        project_id=project_id,
        data=data,
    )


@router.get(
    "",
    response_model=TestStepListResponse,
)
async def get_test_steps(
    project_id: uuid.UUID,
    test_case_id: uuid.UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = Query(None),
    sort_by: str = Query(
        "step_number",
        pattern="^(step_number|created_at|updated_at)$",
    ),
    sort_order: str = Query(
        "asc",
        pattern="^(asc|desc)$",
    ),
    current_user: User = Depends(
        require_project_permission("test_case.view")
    ),
    db: AsyncSession = Depends(get_db),
):
    service = TestStepService(db)

    steps, total = await service.get_test_steps(
        test_case_id=test_case_id,
        project_id=project_id,
        page=page,
        page_size=page_size,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    return TestStepListResponse(
        items=steps,
        page=page,
        page_size=page_size,
        total=total,
        total_pages=ceil(total / page_size) if total else 0,
    )

@router.patch(
    "/reorder",
    response_model=list[TestStepResponse],
)
async def reorder_test_steps(
    project_id: uuid.UUID,
    test_case_id: uuid.UUID,
    data: TestStepReorderRequest,
    current_user: User = Depends(
        require_project_permission("test_case.edit")
    ),
    db: AsyncSession = Depends(get_db),
):
    service = TestStepService(db)

    return await service.reorder_test_steps(
        test_case_id=test_case_id,
        project_id=project_id,
        step_ids=data.step_ids,
    )



@router.get(
    "/{step_id}",
    response_model=TestStepResponse,
)
async def get_test_step(
    project_id: uuid.UUID,
    test_case_id: uuid.UUID,
    step_id: uuid.UUID,
    current_user: User = Depends(
        require_project_permission("test_case.view")
    ),
    db: AsyncSession = Depends(get_db),
):
    service = TestStepService(db)

    step = await service.get_test_step(
        step_id=step_id,
        test_case_id=test_case_id,
        project_id=project_id,
    )

    if step is None:
        from app.exception.exceptions import NotFoundException
        from app.exception.messages import TestStepMessages

        raise NotFoundException(
            TestStepMessages.TEST_STEP_NOT_FOUND
        )

    return step


@router.patch(
    "/{step_id}",
    response_model=TestStepResponse,
)
async def update_test_step(
    project_id: uuid.UUID,
    test_case_id: uuid.UUID,
    step_id: uuid.UUID,
    data: TestStepUpdateRequest,
    current_user: User = Depends(
        require_project_permission("test_case.edit")
    ),
    db: AsyncSession = Depends(get_db),
):
    service = TestStepService(db)

    return await service.update_test_step(
        step_id=step_id,
        test_case_id=test_case_id,
        project_id=project_id,
        data=data,
    )


@router.delete(
    "/{step_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_test_step(
    project_id: uuid.UUID,
    test_case_id: uuid.UUID,
    step_id: uuid.UUID,
    current_user: User = Depends(
        require_project_permission("test_case.edit")
    ),
    db: AsyncSession = Depends(get_db),
):
    service = TestStepService(db)

    await service.delete_test_step(
        step_id=step_id,
        test_case_id=test_case_id,
        project_id=project_id,
    )

    return None


