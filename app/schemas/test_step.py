
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# =========================================================
# CREATE
# =========================================================

class TestStepCreateRequest(BaseModel):
    step_number: int = Field(
        ge=1,
        examples=[1],
    )

    action: str = Field(
        min_length=1,
        max_length=2000,
    )

    expected_result: str = Field(
        min_length=1,
        max_length=2000,
    )


# =========================================================
# UPDATE
# =========================================================

class TestStepUpdateRequest(BaseModel):
    step_number: int | None = Field(
        default=None,
        ge=1,
    )

    action: str | None = Field(
        default=None,
        min_length=1,
        max_length=2000,
    )

    expected_result: str | None = Field(
        default=None,
        min_length=1,
        max_length=2000,
    )


# =========================================================
# RESPONSE
# =========================================================

class TestStepResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    test_case_id: UUID

    step_number: int
    action: str
    expected_result: str

    created_at: datetime
    updated_at: datetime


# =========================================================
# LIST RESPONSE
# =========================================================

class TestStepListResponse(BaseModel):
    items: list[TestStepResponse]

    page: int
    page_size: int

    total: int
    total_pages: int

# =========================================================
# REORDER RESPONSE
# =========================================================



class TestStepReorderRequest(BaseModel):
    step_ids: list[UUID] = Field(
        min_length=1,
        examples=[
            [
                "550e8400-e29b-41d4-a716-446655440000",
            ]
        ],
    )
