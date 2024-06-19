"""Add User and UserPreferences model

Revision ID: 61c33e0f05b6
Revises: a7b928039058
Create Date: 2024-06-06 16:15:17.921800

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '61c33e0f05b6'
down_revision: Union[str, None] = 'a7b928039058'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.UUID(), autoincrement=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('is_deleted', sa.Boolean()),
        
        sa.Column('firebase_uid', sa.String(255)),
        sa.Column('email', sa.String(255)),
        sa.Column('display_name', sa.String(255), nullable=True),
        sa.Column('photo_url', sa.String(), nullable=True),
        sa.Column('email_verified', sa.Boolean()),

        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
    )

    op.create_table(
        'user_preferences',
        sa.Column('id', sa.UUID(), autoincrement=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('is_deleted', sa.Boolean()),

        sa.Column('role', sa.String(255)),
        sa.Column('industry', sa.String(255)),
        sa.Column('location', sa.String(255)),

        sa.Column('user_id', sa.UUID(), nullable=False),

        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"],
            name='fk_preferences_user'
        ),
    )


def downgrade() -> None:
    op.drop_table('users')
    op.drop_table('user_preferences')
