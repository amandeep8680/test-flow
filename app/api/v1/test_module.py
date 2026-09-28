from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.permissions import require_project_permission
from app.schemas.test_module import (
    TestModuleCreateRequest,
    TestModuleListResponse,
    TestModuleResponse,
    TestModuleUpdateRequest,
)
from app.services.test_module import TestModuleService


router = APIRouter(
    prefix="/projects/{project_id}/test-modules",
    tags=["Test Modules"],
)


@router.post(
    "",
    response_model=TestModuleResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_module(
    project_id: UUID,
    data: TestModuleCreateRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(
        require_project_permission("test_module.create")
    ),
):
    service = TestModuleService(db)

    return await service.create_module(
        project_id=project_id,
        data=data,
    )


@router.get(
    "",
    response_model=TestModuleListResponse,
)
async def get_modules(
    project_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query(
        "desc",
        pattern="^(asc|desc)$",
    ),
    db: AsyncSession = Depends(get_db),
    _=Depends(
        require_project_permission("test_module.view")
    ),
):
    service = TestModuleService(db)

    return await service.get_modules(
        project_id=project_id,
        page=page,
        page_size=page_size,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get(
    "/{module_id}",
    response_model=TestModuleResponse,
)
async def get_module(
    project_id: UUID,
    module_id: UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(
        require_project_permission("test_module.view")
    ),
):
    service = TestModuleService(db)

    return await service.get_module(
        project_id=project_id,
        module_id=module_id,
    )


@router.patch(
    "/{module_id}",
    response_model=TestModuleResponse,
)
async def update_module(
    project_id: UUID,
    module_id: UUID,
    data: TestModuleUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(
        require_project_permission("test_module.edit")
    ),
):
    service = TestModuleService(db)

    return await service.update_module(
        project_id=project_id,
        module_id=module_id,
        data=data,
    )


@router.delete(
    "/{module_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_module(
    project_id: UUID,
    module_id: UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(
        require_project_permission("test_module.delete")
    ),
):
    service = TestModuleService(db)

    await service.delete_module(
        project_id=project_id,
        module_id=module_id,
    )

    return None