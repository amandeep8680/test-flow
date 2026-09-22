
import uuid

from sqlalchemy import Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ProjectMemberPermission(Base):
    __tablename__ = "project_member_permissions"

    __table_args__ = (
        UniqueConstraint(
            "project_member_id",
            "permission_id",
            name="uq_project_member_permission",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    project_member_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "project_members.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    permission_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "permissions.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    is_allowed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    project_member: Mapped["ProjectMember"] = relationship(
        "ProjectMember",
    )

    permission: Mapped["Permission"] = relationship(
        "Permission",
    )
