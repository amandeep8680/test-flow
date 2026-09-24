from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TestCycleCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    type: str = Field(
        default="functional",
        pattern="^(smoke|regression|functional|integration|release)$",
    )
    status: str = Field(
        default="draft",
        pattern="^(draft|active|completed|archived)$",
    )


class TestCycleUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    type: str | None = Field(
        default=None,
        pattern="^(smoke|regression|functional|integration|release)$",
    )
    status: str | None = Field(
        default=None,
        pattern="^(draft|active|completed|archived)$",
    )


class TestCycleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    name: str
    description: str | None
    type: str
    status: str
    created_at: datetime
    updated_at: datetime


class TestCycleListResponse(BaseModel):
    items: list[TestCycleResponse]
    page: int
    page_size: int
    total: int
    total_pages: int