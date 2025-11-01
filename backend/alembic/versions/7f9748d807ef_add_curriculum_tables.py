"""Add curriculum tables

Revision ID: 7f9748d807ef
Revises: ab5235cc1c19
Create Date: 2025-10-31 14:04:21.265775

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7f9748d807ef'
down_revision: Union[str, None] = 'ab5235cc1c19'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create curriculum_subjects table
    op.create_table(
        'curriculum_subjects',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('grade', sa.String(length=2), nullable=False),
        sa.Column('subject_name', sa.String(length=100), nullable=False),
        sa.Column('order', sa.Integer(), nullable=True, server_default='99'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_curriculum_subjects_grade', 'curriculum_subjects', ['grade'])
    op.create_index('ix_curriculum_subjects_subject_name', 'curriculum_subjects', ['subject_name'])

    # Create curriculum_units table
    op.create_table(
        'curriculum_units',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('subject_id', sa.String(length=36), nullable=False),
        sa.Column('unit_no', sa.Integer(), nullable=False),
        sa.Column('unit_name', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['subject_id'], ['curriculum_subjects.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_curriculum_units_subject_id', 'curriculum_units', ['subject_id'])

    # Create curriculum_topics table
    op.create_table(
        'curriculum_topics',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('unit_id', sa.String(length=36), nullable=False),
        sa.Column('topic_name', sa.String(length=500), nullable=False),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['unit_id'], ['curriculum_units.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_curriculum_topics_unit_id', 'curriculum_topics', ['unit_id'])


def downgrade() -> None:
    # Drop curriculum tables
    op.drop_index('ix_curriculum_topics_unit_id', table_name='curriculum_topics')
    op.drop_table('curriculum_topics')
    op.drop_index('ix_curriculum_units_subject_id', table_name='curriculum_units')
    op.drop_table('curriculum_units')
    op.drop_index('ix_curriculum_subjects_subject_name', table_name='curriculum_subjects')
    op.drop_index('ix_curriculum_subjects_grade', table_name='curriculum_subjects')
    op.drop_table('curriculum_subjects')
