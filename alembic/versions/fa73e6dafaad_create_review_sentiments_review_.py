"""Create review_sentiments, review_comments, and review_comment_likes tables

Revision ID: fa73e6dafaad
Revises: d5d068b44817
Create Date: 2024-06-11 15:13:04.546383

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fa73e6dafaad'
down_revision: Union[str, None] = 'd5d068b44817'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "review_sentiments",
        sa.Column('id', sa.UUID(), autoincrement=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('is_deleted', sa.Boolean()),

        sa.Column('review_id', sa.UUID()),
        sa.Column('sentiment_score', sa.SmallInteger()),
        sa.Column('sentiment', sa.String(30)),
    )

    op.create_table(
        "review_comments",
        sa.Column('id', sa.UUID(), autoincrement=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('is_deleted', sa.Boolean()),

        sa.Column('review_id', sa.UUID()),
        sa.Column('author_id', sa.UUID()),
        sa.Column('likes_count', sa.Integer()),
        sa.Column('content', sa.String(1000))
    )

    op.create_table(
        "review_comment_likes",
        sa.Column('id', sa.UUID(), autoincrement=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('is_deleted', sa.Boolean()),

        sa.Column('review_comment_id', sa.UUID()),
        sa.Column('liker_id', sa.UUID()),
    )


def downgrade() -> None:
    op.drop_table("review_sentiments")
    op.drop_table("review_comments")
    op.drop_table("review_comment_likes")
