from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class OrganizationSignupRequest(BaseModel):
    """
    Request body for creating a new organization
    together with its initial ADMIN user.
    """

    organization_name: str = Field(
        min_length=1,
        max_length=150,
    )

    organization_slug: str = Field(
        min_length=1,
        max_length=150,
    )

    admin_email: EmailStr

    admin_username: str = Field(
        min_length=3,
        max_length=100,
    )

    admin_password: str = Field(
        min_length=8,
        max_length=128,
    )

    admin_first_name: str = Field(
        min_length=1,
        max_length=100,
    )

    admin_last_name: str = Field(
        min_length=1,
        max_length=100,
    )


class LoginRequest(BaseModel):
    """
    Request body used when a user logs into the system.
    """

    email: EmailStr

    password: str = Field(
        min_length=1,
        max_length=128,
    )


class UserResponse(BaseModel):
    """
    Public user information returned by the API.

    Sensitive fields such as password_hash are intentionally
    excluded from the response.
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
    roles: list[str] = Field(default_factory=list)

class TokenResponse(BaseModel):
    """
    Authentication response containing access and refresh tokens.
    """

    access_token: str
    refresh_token: str
    token_type: str = "bearer"

    user: UserResponse
    roles: list[str]


class ChangePasswordRequest(BaseModel):
    """
    Request body used to change the current user's password.
    """

    current_password: str = Field(
        min_length=1,
        max_length=128,
    )

    new_password: str = Field(
        min_length=8,
        max_length=128,
    )


class RefreshTokenRequest(BaseModel):
    """
    Request body used to refresh an access token.
    """

    refresh_token: str = Field(
        min_length=1,
    )