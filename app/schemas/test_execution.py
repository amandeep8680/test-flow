from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TestExecutionCreateRequest(BaseModel):
    test_case_id: UUID
    status: str = Field(
        default="not_run",
        pattern="^(not_run|passed|failed|blocked|skipped)$",
    )
    actual_result: str | None = None
    notes: str | None = None


class TestExecutionUpdateRequest(BaseModel):
    status: str | None = Field(
        default=None,
        pattern="^(not_run|passed|failed|blocked|skipped)$",
    )
    actual_result: str | None = None
    notes: str | None = None


class TestExecutionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    test_cycle_id: UUID
    test_case_id: UUID
    status: str
    actual_result: str | None
    notes: str | None
    executed_at: datetime | None
    created_at: datetime
    updated_at: datetime


class TestExecutionListResponse(BaseModel):
    items: list[TestExecutionResponse]
    page: int
    page_size: int
    total: int
    total_pages: int