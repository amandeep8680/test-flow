
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CreateUserRequest(BaseModel):
    """
    Request body for creating a new user.
    """

    email: EmailStr

    username: str = Field(
        min_length=3,
        max_length=100,
    )

    first_name: str = Field(
        min_length=1,
        max_length=100,
    )

    last_name: str = Field(
        min_length=1,
        max_length=100,
    )

    role: str = Field(
        min_length=1,
        max_length=50,
    )


class CreateUserResponse(BaseModel):
    """
    Response returned after creating a user.
    """

    id: UUID
    organization_id: UUID
    email: EmailStr
    username: str
    first_name: str
    last_name: str
    role: str
    is_active: bool
    must_change_password: bool
    temporary_password: str


class UserResponse(BaseModel):
    """
    Response returned when fetching users.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    email: EmailStr
    username: str
    first_name: str
    last_name: str
    is_active: bool
    must_change_password: bool

