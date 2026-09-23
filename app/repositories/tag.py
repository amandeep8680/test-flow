import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tag import Tag


class TagRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(
        self,
        tag_id: uuid.UUID,
    ) -> Tag | None:
        result = await self.db.execute(
            select(Tag).where(
                Tag.id == tag_id,
            )
        )

        return result.scalar_one_or_none()

    async def get_by_name(
        self,
        name: str,
    ) -> Tag | None:
        result = await self.db.execute(
            select(Tag).where(
                Tag.name == name,
            )
        )

        return result.scalar_one_or_none()

    async def get_all(self) -> list[Tag]:
        result = await self.db.execute(
            select(Tag)
            .order_by(Tag.name.asc())
        )

        return list(result.scalars().all())

    async def create(
        self,
        tag: Tag,
    ) -> Tag:
        self.db.add(tag)

        await self.db.flush()
        await self.db.refresh(tag)

        return tag

    async def update(
        self,
        tag: Tag,
    ) -> Tag:
        await self.db.flush()
        await self.db.refresh(tag)

        return tag

    async def delete(
        self,
        tag: Tag,
    ) -> None:
        await self.db.delete(tag)
        await self.db.flush()