from pydantic import BaseModel, ConfigDict, EmailStr, Field
from uuid import UUID


class CreateUserRequest(BaseModel):
    """
    Request body for an ADMIN creating a new user.
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
    Response returned after an ADMIN creates a user.
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