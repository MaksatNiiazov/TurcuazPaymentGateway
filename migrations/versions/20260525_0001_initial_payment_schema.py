"""initial payment schema

Revision ID: 20260525_0001
Revises:
Create Date: 2026-05-25
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260525_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "transactions",
        sa.Column("id", sa.String(length=128), primary_key=True),
        sa.Column("provider", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=64)),
        sa.Column("transaction_type", sa.String(length=64)),
        sa.Column("amount", sa.Integer),
        sa.Column("branch", sa.String(length=128)),
        sa.Column("cashier", sa.String(length=128)),
        sa.Column("created_at", sa.String(length=64)),
        sa.Column("paid_at", sa.String(length=64)),
        sa.Column("payment_token", sa.Text),
        sa.Column("static_qr_link", sa.Text),
        sa.Column("metadata", sa.Text),
        sa.Column("raw_payload", sa.Text, nullable=False),
        sa.Column("updated_at", sa.String(length=64), nullable=False),
    )
    op.create_index(
        "idx_transactions_provider_status",
        "transactions",
        ["provider", "status"],
    )
    op.create_index("idx_transactions_updated_at", "transactions", ["updated_at"])

    op.create_table(
        "webhook_events",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("provider", sa.String(length=32), nullable=False),
        sa.Column("transaction_id", sa.String(length=128), nullable=False),
        sa.Column("status", sa.String(length=64)),
        sa.Column("payload_hash", sa.String(length=64), nullable=False),
        sa.Column("payload", sa.Text, nullable=False),
        sa.Column("received_at", sa.String(length=64), nullable=False),
        sa.UniqueConstraint(
            "provider",
            "payload_hash",
            name="uq_webhook_events_provider_payload_hash",
        ),
    )
    op.create_index(
        "idx_webhook_events_transaction_id",
        "webhook_events",
        ["transaction_id"],
    )
    op.create_index("idx_webhook_events_received_at", "webhook_events", ["received_at"])

    op.create_table(
        "api_access_events",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("integration_name", sa.String(length=128), nullable=False),
        sa.Column("method", sa.String(length=16), nullable=False),
        sa.Column("path", sa.Text, nullable=False),
        sa.Column("status_code", sa.Integer),
        sa.Column("user_agent", sa.Text),
        sa.Column("remote_addr", sa.String(length=128)),
        sa.Column("created_at", sa.String(length=64), nullable=False),
    )
    op.create_index(
        "idx_api_access_events_integration_name",
        "api_access_events",
        ["integration_name"],
    )
    op.create_index("idx_api_access_events_created_at", "api_access_events", ["created_at"])


def downgrade() -> None:
    op.drop_index("idx_api_access_events_created_at", table_name="api_access_events")
    op.drop_index("idx_api_access_events_integration_name", table_name="api_access_events")
    op.drop_table("api_access_events")

    op.drop_index("idx_webhook_events_received_at", table_name="webhook_events")
    op.drop_index("idx_webhook_events_transaction_id", table_name="webhook_events")
    op.drop_table("webhook_events")

    op.drop_index("idx_transactions_updated_at", table_name="transactions")
    op.drop_index("idx_transactions_provider_status", table_name="transactions")
    op.drop_table("transactions")
