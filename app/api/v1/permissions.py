
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.permissions import require_permission
from app.models.user import User
from app.schemas.permission import (
    PermissionCreateRequest,
    PermissionResponse,
)
from app.services.permission import PermissionService


router = APIRouter(
    prefix="/permissions",
    tags=["Permissions"],
)


@router.get(
    "",
    response_model=list[PermissionResponse],
)
async def get_permissions(
    current_user: User = Depends(
        require_permission("role.view")
    ),
    db: AsyncSession = Depends(get_db),
):
    service = PermissionService(db)

    return await service.get_permissions()


@router.post(
    "",
    response_model=PermissionResponse,
)
async def create_permission(
    request: PermissionCreateRequest,
    current_user: User = Depends(
        require_permission("role.create")
    ),
    db: AsyncSession = Depends(get_db),
):
    service = PermissionService(db)

    return await service.create_permission(request)

