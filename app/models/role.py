import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Role(Base):
    """
    Represents a role that defines a user's authorization level.

    Roles are controlled by the backend.
    Users cannot assign themselves roles.
    An ADMIN is responsible for assigning roles to users.
    """

    __tablename__ = "roles"

    # Unique identifier for the role.
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Unique role name.
    #
    # Initial system roles:
    # ADMIN
    # QA
    # DEVELOPER
    # VIEWER
    #
    # Keeping this as a database value instead of a Python Enum
    # allows new roles to be added in the future.
    name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    # Timestamp when the role was created.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
