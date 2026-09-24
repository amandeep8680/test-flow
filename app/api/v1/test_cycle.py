from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.permissions import require_project_permission
from app.schemas.test_cycle import (
    TestCycleCreateRequest,
    TestCycleListResponse,
    TestCycleResponse,
    TestCycleUpdateRequest,
)
from app.services.test_cycle import TestCycleService


router = APIRouter(
    prefix="/projects/{project_id}/test-cycles",
    tags=["Test Cycles"],
)


@router.post(
    "",
    response_model=TestCycleResponse,
    status_code=201,
)
async def create_test_cycle(
    project_id: UUID,
    data: TestCycleCreateRequest,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(
        require_project_permission("test_cycle.create")
    ),
):
    service = TestCycleService(db)

    return await service.create_test_cycle(
        project_id,
        data,
    )


@router.get(
    "",
    response_model=TestCycleListResponse,
)
async def get_test_cycles(
    project_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = None,
    cycle_type: str | None = Query(
        default=None,
        pattern="^(smoke|regression|functional|integration|release)$",
    ),
    status: str | None = Query(
        default=None,
        pattern="^(draft|active|completed|archived)$",
    ),
    sort_by: str = Query(
        "created_at",
        pattern="^(created_at|updated_at|name|type|status)$",
    ),
    sort_order: str = Query(
        "desc",
        pattern="^(asc|desc)$",
    ),
    db: AsyncSession = Depends(get_db),
    _: None = Depends(
        require_project_permission("test_cycle.view")
    ),
):
    service = TestCycleService(db)

    items, total = await service.get_test_cycles(
        project_id=project_id,
        page=page,
        page_size=page_size,
        search=search,
        cycle_type=cycle_type,
        status=status,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    return TestCycleListResponse(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get(
    "/{cycle_id}",
    response_model=TestCycleResponse,
)
async def get_test_cycle(
    project_id: UUID,
    cycle_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(
        require_project_permission("test_cycle.view")
    ),
):
    service = TestCycleService(db)

    return await service.get_test_cycle(
        cycle_id,
        project_id,
    )


@router.patch(
    "/{cycle_id}",
    response_model=TestCycleResponse,
)
async def update_test_cycle(
    project_id: UUID,
    cycle_id: UUID,
    data: TestCycleUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(
        require_project_permission("test_cycle.edit")
    ),
):
    service = TestCycleService(db)

    return await service.update_test_cycle(
        cycle_id,
        project_id,
        data,
    )


@router.delete(
    "/{cycle_id}",
    status_code=204,
)
async def delete_test_cycle(
    project_id: UUID,
    cycle_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(
        require_project_permission("test_cycle.delete")
    ),
):
    service = TestCycleService(db)

    await service.delete_test_cycle(
        cycle_id,
        project_id,
    )