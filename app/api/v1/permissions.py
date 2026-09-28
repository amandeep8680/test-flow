from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.permissions import require_permission
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.user import User
from app.models.user_role import UserRole
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
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Permission)
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .join(Role, Role.id == RolePermission.role_id)
        .join(UserRole, UserRole.role_id == Role.id)
        .where(
            UserRole.user_id == current_user.id,
            Role.organization_id == current_user.organization_id,
            Role.is_active.is_(True),
        )
        .distinct()
        .order_by(Permission.name)
    )

    return list(result.scalars().all())


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