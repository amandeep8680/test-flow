import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tag import Tag
from app.repositories.tag import TagRepository
from app.schemas.test_case import TagCreateRequest, TagUpdateRequest


class TagService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = TagRepository(db)

    async def get_tag(
        self,
        tag_id: uuid.UUID,
    ) -> Tag | None:
        return await self.repository.get_by_id(
            tag_id=tag_id,
        )

    async def get_tags(self) -> list[Tag]:
        return await self.repository.get_all()

    async def create_tag(
        self,
        data: TagCreateRequest,
    ) -> Tag:
        existing_tag = await self.repository.get_by_name(
            name=data.name,
        )

        if existing_tag is not None:
            raise ValueError(
                "A tag with this name already exists."
            )

        tag = Tag(
            name=data.name,
        )

        tag = await self.repository.create(tag)

        await self.db.commit()
        await self.db.refresh(tag)

        return tag

    async def update_tag(
        self,
        tag_id: uuid.UUID,
        data: TagUpdateRequest,
    ) -> Tag:
        tag = await self.repository.get_by_id(
            tag_id=tag_id,
        )

        if tag is None:
            raise ValueError("Tag not found.")

        existing_tag = await self.repository.get_by_name(
            name=data.name,
        )

        if existing_tag is not None and existing_tag.id != tag.id:
            raise ValueError(
                "A tag with this name already exists."
            )

        tag.name = data.name

        tag = await self.repository.update(tag)

        await self.db.commit()
        await self.db.refresh(tag)

        return tag

    async def delete_tag(
        self,
        tag_id: uuid.UUID,
    ) -> None:
        tag = await self.repository.get_by_id(
            tag_id=tag_id,
        )

        if tag is None:
            raise ValueError("Tag not found.")

        await self.repository.delete(tag)

        await self.db.commit()