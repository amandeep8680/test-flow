from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class OrganizationResponse(BaseModel):
    """
    Response schema for organization information.

    Sensitive or internal database information is not exposed.
    """

    # Allows Pydantic to create this schema directly
    # from a SQLAlchemy model instance.
    model_config = ConfigDict(from_attributes=True)

    # Unique organization identifier.
    id: UUID

    # Human-readable organization name.
    name: str

    # Unique URL/API-friendly organization identifier.
    slug: str

    # Indicates whether the organization is active.
    is_active: bool

    # Organization creation timestamp.
    created_at: datetime

    # Last update timestamp.
    updated_at: datetime

