
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.permissions import require_project_permission
from app.schemas.test_cycle_test_case import (
    TestCycleTestCaseAddRequest,
    TestCycleTestCaseListResponse,
    TestCycleTestCaseResponse,
)
from app.services.test_cycle_test_case import TestCycleTestCaseService


router = APIRouter(
    prefix="/projects/{project_id}/test-cycles/{cycle_id}/test-cases",
    tags=["Test Cycle Test Cases"],
)


@router.post(
    "",
    response_model=list[TestCycleTestCaseResponse],
    status_code=201,
)
async def add_test_cases(
    project_id: UUID,
    cycle_id: UUID,
    data: TestCycleTestCaseAddRequest,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(
        require_project_permission("test_cycle.edit")
    ),
):
    service = TestCycleTestCaseService(db)

    test_cases = await service.add_test_cases(
        cycle_id,
        project_id,
        data,
    )

    return [
        TestCycleTestCaseResponse.model_validate(test_case)
        for test_case in test_cases
    ]


@router.get(
    "",
    response_model=TestCycleTestCaseListResponse,
)
async def get_test_cases(
    project_id: UUID,
    cycle_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(
        require_project_permission("test_cycle.view")
    ),
):
    service = TestCycleTestCaseService(db)

    test_cases = await service.get_test_cases(
        cycle_id,
        project_id,
    )

    return TestCycleTestCaseListResponse(
        items=[
            TestCycleTestCaseResponse.model_validate(test_case)
            for test_case in test_cases
        ],
        total=len(test_cases),
    )


@router.delete(
    "/{test_case_id}",
    status_code=204,
)
async def remove_test_case(
    project_id: UUID,
    cycle_id: UUID,
    test_case_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(
        require_project_permission("test_cycle.edit")
    ),
):
    service = TestCycleTestCaseService(db)

    await service.remove_test_case(
        cycle_id,
        project_id,
        test_case_id,
    )
