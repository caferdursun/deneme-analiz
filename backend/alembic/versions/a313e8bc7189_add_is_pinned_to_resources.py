"""add_is_pinned_to_resources

Revision ID: a313e8bc7189
Revises: 1fd617418fe7
Create Date: 2025-10-27 16:42:34.191789

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a313e8bc7189'
down_revision: Union[str, None] = '1fd617418fe7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add is_pinned column to resources table
    op.add_column('resources', sa.Column('is_pinned', sa.Boolean(), nullable=False, server_default='0'))


def downgrade() -> None:
    # Remove is_pinned column from resources table
    op.drop_column('resources', 'is_pinned')
