from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TestModuleCreateRequest(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=255,
        examples=["Authentication"],
    )
    description: str | None = None


class TestModuleUpdateRequest(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )
    description: str | None = None


class TestModuleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime


class TestModuleListResponse(BaseModel):
    items: list[TestModuleResponse]
    page: int
    page_size: int
    total: int
    total_pages: int