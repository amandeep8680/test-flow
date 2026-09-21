from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProjectCreateRequest(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=150,
    )

    key: str = Field(
        min_length=1,
        max_length=50,
    )

    description: str | None = Field(
        default=None,
        max_length=2000,
    )


class ProjectUpdateRequest(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )

    description: str | None = Field(
        default=None,
        max_length=2000,
    )


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    name: str
    key: str
    description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime