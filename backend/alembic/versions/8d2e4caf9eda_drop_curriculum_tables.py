"""drop_curriculum_tables

Revision ID: 8d2e4caf9eda
Revises: ffdbec01cad2
Create Date: 2025-11-01 11:07:35.908936

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8d2e4caf9eda'
down_revision: Union[str, None] = 'ffdbec01cad2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop curriculum tables in correct order (child tables first)
    op.drop_table('curriculum_topics')
    op.drop_table('curriculum_units')
    op.drop_table('curriculum_grades')
    op.drop_table('curriculum_subjects')


def downgrade() -> None:
    # Recreate tables if needed (from previous migrations)
    # curriculum_subjects
    op.create_table(
        'curriculum_subjects',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('subject_name', sa.String(100), nullable=False, unique=True),
        sa.Column('order', sa.Integer, nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False),
    )

    # curriculum_grades
    op.create_table(
        'curriculum_grades',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('subject_id', sa.String(36), nullable=False),
        sa.Column('grade', sa.String(10), nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.ForeignKeyConstraint(['subject_id'], ['curriculum_subjects.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_curriculum_grades_subject_id', 'curriculum_grades', ['subject_id'])

    # curriculum_units
    op.create_table(
        'curriculum_units',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('grade_id', sa.String(36), nullable=False),
        sa.Column('unit_no', sa.Integer, nullable=False),
        sa.Column('unit_name', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.ForeignKeyConstraint(['grade_id'], ['curriculum_grades.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_curriculum_units_grade_id', 'curriculum_units', ['grade_id'])

    # curriculum_topics
    op.create_table(
        'curriculum_topics',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('unit_id', sa.String(36), nullable=False),
        sa.Column('topic_name', sa.String(500), nullable=False),
        sa.Column('order', sa.Integer, nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.ForeignKeyConstraint(['unit_id'], ['curriculum_units.id'], ondelete='CASCADE'),
    )
    op.create_index('ix_curriculum_topics_unit_id', 'curriculum_topics', ['unit_id'])
