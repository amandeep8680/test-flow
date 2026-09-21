from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ProjectMemberCreateRequest(BaseModel):
    user_id: UUID

    role: str = Field(
        min_length=1,
        max_length=50,
    )


class ProjectMemberUpdateRoleRequest(BaseModel):
    role: str = Field(
        min_length=1,
        max_length=50,
    )


class ProjectMemberResponse(BaseModel):
    id: UUID
    project_id: UUID
    user_id: UUID
    role: str
    created_at: datetime
    updated_at: datetime