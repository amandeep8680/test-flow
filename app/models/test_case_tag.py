import uuid

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TestCaseTag(Base):
    __tablename__ = "test_case_tags"

    __table_args__ = (
        UniqueConstraint(
            "test_case_id",
            "tag_id",
            name="uq_test_case_tag",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    test_case_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("test_cases.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    tag_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tags.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    test_case = relationship(
        "TestCase",
        back_populates="test_case_tags",
    )

    tag = relationship(
        "Tag",
        back_populates="test_case_tags",
    )