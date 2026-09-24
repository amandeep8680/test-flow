import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TestCase(Base):
    __tablename__ = "test_cases"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    preconditions: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )


    postconditions: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    priority: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="medium",
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="draft",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    project = relationship(
        "Project",
        back_populates="test_cases",
    )

    test_steps = relationship(
            "TestStep",
            back_populates="test_case",
            cascade="all, delete-orphan",
            order_by="TestStep.step_number",
        )
    
    test_case_tags = relationship(
        "TestCaseTag",
        back_populates="test_case",
        cascade="all, delete-orphan",
    )