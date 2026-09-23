import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.permissions import require_project_permission
from app.models.user import User
from app.schemas.test_case import (
    TagResponse,
    TestCaseCreateRequest,
    TestCaseResponse,
    TestCaseUpdateRequest,
)
from app.services.test_case import TestCaseService


router = APIRouter(
    prefix="/projects/{project_id}/test-cases",
    tags=["Test Cases"],
)


def build_test_case_response(test_case) -> TestCaseResponse:
    return TestCaseResponse(
        id=test_case.id,
        project_id=test_case.project_id,
        title=test_case.title,
        description=test_case.description,
        preconditions=test_case.preconditions,
        steps=test_case.steps,
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

    try:
        test_case = await service.create_test_case(
            project_id=project_id,
            data=data,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    return build_test_case_response(test_case)


@router.get(
    "",
    response_model=list[TestCaseResponse],
)
async def get_test_cases(
    project_id: uuid.UUID,
    current_user: User = Depends(
        require_project_permission("test_case.view")
    ),
    db: AsyncSession = Depends(get_db),
):
    service = TestCaseService(db)

    test_cases = await service.get_test_cases(
        project_id=project_id,
    )

    return [
        build_test_case_response(test_case)
        for test_case in test_cases
    ]


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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test case not found.",
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

    try:
        test_case = await service.update_test_case(
            test_case_id=test_case_id,
            project_id=project_id,
            data=data,
        )
    except ValueError as exc:
        if str(exc) == "Test case not found.":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
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

    try:
        await service.delete_test_case(
            test_case_id=test_case_id,
            project_id=project_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    return None