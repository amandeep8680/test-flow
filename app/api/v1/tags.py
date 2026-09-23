import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.permissions import require_permission
from app.models.user import User
from app.schemas.test_case import (
    TagCreateRequest,
    TagResponse,
    TagUpdateRequest,
)
from app.services.tag import TagService


router = APIRouter(
    prefix="/tags",
    tags=["Tags"],
)


@router.post(
    "",
    response_model=TagResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_tag(
    data: TagCreateRequest,
    current_user: User = Depends(
        require_permission("test_case.create")
    ),
    db: AsyncSession = Depends(get_db),
):
    service = TagService(db)

    try:
        return await service.create_tag(data=data)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get(
    "",
    response_model=list[TagResponse],
)
async def get_tags(
    current_user: User = Depends(
        require_permission("test_case.view")
    ),
    db: AsyncSession = Depends(get_db),
):
    service = TagService(db)

    return await service.get_tags()


@router.patch(
    "/{tag_id}",
    response_model=TagResponse,
)
async def update_tag(
    tag_id: uuid.UUID,
    data: TagUpdateRequest,
    current_user: User = Depends(
        require_permission("test_case.edit")
    ),
    db: AsyncSession = Depends(get_db),
):
    service = TagService(db)

    try:
        return await service.update_tag(
            tag_id=tag_id,
            data=data,
        )
    except ValueError as exc:
        if str(exc) == "Tag not found.":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.delete(
    "/{tag_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_tag(
    tag_id: uuid.UUID,
    current_user: User = Depends(
        require_permission("test_case.delete")
    ),
    db: AsyncSession = Depends(get_db),
):
    service = TagService(db)

    try:
        await service.delete_tag(
            tag_id=tag_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    return None