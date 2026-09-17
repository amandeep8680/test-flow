
import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class UserRole(Base):
    """
    Association table between users and roles.

    A user can have multiple roles in the future,
    and a role can belong to multiple users.

    Example:

        User A -> ADMIN
        User A -> QA
        User B -> DEVELOPER
    """

    __tablename__ = "user_roles"

    # ID of the user receiving the role.
    # References users.id.
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )

    # ID of the assigned role.
    # References roles.id.
    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    )
