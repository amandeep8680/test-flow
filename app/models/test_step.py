
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TestStep(Base):
    __tablename__ = "test_steps"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    test_case_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("test_cases.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    step_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    action: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    expected_result: Mapped[str] = mapped_column(
        Text,
        nullable=False,
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

    test_case = relationship(
        "TestCase",
        back_populates="test_steps",
    )
