"""Add priority column to todos table

Revision ID: 003_add_priority
Revises: 002_create_todos
Create Date: 2026-01-08 00:00:00

This migration adds priority support to the Todo table:
- Adds priority VARCHAR(20) column with default 'normal'
- Creates index on priority column for efficient filtering
- Creates composite index on (priority, created_at DESC) for optimized sorting
- Supports two priority levels: "high" and "normal" (enforced at application layer)

Performance:
- idx_todo_priority: Fast filtering by priority (WHERE priority = 'high')
- idx_todo_priority_created: Fast sorting by priority + date (ORDER BY priority DESC, created_at DESC)
- Backwards compatible: Existing todos default to 'normal' priority

Security:
- Priority changes require user authentication (enforced at API layer)
- User can only set priority on their own todos (ownership verification at API layer)
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '003_add_priority'
down_revision = '002_create_todos'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Add priority column to todo table with indexes.

    Changes:
        - Adds priority VARCHAR(20) NOT NULL DEFAULT 'normal'
        - Creates idx_todo_priority index for filtering
        - Creates idx_todo_priority_created composite index for sorting

    Backwards Compatibility:
        - All existing todos will have priority = 'normal' (server_default)
        - No data loss or corruption
        - Non-breaking change for API responses (new optional field)
    """
    # Add priority column with default value
    op.add_column(
        'todo',
        sa.Column(
            'priority',
            sa.String(length=20),
            nullable=False,
            server_default='normal',
            comment='Priority level: "high" or "normal" (default: normal)'
        )
    )

    # Create index on priority column for efficient filtering
    # Supports queries like: WHERE priority = 'high'
    op.create_index(
        'idx_todo_priority',
        'todo',
        ['priority'],
        postgresql_using='btree'
    )

    # Create composite index for optimized priority + date sorting
    # Supports queries like: ORDER BY (priority = 'high') DESC, created_at DESC
    # This makes high priority todos appear first, then sorted by creation date
    op.create_index(
        'idx_todo_priority_created',
        'todo',
        ['priority', sa.text('created_at DESC')],
        postgresql_using='btree'
    )


def downgrade() -> None:
    """
    Remove priority column and indexes from todo table.

    Warning:
        This will permanently delete all priority data.
        Ensure you have a backup before running this migration in production.
    """
    # Drop indexes first
    op.drop_index('idx_todo_priority_created', table_name='todo')
    op.drop_index('idx_todo_priority', table_name='todo')

    # Drop priority column
    op.drop_column('todo', 'priority')
