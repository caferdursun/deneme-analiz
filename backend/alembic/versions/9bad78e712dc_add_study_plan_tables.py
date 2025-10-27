"""add_study_plan_tables

Revision ID: 9bad78e712dc
Revises: d6cf8a805c38
Create Date: 2025-10-27 05:58:19.136206

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9bad78e712dc'
down_revision: Union[str, None] = 'd6cf8a805c38'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create study_plans table
    op.create_table(
        'study_plans',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('student_id', sa.String(36), sa.ForeignKey('students.id'), nullable=False, index=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('time_frame', sa.Integer(), nullable=False),
        sa.Column('daily_study_time', sa.Integer(), nullable=False),
        sa.Column('study_style', sa.String(20), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='active', index=True),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )

    # Create study_plan_days table
    op.create_table(
        'study_plan_days',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('plan_id', sa.String(36), sa.ForeignKey('study_plans.id'), nullable=False, index=True),
        sa.Column('day_number', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('total_duration_minutes', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('completed', sa.Boolean(), nullable=False, server_default='0', index=True),
        sa.Column('notes', sa.Text()),
    )

    # Create study_plan_items table
    op.create_table(
        'study_plan_items',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('day_id', sa.String(36), sa.ForeignKey('study_plan_days.id'), nullable=False, index=True),
        sa.Column('recommendation_id', sa.String(36), sa.ForeignKey('recommendations.id'), nullable=True),
        sa.Column('subject_name', sa.String(50), nullable=False),
        sa.Column('topic', sa.String(255), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('duration_minutes', sa.Integer(), nullable=False),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('completed', sa.Boolean(), nullable=False, server_default='0', index=True),
        sa.Column('completed_at', sa.DateTime()),
    )


def downgrade() -> None:
    # Drop tables in reverse order (respecting foreign keys)
    op.drop_table('study_plan_items')
    op.drop_table('study_plan_days')
    op.drop_table('study_plans')
