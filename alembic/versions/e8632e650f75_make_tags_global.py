"""make tags global

Revision ID: e8632e650f75
Revises: bc579bd07f52
Create Date: 2026-09-23 11:48:27.541726

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e8632e650f75"
down_revision: Union[str, Sequence[str], None] = "bc579bd07f52"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---------------------------------------------------------
    # 1. Merge duplicate tag names
    # ---------------------------------------------------------
    #
    # If the old database has:
    #
    # Project A -> "smoke"
    # Project B -> "smoke"
    #
    # keep the first tag and move all test-case references
    # to that tag.
    #
    # If the same test case is already linked to both duplicate
    # tags, remove the duplicate relation first.
    #
    op.execute(
        sa.text(
            """
            DO $$
            DECLARE
                duplicate_tag RECORD;
            BEGIN
                FOR duplicate_tag IN
                    SELECT
                        duplicate.id AS duplicate_id,
                        canonical.id AS canonical_id
                    FROM tags AS duplicate
                    JOIN tags AS canonical
                        ON canonical.name = duplicate.name
                       AND canonical.id < duplicate.id
                LOOP

                    -- Remove duplicate test-case/tag relations
                    -- where the canonical relation already exists.
                    DELETE FROM test_case_tags AS tct
                    WHERE tct.tag_id = duplicate_tag.duplicate_id
                      AND EXISTS (
                          SELECT 1
                          FROM test_case_tags AS existing
                          WHERE existing.test_case_id = tct.test_case_id
                            AND existing.tag_id = duplicate_tag.canonical_id
                      );

                    -- Move remaining relations to canonical tag.
                    UPDATE test_case_tags
                    SET tag_id = duplicate_tag.canonical_id
                    WHERE tag_id = duplicate_tag.duplicate_id;

                    -- Delete duplicate tag.
                    DELETE FROM tags
                    WHERE id = duplicate_tag.duplicate_id;

                END LOOP;
            END
            $$;
            """
        )
    )

    # ---------------------------------------------------------
    # 2. Remove old project_id foreign key
    # ---------------------------------------------------------

    op.drop_constraint(
        "tags_project_id_fkey",
        "tags",
        type_="foreignkey",
    )

    # ---------------------------------------------------------
    # 3. Remove project_id column
    # ---------------------------------------------------------

    op.drop_column(
        "tags",
        "project_id",
    )

    # ---------------------------------------------------------
    # 4. Make tag name globally unique
    # ---------------------------------------------------------

    op.create_unique_constraint(
        "uq_tags_name",
        "tags",
        ["name"],
    )


def downgrade() -> None:
    # ---------------------------------------------------------
    # 1. Remove global unique constraint
    # ---------------------------------------------------------

    op.drop_constraint(
        "uq_tags_name",
        "tags",
        type_="unique",
    )

    # ---------------------------------------------------------
    # 2. Add project_id back
    # ---------------------------------------------------------

    op.add_column(
        "tags",
        sa.Column(
            "project_id",
            sa.UUID(),
            nullable=True,
        ),
    )

    # ---------------------------------------------------------
    # 3. Recreate project foreign key
    # ---------------------------------------------------------

    op.create_foreign_key(
        "tags_project_id_fkey",
        "tags",
        "projects",
        ["project_id"],
        ["id"],
        ondelete="CASCADE",
    )