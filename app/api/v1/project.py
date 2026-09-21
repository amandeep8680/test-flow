from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.project import (
    ProjectCreateRequest,
    ProjectResponse,
    ProjectUpdateRequest,
)
from app.schemas.project_member import (
    ProjectMemberCreateRequest,
    ProjectMemberResponse,
    ProjectMemberUpdateRoleRequest,
)
from app.services.project import ProjectService


router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)


# =========================================================
# CREATE PROJECT
# =========================================================

@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_project(
    request: ProjectCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)

    return await service.create_project(
        current_user=current_user,
        request=request,
    )


# =========================================================
# GET ALL PROJECTS
# Active + Inactive
#
# Optional:
# ?search=backend
# ?is_active=true
# ?search=backend&is_active=true
# =========================================================

@router.get(
    "",
    response_model=list[ProjectResponse],
)
async def get_projects(
    search: str | None = Query(
        default=None,
        description="Search projects by name or key",
    ),
    is_active: bool | None = Query(
        default=None,
        description="Filter projects by active status",
    ),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)

    return await service.get_projects(
        current_user=current_user,
        search=search,
        is_active=is_active,
    )


# =========================================================
# GET ACTIVE PROJECTS
# =========================================================

@router.get(
    "/active",
    response_model=list[ProjectResponse],
)
async def get_active_projects(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)

    return await service.get_active_projects(
        current_user=current_user,
    )


# =========================================================
# GET INACTIVE PROJECTS
# =========================================================

@router.get(
    "/inactive",
    response_model=list[ProjectResponse],
)
async def get_inactive_projects(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)

    return await service.get_inactive_projects(
        current_user=current_user,
    )


# =========================================================
# GET PROJECT MEMBERS
# =========================================================

@router.get(
    "/{project_id}/members",
    response_model=list[ProjectMemberResponse],
)
async def get_project_members(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)

    return await service.get_members(
        project_id=project_id,
        current_user=current_user,
    )


# =========================================================
# GET PROJECT SUMMARY
# =========================================================

@router.get(
    "/{project_id}/summary",
)
async def get_project_summary(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)

    return await service.get_project_summary(
        project_id=project_id,
        current_user=current_user,
    )


# =========================================================
# PERMANENTLY DELETE PROJECT
# =========================================================

@router.delete(
    "/{project_id}/permanent",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_project_permanently(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)

    await service.delete_project_permanently(
        project_id=project_id,
        current_user=current_user,
    )


# =========================================================
# GET SINGLE PROJECT
# =========================================================

@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
)
async def get_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)

    return await service.get_project(
        project_id=project_id,
        current_user=current_user,
    )


# =========================================================
# UPDATE PROJECT
# =========================================================

@router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
)
async def update_project(
    project_id: UUID,
    request: ProjectUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)

    return await service.update_project(
        project_id=project_id,
        current_user=current_user,
        request=request,
    )


# =========================================================
# DEACTIVATE PROJECT
# DELETE = Mark as Inactive
# =========================================================

@router.delete(
    "/{project_id}",
    response_model=ProjectResponse,
)
async def deactivate_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)

    return await service.deactivate_project(
        project_id=project_id,
        current_user=current_user,
    )


# =========================================================
# ACTIVATE PROJECT
# =========================================================

@router.post(
    "/{project_id}/activate",
    response_model=ProjectResponse,
)
async def activate_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)

    return await service.activate_project(
        project_id=project_id,
        current_user=current_user,
    )


# =========================================================
# ADD PROJECT MEMBER
# =========================================================

@router.post(
    "/{project_id}/members",
    response_model=ProjectMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_project_member(
    project_id: UUID,
    request: ProjectMemberCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)

    return await service.add_member(
        project_id=project_id,
        current_user=current_user,
        request=request,
    )


# =========================================================
# REMOVE PROJECT MEMBER
# =========================================================

@router.delete(
    "/{project_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_project_member(
    project_id: UUID,
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)

    await service.remove_member(
        project_id=project_id,
        current_user=current_user,
        user_id=user_id,
    )


# =========================================================
# UPDATE PROJECT MEMBER ROLE
# =========================================================

@router.patch(
    "/{project_id}/members/{user_id}",
    response_model=ProjectMemberResponse,
)
async def update_project_member_role(
    project_id: UUID,
    user_id: UUID,
    request: ProjectMemberUpdateRoleRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)

    return await service.update_member_role(
        project_id=project_id,
        current_user=current_user,
        user_id=user_id,
        request=request,
    )

