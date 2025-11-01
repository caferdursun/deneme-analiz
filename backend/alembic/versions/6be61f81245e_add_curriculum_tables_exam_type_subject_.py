"""add_curriculum_tables_exam_type_subject_topic

Revision ID: 6be61f81245e
Revises: 8d2e4caf9eda
Create Date: 2025-11-01 11:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6be61f81245e'
down_revision: Union[str, None] = '8d2e4caf9eda'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create exam_types table
    op.create_table(
        'exam_types',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(50), nullable=False, unique=True),
        sa.Column('display_name', sa.String(100), nullable=False),
        sa.Column('order', sa.Integer, nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False),
    )
    op.create_index('ix_exam_types_name', 'exam_types', ['name'])

    # Create subjects table
    op.create_table(
        'subjects',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('exam_type_id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('order', sa.Integer, nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.ForeignKeyConstraint(['exam_type_id'], ['exam_types.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_subjects_exam_type_id', 'subjects', ['exam_type_id'])
    op.create_index('ix_subjects_name', 'subjects', ['name'])

    # Create topics table
    op.create_table(
        'topics',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('subject_id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(500), nullable=False),
        sa.Column('grade_info', sa.String(50), nullable=True),  # e.g., "9", "9,10", "9,10,11"
        sa.Column('order', sa.Integer, nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.ForeignKeyConstraint(['subject_id'], ['subjects.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_topics_subject_id', 'topics', ['subject_id'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('topics')
    op.drop_table('subjects')
    op.drop_table('exam_types')
