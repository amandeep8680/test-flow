
from uuid import UUID

from pydantic import BaseModel, Field


class TestCycleTestCaseAddRequest(BaseModel):
    test_case_ids: list[UUID] = Field(
        min_length=1,
        examples=[
            [
                "550e8400-e29b-41d4-a716-446655440000",
                "650e8400-e29b-41d4-a716-446655440001",
            ]
        ],
    )


class TestCycleTestCaseResponse(BaseModel):
    id: UUID
    title: str
    description: str | None
    priority: str
    status: str


class TestCycleTestCaseListResponse(BaseModel):
    items: list[TestCycleTestCaseResponse]
    total: int
