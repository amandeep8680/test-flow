import uuid

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.exception.exceptions import NotFoundException
from app.exception.messages import TestCaseMessages
from app.models.test_case import TestCase
from app.models.test_case_tag import TestCaseTag
from app.repositories.tag import TagRepository
from app.repositories.test_case import TestCaseRepository
from app.repositories.test_module import TestModuleRepository
from app.schemas.test_case import (
    TestCaseCreateRequest,
    TestCaseUpdateRequest,
)


class TestCaseService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.test_case_repository = TestCaseRepository(db)
        self.tag_repository = TagRepository(db)
        self.test_module_repository = TestModuleRepository(db)

    async def get_test_case(
        self,
        test_case_id: uuid.UUID,
        project_id: uuid.UUID,
        module_id: uuid.UUID,
    ) -> TestCase | None:
        return await self.test_case_repository.get_by_id(
            test_case_id=test_case_id,
            project_id=project_id,
            module_id=module_id,
        )

    async def get_test_cases(
        self,
        project_id: uuid.UUID,
        module_id: uuid.UUID,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
        status: str | None = None,
        priority: str | None = None,
        tag_id: uuid.UUID | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[list[TestCase], int]:

        return await self.test_case_repository.get_all(
            project_id=project_id,
            module_id=module_id,
            page=page,
            page_size=page_size,
            search=search,
            status=status,
            priority=priority,
            tag_id=tag_id,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    async def create_test_case(
        self,
        project_id: uuid.UUID,
        module_id: uuid.UUID,
        data: TestCaseCreateRequest,
    ) -> TestCase:

        module = await self.test_module_repository.get_by_id(
            module_id=module_id,
            project_id=project_id,
        )

        if module is None:
            raise NotFoundException(
                TestCaseMessages.TEST_MODULE_NOT_FOUND
            )

        tags = []

        for tag_id in data.tag_ids:
            tag = await self.tag_repository.get_by_id(
                tag_id=tag_id,
            )

            if tag is None:
                raise NotFoundException(
                    TestCaseMessages.TAG_NOT_FOUND
                )

            tags.append(tag)

        test_case = TestCase(
            project_id=project_id,
            module_id=module_id,
            title=data.title,
            description=data.description,
            preconditions=data.preconditions,
            postconditions=data.postconditions,
            priority=data.priority,
            status=data.status,
        )

        test_case = await self.test_case_repository.create(
            test_case=test_case,
        )

        for tag in tags:
            self.db.add(
                TestCaseTag(
                    test_case_id=test_case.id,
                    tag_id=tag.id,
                )
            )

        await self.db.commit()

        test_case = await self.test_case_repository.get_by_id(
            test_case_id=test_case.id,
            project_id=project_id,
            module_id=module_id,
        )

        return test_case

    async def update_test_case(
        self,
        test_case_id: uuid.UUID,
        project_id: uuid.UUID,
        module_id: uuid.UUID,
        data: TestCaseUpdateRequest,
    ) -> TestCase:

        test_case = await self.test_case_repository.get_by_id(
            test_case_id=test_case_id,
            project_id=project_id,
            module_id=module_id,
        )

        if test_case is None:
            raise NotFoundException(
                TestCaseMessages.TEST_CASE_NOT_FOUND
            )

        tags = None

        if data.tag_ids is not None:
            tags = []

            for tag_id in data.tag_ids:
                tag = await self.tag_repository.get_by_id(
                    tag_id=tag_id,
                )

                if tag is None:
                    raise NotFoundException(
                        TestCaseMessages.TAG_NOT_FOUND
                    )

                tags.append(tag)

        update_data = data.model_dump(
            exclude_unset=True,
            exclude={"tag_ids"},
        )

        for field, value in update_data.items():
            setattr(test_case, field, value)

        if tags is not None:
            await self.db.execute(
                delete(TestCaseTag).where(
                    TestCaseTag.test_case_id == test_case.id
                )
            )

            for tag in tags:
                self.db.add(
                    TestCaseTag(
                        test_case_id=test_case.id,
                        tag_id=tag.id,
                    )
                )

        await self.test_case_repository.update(
            test_case=test_case,
        )

        await self.db.commit()

        test_case = await self.test_case_repository.get_by_id(
            test_case_id=test_case.id,
            project_id=project_id,
            module_id=module_id,
        )

        return test_case

    async def delete_test_case(
        self,
        test_case_id: uuid.UUID,
        project_id: uuid.UUID,
        module_id: uuid.UUID,
    ) -> None:

        test_case = await self.test_case_repository.get_by_id(
            test_case_id=test_case_id,
            project_id=project_id,
            module_id=module_id,
        )

        if test_case is None:
            raise NotFoundException(
                TestCaseMessages.TEST_CASE_NOT_FOUND
            )

        await self.test_case_repository.delete(
            test_case=test_case,
        )

        await self.db.commit()