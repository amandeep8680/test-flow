
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.organization import Organization
from app.core.database import Base


class User(Base):
    """
    Represents a user belonging to an organization.

    Users are isolated by organization_id.
    Authentication credentials are stored securely using
    an Argon2 password hash, never as plain-text passwords.
    """

    __tablename__ = "users"

    # Unique identifier for the user.
    # UUID prevents predictable sequential IDs.
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Organization this user belongs to.
    # Every user must belong to exactly one organization.
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )

    # User's unique email address.
    # Used as one of the login identifiers.
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    # Username used to identify/login as the user.
    username: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    # Argon2 password hash.
    # NEVER store the user's plain-text password here.
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # User's first name.
    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    # User's last name.
    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    # Controls whether the user is allowed to authenticate.
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    # True for newly created users who must change
    # their temporary password during first login.
    must_change_password: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    # Stores the timestamp of the user's most recent
    # successful login.
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Timestamp when the user was created.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # Timestamp when the user was last updated.
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    # user's organization relationship
    organization: Mapped["Organization"] = relationship(
    "Organization",
    back_populates="users",
)

