"""restructure curriculum schema: subject->grade->unit->topic

Revision ID: ffdbec01cad2
Revises: 7f9748d807ef
Create Date: 2025-10-31 14:24:18.481462

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ffdbec01cad2'
down_revision: Union[str, None] = '7f9748d807ef'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # SQLite-compatible migration: Drop and recreate curriculum tables
    # Use bind to execute raw SQL with IF EXISTS for SQLite
    bind = op.get_bind()
    bind.execute(sa.text('DROP TABLE IF EXISTS curriculum_topics'))
    bind.execute(sa.text('DROP TABLE IF EXISTS curriculum_units'))
    bind.execute(sa.text('DROP TABLE IF EXISTS curriculum_grades'))
    bind.execute(sa.text('DROP TABLE IF EXISTS curriculum_subjects'))

    # Create new curriculum_subjects table (top level: Ders)
    op.create_table(
        'curriculum_subjects',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('subject_name', sa.String(length=100), nullable=False),
        sa.Column('order', sa.Integer(), nullable=True, server_default='99'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_curriculum_subjects_subject_name'), 'curriculum_subjects', ['subject_name'], unique=True)

    # Create new curriculum_grades table (second level: Sınıf)
    op.create_table(
        'curriculum_grades',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('subject_id', sa.String(length=36), nullable=False),
        sa.Column('grade', sa.String(length=2), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['subject_id'], ['curriculum_subjects.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_curriculum_grades_grade'), 'curriculum_grades', ['grade'], unique=False)
    op.create_index(op.f('ix_curriculum_grades_subject_id'), 'curriculum_grades', ['subject_id'], unique=False)

    # Create new curriculum_units table (third level: Ünite)
    op.create_table(
        'curriculum_units',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('grade_id', sa.String(length=36), nullable=False),
        sa.Column('unit_no', sa.Integer(), nullable=False),
        sa.Column('unit_name', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['grade_id'], ['curriculum_grades.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_curriculum_units_grade_id'), 'curriculum_units', ['grade_id'], unique=False)

    # Create new curriculum_topics table (fourth level: Konu)
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
    op.create_index(op.f('ix_curriculum_topics_unit_id'), 'curriculum_topics', ['unit_id'], unique=False)


def downgrade() -> None:
    # Reverse the schema restructuring
    op.drop_table('curriculum_topics')
    op.drop_table('curriculum_units')
    op.drop_table('curriculum_grades')
    op.drop_table('curriculum_subjects')

    # Recreate old structure (grade+subject combined in subjects table)
    op.create_table(
        'curriculum_subjects',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('grade', sa.String(length=2), nullable=False),
        sa.Column('subject_name', sa.String(length=100), nullable=False),
        sa.Column('order', sa.Integer(), nullable=True, server_default='99'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_curriculum_subjects_grade', 'curriculum_subjects', ['grade'], unique=False)
    op.create_index('ix_curriculum_subjects_subject_name', 'curriculum_subjects', ['subject_name'], unique=False)

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
    op.create_index('ix_curriculum_units_subject_id', 'curriculum_units', ['subject_id'], unique=False)

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
    op.create_index('ix_curriculum_topics_unit_id', 'curriculum_topics', ['unit_id'], unique=False)
