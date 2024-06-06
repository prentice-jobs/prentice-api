"""companies_table

Revision ID: a7b928039058
Revises: 1b457608f2ef
Create Date: 2024-06-05 12:37:27.542387

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a7b928039058'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'companies',
        sa.Column('id', sa.UUID(), autoincrement=False, nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('is_deleted', sa.BOOLEAN(),
                  autoincrement=False, nullable=True),

        sa.Column('display_name', sa.VARCHAR(length=225),
                  autoincrement=False, nullable=False),
        sa.Column('description', sa.VARCHAR(length=255),
                  autoincrement=False, nullable=True),
        sa.Column('logo_url', sa.VARCHAR(length=225),
                  autoincrement=False, nullable=False),
        sa.Column('star_rating', sa.Float(precision=1), nullable=False),
        sa.Column('company_sentiment', sa.Float(precision=1), nullable=False),
        sa.Column('tags', sa.ARRAY(item_type=sa.String), nullable=True),
        sa.Column('review_count', sa.Integer(), nullable=False),
        sa.Column('company_review', sa.ARRAY(
            item_type=sa.UUID()), nullable=True),

        sa.PrimaryKeyConstraint('id', name='pk_company_id'),
    )


def downgrade() -> None:
    pass
