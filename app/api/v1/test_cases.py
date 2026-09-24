
import uuid
from math import ceil

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.permissions import require_project_permission
from app.exception.exceptions import NotFoundException
from app.exception.messages import TestCaseMessages
from app.models.user import User
from app.schemas.test_case import (
    TagResponse,
    TestCaseCreateRequest,
    TestCaseListResponse,
    TestCaseResponse,
    TestCaseUpdateRequest,
)
from app.services.test_case import TestCaseService


router = APIRouter(
    prefix="/projects/{project_id}/test-cases",
    tags=["Test Cases"],
)


def build_test_case_response(
    test_case,
) -> TestCaseResponse:
    return TestCaseResponse(
        id=test_case.id,
        project_id=test_case.project_id,
        title=test_case.title,
        description=test_case.description,
        preconditions=test_case.preconditions,
        postconditions=test_case.postconditions,
        priority=test_case.priority,
        status=test_case.status,
        tags=[
            TagResponse.model_validate(test_case_tag.tag)
            for test_case_tag in test_case.test_case_tags
        ],
    )


@router.post(
    "",
    response_model=TestCaseResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_test_case(
    project_id: uuid.UUID,
    data: TestCaseCreateRequest,
    current_user: User = Depends(
        require_project_permission("test_case.create")
    ),
    db: AsyncSession = Depends(get_db),
):
    service = TestCaseService(db)

    test_case = await service.create_test_case(
        project_id=project_id,
        data=data,
    )

    return build_test_case_response(test_case)


@router.get(
    "",
    response_model=TestCaseListResponse,
)
async def get_test_cases(
    project_id: uuid.UUID,
    page: int = Query(
        1,
        ge=1,
    ),
    page_size: int = Query(
        20,
        ge=1,
        le=100,
    ),
    search: str | None = Query(None),
    status: str | None = Query(
        None,
        pattern="^(draft|active|inactive)$",
    ),
    priority: str | None = Query(
        None,
        pattern="^(low|medium|high|critical)$",
    ),
    tag_id: uuid.UUID | None = Query(None),
    sort_by: str = Query(
        "created_at",
    ),
    sort_order: str = Query(
        "desc",
        pattern="^(asc|desc)$",
    ),
    current_user: User = Depends(
        require_project_permission("test_case.view")
    ),
    db: AsyncSession = Depends(get_db),
):
    service = TestCaseService(db)

    test_cases, total = await service.get_test_cases(
        project_id=project_id,
        page=page,
        page_size=page_size,
        search=search,
        status=status,
        priority=priority,
        tag_id=tag_id,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    return TestCaseListResponse(
        items=[
            build_test_case_response(test_case)
            for test_case in test_cases
        ],
        page=page,
        page_size=page_size,
        total=total,
        total_pages=ceil(total / page_size) if total else 0,
    )


@router.get(
    "/{test_case_id}",
    response_model=TestCaseResponse,
)
async def get_test_case(
    project_id: uuid.UUID,
    test_case_id: uuid.UUID,
    current_user: User = Depends(
        require_project_permission("test_case.view")
    ),
    db: AsyncSession = Depends(get_db),
):
    service = TestCaseService(db)

    test_case = await service.get_test_case(
        test_case_id=test_case_id,
        project_id=project_id,
    )

    if test_case is None:
        raise NotFoundException(
            TestCaseMessages.TEST_CASE_NOT_FOUND
        )

    return build_test_case_response(test_case)


@router.patch(
    "/{test_case_id}",
    response_model=TestCaseResponse,
)
async def update_test_case(
    project_id: uuid.UUID,
    test_case_id: uuid.UUID,
    data: TestCaseUpdateRequest,
    current_user: User = Depends(
        require_project_permission("test_case.edit")
    ),
    db: AsyncSession = Depends(get_db),
):
    service = TestCaseService(db)

    test_case = await service.update_test_case(
        test_case_id=test_case_id,
        project_id=project_id,
        data=data,
    )

    return build_test_case_response(test_case)


@router.delete(
    "/{test_case_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_test_case(
    project_id: uuid.UUID,
    test_case_id: uuid.UUID,
    current_user: User = Depends(
        require_project_permission("test_case.delete")
    ),
    db: AsyncSession = Depends(get_db),
):
    service = TestCaseService(db)

    await service.delete_test_case(
        test_case_id=test_case_id,
        project_id=project_id,
    )

    return None
