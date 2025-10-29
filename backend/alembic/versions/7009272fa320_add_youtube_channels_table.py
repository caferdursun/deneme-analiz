"""Add youtube_channels table

Revision ID: 7009272fa320
Revises: a313e8bc7189
Create Date: 2025-10-29 16:13:54.202528

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7009272fa320'
down_revision: Union[str, None] = 'a313e8bc7189'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create youtube_channels table
    op.create_table(
        'youtube_channels',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('channel_id', sa.String(length=100), nullable=False),
        sa.Column('channel_name', sa.String(length=255), nullable=False),
        sa.Column('custom_url', sa.String(length=255), nullable=True),
        sa.Column('subject_name', sa.String(length=50), nullable=False),
        sa.Column('subscriber_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('video_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('view_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('thumbnail_url', sa.String(length=500), nullable=True),
        sa.Column('trust_score', sa.Float(), nullable=True, server_default='70.0'),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='1'),
        sa.Column('last_updated', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('discovered_via', sa.String(length=100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('channel_id')
    )
    op.create_index(op.f('ix_youtube_channels_channel_id'), 'youtube_channels', ['channel_id'], unique=True)
    op.create_index(op.f('ix_youtube_channels_subject_name'), 'youtube_channels', ['subject_name'], unique=False)
    op.create_index(op.f('ix_youtube_channels_is_active'), 'youtube_channels', ['is_active'], unique=False)


def downgrade() -> None:
    # Drop youtube_channels table
    op.drop_index(op.f('ix_youtube_channels_is_active'), table_name='youtube_channels')
    op.drop_index(op.f('ix_youtube_channels_subject_name'), table_name='youtube_channels')
    op.drop_index(op.f('ix_youtube_channels_channel_id'), table_name='youtube_channels')
    op.drop_table('youtube_channels')
