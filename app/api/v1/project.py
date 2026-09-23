from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.permissions import (
    require_permission,
    require_project_permission,
)
from app.models.user import User
from app.schemas.project import (
    ProjectCreateRequest,
    ProjectListResponse,
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
# POST /projects
# =========================================================

@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_project(
    request: ProjectCreateRequest,
    current_user: User = Depends(
        require_permission("project.create")
    ),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)

    return await service.create_project(
        current_user=current_user,
        request=request,
    )


# =========================================================
# GET ALL PROJECTS
# GET /projects
#
# Optional:
# ?search=backend
# ?is_active=true
# ?search=backend&is_active=true
#
# Organization-scoped
# NO project_id
# =========================================================

@router.get(
    "",
    response_model=ProjectListResponse,
)
async def get_projects(
    page: int = Query(
        default=1,
        ge=1,
        description="Page number",
    ),
    page_size: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Number of projects per page",
    ),
    search: str | None = Query(
        default=None,
        description="Search projects by name or key",
    ),
    is_active: bool | None = Query(
        default=None,
        description="Filter projects by active status",
    ),
    sort_by: str = Query(
        default="created_at",
        description="Sort by: created_at, updated_at, name, key",
    ),
    sort_order: str = Query(
        default="desc",
        pattern="^(asc|desc)$",
        description="Sort order",
    ),
    current_user: User = Depends(
        require_permission("project.view")
    ),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)

    try:
        projects, total = await service.get_projects(
            current_user=current_user,
            page=page,
            page_size=page_size,
            search=search,
            is_active=is_active,
            sort_by=sort_by,
            sort_order=sort_order,
        )
    except ValueError as exc:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    return ProjectListResponse(
        items=projects,
        page=page,
        page_size=page_size,
        total=total,
        total_pages=(total + page_size - 1) // page_size
        if total
        else 0,
    )


# =========================================================
# GET ACTIVE PROJECTS
# GET /projects/active
#
# Organization-scoped
# NO project_id
# =========================================================

# @router.get(
#     "/active",
#     response_model=list[ProjectResponse],
# )
# async def get_active_projects(
#     current_user: User = Depends(
#         require_permission("project.view")
#     ),
#     db: AsyncSession = Depends(get_db),
# ):
#     service = ProjectService(db)

#     return await service.get_active_projects(
#         current_user=current_user,
#     )


# =========================================================
# GET INACTIVE PROJECTS
# GET /projects/inactive
#
# Organization-scoped
# NO project_id
# =========================================================

# @router.get(
#     "/inactive",
#     response_model=list[ProjectResponse],
# )
# async def get_inactive_projects(
#     current_user: User = Depends(
#         require_permission("project.view")
#     ),
#     db: AsyncSession = Depends(get_db),
# ):
#     service = ProjectService(db)

#     return await service.get_inactive_projects(
#         current_user=current_user,
#     )


# =========================================================
# GET PROJECT MEMBERS
# GET /projects/{project_id}/members
#
# Project-scoped
# =========================================================

@router.get(
    "/{project_id}/members",
    response_model=list[ProjectMemberResponse],
)
async def get_project_members(
    project_id: UUID,
    current_user: User = Depends(
        require_project_permission("project.manage_members")
    ),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)

    return await service.get_members(
        project_id=project_id,
        current_user=current_user,
    )


# =========================================================
# GET PROJECT SUMMARY
# GET /projects/{project_id}/summary
#
# Project-scoped
# =========================================================

@router.get(
    "/{project_id}/summary",
)
async def get_project_summary(
    project_id: UUID,
    current_user: User = Depends(
        require_project_permission("project.view")
    ),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)

    return await service.get_project_summary(
        project_id=project_id,
        current_user=current_user,
    )


# =========================================================
# PERMANENTLY DELETE PROJECT
# DELETE /projects/{project_id}/permanent
#
# Project-scoped
# =========================================================

@router.delete(
    "/{project_id}/permanent",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_project_permanently(
    project_id: UUID,
    current_user: User = Depends(
        require_project_permission("project.delete")
    ),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)

    await service.delete_project_permanently(
        project_id=project_id,
        current_user=current_user,
    )


# =========================================================
# GET SINGLE PROJECT
# GET /projects/{project_id}
#
# Project-scoped
# =========================================================

@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
)
async def get_project(
    project_id: UUID,
    current_user: User = Depends(
        require_project_permission("project.view")
    ),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)

    return await service.get_project(
        project_id=project_id,
        current_user=current_user,
    )


# =========================================================
# UPDATE PROJECT
# PATCH /projects/{project_id}
#
# Project-scoped
# =========================================================

@router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
)
async def update_project(
    project_id: UUID,
    request: ProjectUpdateRequest,
    current_user: User = Depends(
        require_project_permission("project.edit")
    ),
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
# DELETE /projects/{project_id}
#
# Soft delete / mark inactive
# Project-scoped
# =========================================================

@router.delete(
    "/{project_id}",
    response_model=ProjectResponse,
)
async def deactivate_project(
    project_id: UUID,
    current_user: User = Depends(
        require_project_permission("project.delete")
    ),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)

    return await service.deactivate_project(
        project_id=project_id,
        current_user=current_user,
    )


# =========================================================
# ACTIVATE PROJECT
# POST /projects/{project_id}/activate
#
# Project-scoped
# =========================================================

@router.post(
    "/{project_id}/activate",
    response_model=ProjectResponse,
)
async def activate_project(
    project_id: UUID,
    current_user: User = Depends(
        require_project_permission("project.edit")
    ),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)

    return await service.activate_project(
        project_id=project_id,
        current_user=current_user,
    )


# =========================================================
# ADD PROJECT MEMBER
# POST /projects/{project_id}/members
#
# Project-scoped
# =========================================================

@router.post(
    "/{project_id}/members",
    response_model=ProjectMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_project_member(
    project_id: UUID,
    request: ProjectMemberCreateRequest,
    current_user: User = Depends(
        require_project_permission("project.manage_members")
    ),
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
# DELETE /projects/{project_id}/members/{user_id}
#
# Project-scoped
# =========================================================

@router.delete(
    "/{project_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_project_member(
    project_id: UUID,
    user_id: UUID,
    current_user: User = Depends(
        require_project_permission("project.manage_members")
    ),
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
# PATCH /projects/{project_id}/members/{user_id}
#
# Project-scoped
# =========================================================

@router.patch(
    "/{project_id}/members/{user_id}",
    response_model=ProjectMemberResponse,
)
async def update_project_member_role(
    project_id: UUID,
    user_id: UUID,
    request: ProjectMemberUpdateRoleRequest,
    current_user: User = Depends(
        require_project_permission("project.manage_members")
    ),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)

    return await service.update_member_role(
        project_id=project_id,
        current_user=current_user,
        user_id=user_id,
        request=request,
    )