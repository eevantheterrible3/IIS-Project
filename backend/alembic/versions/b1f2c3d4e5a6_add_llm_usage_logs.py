"""add llm usage logs

Revision ID: b1f2c3d4e5a6
Revises: 6cafd74ca767
Create Date: 2026-06-28 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b1f2c3d4e5a6'
down_revision: Union[str, None] = '6cafd74ca767'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'llm_usage_logs',
        sa.Column('llm_usage_log_id', sa.String(length=36), nullable=False),
        sa.Column('document_id', sa.String(length=36), nullable=True),
        sa.Column('user_id', sa.String(length=36), nullable=True),
        sa.Column('document_type_id', sa.String(length=36), nullable=True),
        sa.Column('generation_type', sa.String(length=16), nullable=False),
        sa.Column('model', sa.String(length=128), nullable=True),
        sa.Column('prompt_tokens', sa.Integer(), nullable=False),
        sa.Column('completion_tokens', sa.Integer(), nullable=False),
        sa.Column('total_tokens', sa.Integer(), nullable=False),
        sa.Column('estimated_cost', sa.Numeric(precision=12, scale=6), nullable=True),
        sa.Column('latency_ms', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['document_id'], ['documents.document_id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['document_type_id'], ['document_types.document_type_id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('llm_usage_log_id'),
    )
    op.create_index(
        op.f('ix_llm_usage_logs_llm_usage_log_id'),
        'llm_usage_logs',
        ['llm_usage_log_id'],
        unique=False,
    )
    # Analytics queries all filter/group/order by created_at — index it.
    op.create_index(
        op.f('ix_llm_usage_logs_created_at'),
        'llm_usage_logs',
        ['created_at'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f('ix_llm_usage_logs_created_at'), table_name='llm_usage_logs')
    op.drop_index(op.f('ix_llm_usage_logs_llm_usage_log_id'), table_name='llm_usage_logs')
    op.drop_table('llm_usage_logs')
