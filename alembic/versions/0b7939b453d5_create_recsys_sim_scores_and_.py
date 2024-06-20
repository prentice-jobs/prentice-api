"""create recsys sim_scores and recommendation cache tables

Revision ID: 0b7939b453d5
Revises: fa73e6dafaad
Create Date: 2024-06-18 13:34:44.532365

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0b7939b453d5'
down_revision: Union[str, None] = 'fa73e6dafaad'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'user_review_similarity_scores',
        sa.Column('id', sa.UUID(), autoincrement=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('is_deleted', sa.Boolean()),

        sa.Column('user_id', sa.UUID()),
        sa.Column('review_id', sa.UUID()),
        sa.Column('sim_score', sa.Float(precision=3)),

        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"],
            name="fk_sim_scores_user",
        ),
        sa.ForeignKeyConstraint(
            ["review_id"], ["company_reviews.id"],
            name="fk_sim_scores_review",
        )
    )

    op.create_table(
        'user_review_recommendations_cache',
        sa.Column('id', sa.UUID(), autoincrement=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('is_deleted', sa.Boolean()),

        sa.Column('user_id', sa.UUID()),
        sa.Column('review_id', sa.UUID()),
        sa.Column('sim_score', sa.Float(precision=3)),

        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"],
            name="fk_sim_scores_user",
        ),
        sa.ForeignKeyConstraint(
            ["review_id"], ["company_reviews.id"],
            name="fk_sim_scores_review",
        )
    )


def downgrade() -> None:
    op.drop_table('user_review_recommendations_cache')
    op.drop_table('user_review_similarity_scores')