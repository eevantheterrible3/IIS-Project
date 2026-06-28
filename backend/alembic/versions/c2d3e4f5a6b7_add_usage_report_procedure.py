"""add usage report tables and PL/pgSQL procedure

Revision ID: c2d3e4f5a6b7
Revises: b1f2c3d4e5a6
Create Date: 2026-06-28 12:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c2d3e4f5a6b7'
down_revision: Union[str, None] = 'b1f2c3d4e5a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


PROCEDURE_SQL = r"""
CREATE OR REPLACE PROCEDURE generate_usage_report(
    p_period_start timestamp,
    p_period_end   timestamp,
    INOUT p_report_id varchar DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_total_gen  integer;
    v_total_tok  bigint;
    v_total_cost numeric(14,6);
    rec          record;
BEGIN
    -- Caller may pass a report_id; otherwise generate one.
    IF p_report_id IS NULL THEN
        p_report_id := gen_random_uuid()::text;
    END IF;

    -- 1) Header totals for the whole period: aggregate WITHOUT group by => one row.
    SELECT count(*),
           COALESCE(sum(total_tokens), 0),
           COALESCE(sum(estimated_cost), 0)
      INTO v_total_gen, v_total_tok, v_total_cost
      FROM llm_usage_logs
     WHERE created_at >= p_period_start
       AND created_at <= p_period_end;

    INSERT INTO usage_reports(
        report_id, title, period_start, period_end,
        total_generations, total_tokens, total_cost
    )
    VALUES (
        p_report_id,
        'Izvestaj potrosnje LLM-a ' || p_period_start::date || ' - ' || p_period_end::date,
        p_period_start, p_period_end,
        v_total_gen, v_total_tok, v_total_cost
    );

    -- 2) One report line per document type: GROUP BY collapses the logs into
    --    one summarised row per distinct document type.
    FOR rec IN
        SELECT COALESCE(dt.name, 'Unknown')        AS label,
               count(*)                            AS gens,
               COALESCE(sum(l.total_tokens), 0)    AS tok,
               COALESCE(sum(l.estimated_cost), 0)  AS cost
          FROM llm_usage_logs l
          LEFT JOIN document_types dt
                 ON dt.document_type_id = l.document_type_id
         WHERE l.created_at >= p_period_start
           AND l.created_at <= p_period_end
         GROUP BY COALESCE(dt.name, 'Unknown')
         ORDER BY tok DESC
    LOOP
        INSERT INTO usage_report_items(
            usage_report_item_id, report_id, label,
            generations, total_tokens, estimated_cost
        )
        VALUES (
            gen_random_uuid()::text, p_report_id, rec.label,
            rec.gens, rec.tok, rec.cost
        );
    END LOOP;

    RAISE NOTICE 'Izvestaj % kreiran: % generisanja, % tokena, trosak %',
        p_report_id, v_total_gen, v_total_tok, v_total_cost;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Greska pri generisanju izvestaja: %', SQLERRM;
        RAISE;
END;
$$;
"""


def upgrade() -> None:
    op.create_table(
        'usage_reports',
        sa.Column('report_id', sa.String(length=36), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('period_start', sa.DateTime(), nullable=False),
        sa.Column('period_end', sa.DateTime(), nullable=False),
        sa.Column('generated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('total_generations', sa.Integer(), nullable=False),
        sa.Column('total_tokens', sa.BigInteger(), nullable=False),
        sa.Column('total_cost', sa.Numeric(precision=14, scale=6), nullable=True),
        sa.PrimaryKeyConstraint('report_id'),
    )
    op.create_index(op.f('ix_usage_reports_report_id'), 'usage_reports', ['report_id'], unique=False)

    op.create_table(
        'usage_report_items',
        sa.Column('usage_report_item_id', sa.String(length=36), nullable=False),
        sa.Column('report_id', sa.String(length=36), nullable=False),
        sa.Column('label', sa.String(length=255), nullable=False),
        sa.Column('generations', sa.Integer(), nullable=False),
        sa.Column('total_tokens', sa.BigInteger(), nullable=False),
        sa.Column('estimated_cost', sa.Numeric(precision=14, scale=6), nullable=True),
        sa.ForeignKeyConstraint(['report_id'], ['usage_reports.report_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('usage_report_item_id'),
    )
    op.create_index(op.f('ix_usage_report_items_usage_report_item_id'), 'usage_report_items', ['usage_report_item_id'], unique=False)
    op.create_index(op.f('ix_usage_report_items_report_id'), 'usage_report_items', ['report_id'], unique=False)

    op.execute(PROCEDURE_SQL)


def downgrade() -> None:
    op.execute("DROP PROCEDURE IF EXISTS generate_usage_report(timestamp, timestamp, varchar)")
    op.drop_index(op.f('ix_usage_report_items_report_id'), table_name='usage_report_items')
    op.drop_index(op.f('ix_usage_report_items_usage_report_item_id'), table_name='usage_report_items')
    op.drop_table('usage_report_items')
    op.drop_index(op.f('ix_usage_reports_report_id'), table_name='usage_reports')
    op.drop_table('usage_reports')
