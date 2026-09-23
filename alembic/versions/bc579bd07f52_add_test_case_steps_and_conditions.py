"""add test case steps and conditions

Revision ID: bc579bd07f52
Revises: d7e3d3b97c64
Create Date: 2026-09-23 10:51:27.578197

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "bc579bd07f52"
down_revision: Union[str, Sequence[str], None] = "d7e3d3b97c64"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Existing preconditions column was TEXT.
    # Drop it because we are changing its structure to JSON.
    op.drop_column(
        "test_cases",
        "preconditions",
    )

    # Recreate preconditions as JSON list.
    op.add_column(
        "test_cases",
        sa.Column(
            "preconditions",
            sa.JSON(),
            nullable=False,
            server_default="[]",
        ),
    )

    # Add test steps.
    op.add_column(
        "test_cases",
        sa.Column(
            "steps",
            sa.JSON(),
            nullable=False,
            server_default="[]",
        ),
    )

    # Add postconditions.
    op.add_column(
        "test_cases",
        sa.Column(
            "postconditions",
            sa.JSON(),
            nullable=False,
            server_default="[]",
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column(
        "test_cases",
        "postconditions",
    )

    op.drop_column(
        "test_cases",
        "steps",
    )

    op.drop_column(
        "test_cases",
        "preconditions",
    )

    # Restore the original TEXT column.
    op.add_column(
        "test_cases",
        sa.Column(
            "preconditions",
            sa.Text(),
            nullable=True,
        ),
    )