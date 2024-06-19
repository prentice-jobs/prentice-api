"""Add company_reviews table

Revision ID: d5d068b44817
Revises: 61c33e0f05b6
Create Date: 2024-06-11 12:04:02.349641

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd5d068b44817'
down_revision: Union[str, None] = '61c33e0f05b6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'company_reviews',
        sa.Column('id', sa.UUID(), autoincrement=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('is_deleted', sa.Boolean()),
        
        sa.Column('company_id', sa.UUID()),
        sa.Column('author_id', sa.UUID()),
        sa.Column('location', sa.String(200)),
        sa.Column('is_remote', sa.Boolean()),
        
        sa.Column('tags', sa.String(500)),
        sa.Column('star_rating', sa.Float(precision=1)),

        sa.Column('title', sa.String(255)),
        sa.Column('description', sa.String()),
        sa.Column('role', sa.String(255)),

        sa.Column('start_date', sa.TIMESTAMP(timezone=True)),
        sa.Column('end_date', sa.TIMESTAMP(timezone=True)),

        sa.Column('offer_letter_url', sa.String()),
        sa.Column('annual_salary', sa.BigInteger()),
        sa.Column('salary_currency', sa.String(3)),

        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('company_reviews')
