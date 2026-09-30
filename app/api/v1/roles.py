from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.permissions import require_permission
from app.models.role import Role
from app.models.user import User
from app.models.user_role import UserRole
from app.schemas.role import RoleCreateRequest, RoleResponse, RoleUpdateRequest
from app.services.role import RoleService

router = APIRouter(prefix="/roles", tags=["Roles"])


@router.get("", response_model=list[RoleResponse])
async def get_roles(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = RoleService(db)

    return await service.get_roles(
        organization_id=current_user.organization_id,
    )


@router.get("/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: UUID,
    current_user: User = Depends(require_permission("role.view")),
    db: AsyncSession = Depends(get_db),
):
    service = RoleService(db)

    role = await service.get_role(
        role_id=role_id,
        organization_id=current_user.organization_id,
    )

    if role is None:
        raise HTTPException(status_code=404, detail="Role not found")

    return role


@router.post("", response_model=RoleResponse, status_code=201)
async def create_role(
    request: RoleCreateRequest,
    current_user: User = Depends(require_permission("role.create")),
    db: AsyncSession = Depends(get_db),
):
    service = RoleService(db)

    return await service.create_role(
        request=request,
        organization_id=current_user.organization_id,
    )


@router.patch("/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: UUID,
    request: RoleUpdateRequest,
    current_user: User = Depends(require_permission("role.edit")),
    db: AsyncSession = Depends(get_db),
):
    service = RoleService(db)

    role = await service.update_role(
        role_id=role_id,
        organization_id=current_user.organization_id,
        request=request,
    )

    if role is None:
        raise HTTPException(status_code=404, detail="Role not found")

    return role


@router.delete(
    "/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)



@router.delete(
    "/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_role(
    role_id: UUID,
    current_user: User = Depends(
        require_permission("role.delete")
    ),
    db: AsyncSession = Depends(get_db),
):
    service = RoleService(db)

    await service.delete_role(
        role_id=role_id,
        organization_id=current_user.organization_id,
        current_user_id=current_user.id,
    )