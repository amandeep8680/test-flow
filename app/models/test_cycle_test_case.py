
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TestCycleTestCase(Base):
    __tablename__ = "test_cycle_test_cases"

    __table_args__ = (
        UniqueConstraint(
            "test_cycle_id",
            "test_case_id",
            name="uq_test_cycle_test_case",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    test_cycle_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("test_cycles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    test_case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("test_cases.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    test_cycle = relationship(
        "TestCycle",
        back_populates="test_cycle_test_cases",
    )

    test_case = relationship(
        "TestCase",
        back_populates="test_cycle_test_cases",
    )
