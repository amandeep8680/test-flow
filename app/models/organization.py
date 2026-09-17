import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column , relationship

from app.core.database import Base


class Organization(Base):
    """
    Represents an organization/tenant in the system.

    Each organization is isolated from other organizations.
    Users belong to an organization through organization_id.
    """

    __tablename__ = "organizations"

    # Unique identifier for the organization.
    # UUID is used instead of sequential integer IDs.
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Human-readable organization name.
    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    # URL/API-friendly unique identifier for the organization.
    # Example: "acme-corp"
    slug: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        nullable=False,
        index=True,
    )

    # Controls whether the organization is allowed to use the system.
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    # Timestamp when the organization was created.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # Timestamp when the organization was last updated.
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    users: Mapped[list["User"]] = relationship(
        "User",
        back_populates="organization",
    )