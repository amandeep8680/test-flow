from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exception.exceptions import (
    ConflictException,
    NotFoundException,
)
from app.exception.messages import ProjectMessages
from app.models.project import Project
from app.models.project_member import ProjectMember
from app.models.user import User
from app.repositories.project import ProjectRepository
from app.repositories.project_member import ProjectMemberRepository
from app.repositories.user import UserRepository
from app.schemas.project import (
    ProjectCreateRequest,
    ProjectUpdateRequest,
)
from app.schemas.project_member import (
    ProjectMemberCreateRequest,
    ProjectMemberUpdateRoleRequest,
)


class ProjectService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.project_repository = ProjectRepository(db)
        self.project_member_repository = ProjectMemberRepository(db)
        self.user_repository = UserRepository(db)

    # =========================================================
    # GET SINGLE PROJECT
    # =========================================================

    async def get_project(
        self,
        project_id: UUID,
        current_user: User,
    ) -> Project:
        project = await self.project_repository.get_by_id(
            project_id
        )

        if (
            project is None
            or project.organization_id
            != current_user.organization_id
        ):
            raise NotFoundException(
                ProjectMessages.PROJECT_NOT_FOUND
            )

        return project

    # =========================================================
    # CREATE PROJECT
    # =========================================================

    async def create_project(
        self,
        current_user: User,
        request: ProjectCreateRequest,
    ) -> Project:
        existing_project = await self.project_repository.get_by_key(
            organization_id=current_user.organization_id,
            key=request.key,
        )

        if existing_project:
            raise ConflictException(
                ProjectMessages.PROJECT_KEY_ALREADY_EXISTS
            )

        project = await self.project_repository.create(
            organization_id=current_user.organization_id,
            name=request.name,
            key=request.key,
            description=request.description,
        )

        await self.db.commit()
        await self.db.refresh(project)

        return project

    # =========================================================
    # GET ALL PROJECTS
    # =========================================================

    async def get_projects(
        self,
        current_user: User,
        search: str | None = None,
        is_active: bool | None = None,
    ) -> list[Project]:
        return await self.project_repository.get_all_by_organization(
            organization_id=current_user.organization_id,
            search=search,
            is_active=is_active,
        )

    # =========================================================
    # GET ACTIVE PROJECTS
    # =========================================================

    async def get_active_projects(
        self,
        current_user: User,
    ) -> list[Project]:
        return await (
            self.project_repository.get_active_by_organization(
                organization_id=current_user.organization_id,
            )
        )

    # =========================================================
    # GET INACTIVE PROJECTS
    # =========================================================

    async def get_inactive_projects(
        self,
        current_user: User,
    ) -> list[Project]:
        return await (
            self.project_repository.get_inactive_by_organization(
                organization_id=current_user.organization_id,
            )
        )

    # =========================================================
    # UPDATE PROJECT
    # =========================================================

    async def update_project(
        self,
        project_id: UUID,
        current_user: User,
        request: ProjectUpdateRequest,
    ) -> Project:
        project = await self.get_project(
            project_id=project_id,
            current_user=current_user,
        )

        project = await self.project_repository.update(
            project=project,
            name=request.name,
            description=request.description,
        )

        await self.db.commit()
        await self.db.refresh(project)

        return project

    # =========================================================
    # DEACTIVATE PROJECT
    # =========================================================

    async def deactivate_project(
        self,
        project_id: UUID,
        current_user: User,
    ) -> Project:
        project = await self.get_project(
            project_id=project_id,
            current_user=current_user,
        )

        if not project.is_active:
            raise ConflictException(
                ProjectMessages.PROJECT_ALREADY_INACTIVE
            )

        project = await self.project_repository.deactivate(
            project
        )

        await self.db.commit()
        await self.db.refresh(project)

        return project

    # =========================================================
    # ACTIVATE PROJECT
    # =========================================================

    async def activate_project(
        self,
        project_id: UUID,
        current_user: User,
    ) -> Project:
        project = await self.get_project(
            project_id=project_id,
            current_user=current_user,
        )

        if project.is_active:
            raise ConflictException(
                ProjectMessages.PROJECT_ALREADY_ACTIVE
            )

        project = await self.project_repository.activate(
            project
        )

        await self.db.commit()
        await self.db.refresh(project)

        return project

    # =========================================================
    # PERMANENTLY DELETE PROJECT
    # =========================================================

    async def delete_project_permanently(
        self,
        project_id: UUID,
        current_user: User,
    ) -> None:
        project = await self.get_project(
            project_id=project_id,
            current_user=current_user,
        )

        await self.project_repository.delete_permanently(
            project
        )

        await self.db.commit()

    # =========================================================
    # ADD PROJECT MEMBER
    # =========================================================

    async def add_member(
        self,
        project_id: UUID,
        current_user: User,
        request: ProjectMemberCreateRequest,
    ) -> ProjectMember:
        await self.get_project(
            project_id=project_id,
            current_user=current_user,
        )

        user = await self.user_repository.get_by_id(
            request.user_id
        )

        if (
            user is None
            or user.organization_id
            != current_user.organization_id
        ):
            raise NotFoundException(
                ProjectMessages.USER_NOT_FOUND
            )

        existing_member = (
            await self.project_member_repository
            .get_by_project_and_user(
                project_id=project_id,
                user_id=request.user_id,
            )
        )

        if existing_member:
            raise ConflictException(
                ProjectMessages.MEMBER_ALREADY_EXISTS
            )

        member = await self.project_member_repository.create(
            project_id=project_id,
            user_id=request.user_id,
            role=request.role,
        )

        await self.db.commit()
        await self.db.refresh(member)

        return member

    # =========================================================
    # GET PROJECT MEMBERS
    # =========================================================

    async def get_members(
        self,
        project_id: UUID,
        current_user: User,
    ) -> list[ProjectMember]:
        await self.get_project(
            project_id=project_id,
            current_user=current_user,
        )

        return await self.project_member_repository.get_by_project(
            project_id=project_id,
        )



    # =========================================================
    # REMOVE PROJECT MEMBER
    # =========================================================

    async def remove_member(
        self,
        project_id: UUID,
        current_user: User,
        user_id: UUID,
    ) -> None:
        await self.get_project(
            project_id=project_id,
            current_user=current_user,
        )

        member = (
            await self.project_member_repository
            .get_by_project_and_user(
                project_id=project_id,
                user_id=user_id,
            )
        )

        if member is None:
            raise NotFoundException(
                ProjectMessages.PROJECT_MEMBER_NOT_FOUND
            )

        await self.project_member_repository.delete(member)

        await self.db.commit()

    # =========================================================
    # UPDATE PROJECT MEMBER ROLE
    # =========================================================

    async def update_member_role(
        self,
        project_id: UUID,
        current_user: User,
        user_id: UUID,
        request: ProjectMemberUpdateRoleRequest,
    ) -> ProjectMember:
        await self.get_project(
            project_id=project_id,
            current_user=current_user,
        )

        member = (
            await self.project_member_repository
            .get_by_project_and_user(
                project_id=project_id,
                user_id=user_id,
            )
        )

        if member is None:
            raise NotFoundException(
                ProjectMessages.PROJECT_MEMBER_NOT_FOUND
            )

        member = await self.project_member_repository.update_role(
            member=member,
            role=request.role,
        )

        await self.db.commit()
        await self.db.refresh(member)

        return member

    # =========================================================
    # PROJECT SUMMARY
    # =========================================================

    async def get_project_summary(
        self,
        project_id: UUID,
        current_user: User,
    ) -> dict:
        project = await self.get_project(
            project_id=project_id,
            current_user=current_user,
        )

        result = await self.db.execute(
            select(
                func.count(ProjectMember.user_id)
            ).where(
                ProjectMember.project_id == project_id,
            )
        )

        members_count = result.scalar_one()

        return {
            "project_id": project.id,
            "name": project.name,
            "key": project.key,
            "description": project.description,
            "is_active": project.is_active,
            "members_count": members_count,
        }