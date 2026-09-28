from math import ceil
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.exception.exceptions import (
    BadRequestException,
    NotFoundException,
)
from app.exception.messages import TestModuleMessages
from app.models.test_module import TestModule
from app.repositories.test_module import TestModuleRepository
from app.schemas.test_module import (
    TestModuleCreateRequest,
    TestModuleUpdateRequest,
)


class TestModuleService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = TestModuleRepository(db)

    async def create_module(
        self,
        project_id: UUID,
        data: TestModuleCreateRequest,
    ):
        module = TestModule(
            project_id=project_id,
            name=data.name,
            description=data.description,
        )

        await self.repository.create(module)
        await self.db.commit()

        return module

    async def get_module(
        self,
        project_id: UUID,
        module_id: UUID,
    ):
        module = await self.repository.get_by_id(
            module_id=module_id,
            project_id=project_id,
        )

        if not module:
            raise NotFoundException(
                TestModuleMessages.TEST_MODULE_NOT_FOUND
            )

        return module

    async def get_modules(
        self,
        project_id: UUID,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ):
        try:
            items, total = await self.repository.get_all(
                project_id=project_id,
                page=page,
                page_size=page_size,
                search=search,
                sort_by=sort_by,
                sort_order=sort_order,
            )
        except ValueError:
            raise BadRequestException(
                TestModuleMessages.INVALID_SORT_FIELD
            )

        return {
            "items": items,
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": ceil(total / page_size) if total else 0,
        }

    async def update_module(
        self,
        project_id: UUID,
        module_id: UUID,
        data: TestModuleUpdateRequest,
    ):
        module = await self.get_module(
            project_id=project_id,
            module_id=module_id,
        )

        update_data = data.model_dump(
            exclude_unset=True
        )

        for field, value in update_data.items():
            setattr(module, field, value)

        await self.repository.update(module)
        await self.db.commit()

        return module

    async def delete_module(
        self,
        project_id: UUID,
        module_id: UUID,
    ):
        module = await self.get_module(
            project_id=project_id,
            module_id=module_id,
        )

        await self.repository.delete(module)
        await self.db.commit()