import uuid

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.test_case import TestCase
from app.models.test_case_tag import TestCaseTag
from app.repositories.tag import TagRepository
from app.repositories.test_case import TestCaseRepository
from app.schemas.test_case import (
    TestCaseCreateRequest,
    TestCaseUpdateRequest,
)


class TestCaseService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.test_case_repository = TestCaseRepository(db)
        self.tag_repository = TagRepository(db)

    async def get_test_case(
        self,
        test_case_id: uuid.UUID,
        project_id: uuid.UUID,
    ) -> TestCase | None:
        return await self.test_case_repository.get_by_id(
            test_case_id=test_case_id,
            project_id=project_id,
        )

    async def get_test_cases(
        self,
        project_id: uuid.UUID,
    ) -> list[TestCase]:
        return await self.test_case_repository.get_all(
            project_id=project_id,
        )

    async def create_test_case(
        self,
        project_id: uuid.UUID,
        data: TestCaseCreateRequest,
    ) -> TestCase:

        tags = []

        # Validate global tags
        for tag_id in data.tag_ids:
            tag = await self.tag_repository.get_by_id(
                tag_id=tag_id,
            )

            if tag is None:
                raise ValueError(
                    f"Tag {tag_id} does not exist."
                )

            tags.append(tag)

        test_case = TestCase(
            project_id=project_id,
            title=data.title,
            description=data.description,
            preconditions=data.preconditions,
            steps=[
                step.model_dump()
                for step in data.steps
            ],
            postconditions=data.postconditions,
            priority=data.priority,
            status=data.status,
        )

        test_case = await self.test_case_repository.create(
            test_case=test_case,
        )

        # Attach multiple tags if provided
        for tag in tags:
            self.db.add(
                TestCaseTag(
                    test_case_id=test_case.id,
                    tag_id=tag.id,
                )
            )

        await self.db.commit()

        # Re-fetch with tags eagerly loaded
        test_case = await self.test_case_repository.get_by_id(
            test_case_id=test_case.id,
            project_id=project_id,
        )

        return test_case

    async def update_test_case(
        self,
        test_case_id: uuid.UUID,
        project_id: uuid.UUID,
        data: TestCaseUpdateRequest,
    ) -> TestCase:

        test_case = await self.test_case_repository.get_by_id(
            test_case_id=test_case_id,
            project_id=project_id,
        )

        if test_case is None:
            raise ValueError("Test case not found.")

        # None = tags were not included in update request
        tags = None

        if data.tag_ids is not None:
            tags = []

            # Validate global tags
            for tag_id in data.tag_ids:
                tag = await self.tag_repository.get_by_id(
                    tag_id=tag_id,
                )

                if tag is None:
                    raise ValueError(
                        f"Tag {tag_id} does not exist."
                    )

                tags.append(tag)

        update_data = data.model_dump(
            exclude_unset=True,
            exclude={"tag_ids"},
        )

        if "steps" in update_data and data.steps is not None:
            update_data["steps"] = [
                step.model_dump()
                for step in data.steps
            ]

        for field, value in update_data.items():
            setattr(test_case, field, value)

        # If tag_ids was provided:
        # replace existing tags with the new list.
        #
        # [] means remove all tags.
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

        # Re-fetch with tags eagerly loaded
        test_case = await self.test_case_repository.get_by_id(
            test_case_id=test_case.id,
            project_id=project_id,
        )

        return test_case

    async def delete_test_case(
        self,
        test_case_id: uuid.UUID,
        project_id: uuid.UUID,
    ) -> None:

        test_case = await self.test_case_repository.get_by_id(
            test_case_id=test_case_id,
            project_id=project_id,
        )

        if test_case is None:
            raise ValueError("Test case not found.")

        await self.test_case_repository.delete(
            test_case=test_case,
        )

        await self.db.commit()