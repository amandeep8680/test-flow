from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TestStepExecutionUpdateRequest(BaseModel):
    status: str = Field(
        pattern="^(not_run|passed|failed|blocked|skipped)$",
    )
    actual_result: str | None = None
    notes: str | None = None


class TestStepExecutionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    test_execution_id: UUID
    test_step_id: UUID
    step_number: int
    status: str
    actual_result: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime