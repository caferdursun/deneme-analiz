"""Remove description from study_plan_items

Revision ID: ab5235cc1c19
Revises: 7009272fa320
Create Date: 2025-10-31 13:05:04.346802

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision: str = 'ab5235cc1c19'
down_revision: Union[str, None] = '7009272fa320'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop deprecated resource-related tables (if they exist)
    try:
        op.drop_index('ix_youtube_channels_channel_id', table_name='youtube_channels')
        op.drop_index('ix_youtube_channels_is_active', table_name='youtube_channels')
        op.drop_index('ix_youtube_channels_subject_name', table_name='youtube_channels')
        op.drop_table('youtube_channels')
    except:
        pass  # Table may not exist

    try:
        op.drop_index('ix_recommendation_resources_recommendation_id', table_name='recommendation_resources')
        op.drop_index('ix_recommendation_resources_resource_id', table_name='recommendation_resources')
        op.drop_table('recommendation_resources')
    except:
        pass

    try:
        op.drop_index('ix_resource_blacklist_url', table_name='resource_blacklist')
        op.drop_table('resource_blacklist')
    except:
        pass

    try:
        op.drop_table('resources')
    except:
        pass

    # Remove description column from study_plan_items using batch operations for SQLite
    with op.batch_alter_table('study_plan_items', schema=None) as batch_op:
        batch_op.drop_column('description')


def downgrade() -> None:
    # Add description column back to study_plan_items
    with op.batch_alter_table('study_plan_items', schema=None) as batch_op:
        batch_op.add_column(sa.Column('description', sa.TEXT(), nullable=True))

    # Recreate resource tables
    op.create_table('resources',
    sa.Column('id', sa.VARCHAR(length=36), nullable=False),
    sa.Column('name', sa.VARCHAR(length=255), nullable=False),
    sa.Column('type', sa.VARCHAR(length=20), nullable=False),
    sa.Column('url', sa.VARCHAR(length=500), nullable=False),
    sa.Column('description', sa.TEXT(), nullable=True),
    sa.Column('subject_name', sa.VARCHAR(length=50), nullable=True),
    sa.Column('topic', sa.VARCHAR(length=255), nullable=True),
    sa.Column('thumbnail_url', sa.VARCHAR(length=500), nullable=True),
    sa.Column('extra_data', sqlite.JSON(), nullable=True),
    sa.Column('is_active', sa.BOOLEAN(), nullable=True),
    sa.Column('created_at', sa.DATETIME(), nullable=True),
    sa.Column('learning_outcome_ids', sqlite.JSON(), nullable=True),
    sa.Column('quality_score', sa.FLOAT(), nullable=True),
    sa.Column('education_level', sa.VARCHAR(length=20), nullable=True),
    sa.Column('curator_notes', sa.TEXT(), nullable=True),
    sa.Column('is_pinned', sa.BOOLEAN(), server_default=sa.text("'0'"), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('resource_blacklist',
    sa.Column('id', sa.VARCHAR(length=36), nullable=False),
    sa.Column('url', sa.VARCHAR(length=500), nullable=False),
    sa.Column('name', sa.VARCHAR(length=255), nullable=True),
    sa.Column('type', sa.VARCHAR(length=20), nullable=True),
    sa.Column('subject_name', sa.VARCHAR(length=50), nullable=True),
    sa.Column('topic', sa.VARCHAR(length=255), nullable=True),
    sa.Column('reason', sa.TEXT(), nullable=True),
    sa.Column('blacklisted_by', sa.VARCHAR(length=50), nullable=True),
    sa.Column('created_at', sa.DATETIME(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_resource_blacklist_url', 'resource_blacklist', ['url'], unique=1)
    op.create_table('recommendation_resources',
    sa.Column('id', sa.VARCHAR(length=36), nullable=False),
    sa.Column('recommendation_id', sa.VARCHAR(length=36), nullable=False),
    sa.Column('resource_id', sa.VARCHAR(length=36), nullable=False),
    sa.Column('created_at', sa.DATETIME(), nullable=True),
    sa.ForeignKeyConstraint(['recommendation_id'], ['recommendations.id'], ),
    sa.ForeignKeyConstraint(['resource_id'], ['resources.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_recommendation_resources_resource_id', 'recommendation_resources', ['resource_id'], unique=False)
    op.create_index('ix_recommendation_resources_recommendation_id', 'recommendation_resources', ['recommendation_id'], unique=False)
    op.create_table('youtube_channels',
    sa.Column('id', sa.VARCHAR(length=36), nullable=False),
    sa.Column('channel_id', sa.VARCHAR(length=100), nullable=False),
    sa.Column('channel_name', sa.VARCHAR(length=255), nullable=False),
    sa.Column('custom_url', sa.VARCHAR(length=255), nullable=True),
    sa.Column('subject_name', sa.VARCHAR(length=50), nullable=False),
    sa.Column('subscriber_count', sa.INTEGER(), server_default=sa.text("'0'"), nullable=True),
    sa.Column('video_count', sa.INTEGER(), server_default=sa.text("'0'"), nullable=True),
    sa.Column('view_count', sa.INTEGER(), server_default=sa.text("'0'"), nullable=True),
    sa.Column('description', sa.TEXT(), nullable=True),
    sa.Column('thumbnail_url', sa.VARCHAR(length=500), nullable=True),
    sa.Column('trust_score', sa.FLOAT(), server_default=sa.text("'70.0'"), nullable=True),
    sa.Column('is_active', sa.BOOLEAN(), server_default=sa.text("'1'"), nullable=True),
    sa.Column('last_updated', sa.DATETIME(), nullable=True),
    sa.Column('created_at', sa.DATETIME(), nullable=True),
    sa.Column('discovered_via', sa.VARCHAR(length=100), nullable=True),
    sa.Column('notes', sa.TEXT(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('channel_id')
    )
    op.create_index('ix_youtube_channels_subject_name', 'youtube_channels', ['subject_name'], unique=False)
    op.create_index('ix_youtube_channels_is_active', 'youtube_channels', ['is_active'], unique=False)
    op.create_index('ix_youtube_channels_channel_id', 'youtube_channels', ['channel_id'], unique=1)
    # ### end Alembic commands ###
