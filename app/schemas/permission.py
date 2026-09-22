from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PermissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None


class PermissionCreateRequest(BaseModel):
    resource: str = Field(
        min_length=1,
        max_length=50,
    )

    action: str = Field(
        min_length=1,
        max_length=50,
    )

    description: str | None = None
