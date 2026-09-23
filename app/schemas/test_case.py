from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# -------------------------
# Test Case Step
# -------------------------

class TestStep(BaseModel):
    step: int = Field(
        ge=1,
    )

    action: str = Field(
        min_length=1,
    )

    expected_result: str = Field(
        min_length=1,
    )


# -------------------------
# Test Case
# -------------------------

class TestCaseCreateRequest(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=255,
    )

    description: str | None = None

    preconditions: list[str] = Field(
        default_factory=list,
    )

    steps: list[TestStep] = Field(
        default_factory=list,
    )

    postconditions: list[str] = Field(
        default_factory=list,
    )

    priority: str = Field(
        default="medium",
        pattern="^(low|medium|high|critical)$",
    )

    status: str = Field(
        default="draft",
        pattern="^(draft|active|inactive)$",
    )

    tag_ids: list[UUID] = Field(
    default_factory=list,
    json_schema_extra={"example": []},
    )


class TestCaseUpdateRequest(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    description: str | None = None

    preconditions: list[str] | None = None

    steps: list[TestStep] | None = None

    postconditions: list[str] | None = None

    priority: str | None = Field(
        default=None,
        pattern="^(low|medium|high|critical)$",
    )

    status: str | None = Field(
        default=None,
        pattern="^(draft|active|inactive)$",
    )

    tag_ids: list[UUID] = Field(
        default_factory=list,
        json_schema_extra={"example": []},
        )


# -------------------------
# Global Tag
# -------------------------

class TagCreateRequest(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
    )


class TagUpdateRequest(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
    )


class TagResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str


# -------------------------
# Test Case Response
# -------------------------

class TestCaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    title: str
    description: str | None

    preconditions: list[str]
    steps: list[TestStep]
    postconditions: list[str]

    priority: str
    status: str

    tags: list[TagResponse] = Field(
        default_factory=list,
    )


class TestCaseListResponse(BaseModel):
    items: list[TestCaseResponse]
    page: int
    page_size: int
    total: int
    total_pages: int