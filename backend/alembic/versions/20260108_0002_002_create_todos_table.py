"""Create todos table

Revision ID: 002_create_todos
Revises: 001_create_users
Create Date: 2026-01-08 00:00:00

This migration creates the Todo table with:
- UUID primary key (auto-generated via gen_random_uuid())
- Foreign key to User table with CASCADE delete
- Title field (VARCHAR 500, required)
- Description field (TEXT, optional)
- Completed status (BOOLEAN, default false)
- Created_at and updated_at timestamps
- Performance indexes on user_id, completed, and created_at

Security:
- user_id indexed for fast user-scoped queries (CRITICAL for multi-tenant isolation)
- Foreign key constraint ensures data integrity
- ON DELETE CASCADE: when user is deleted, all their todos are automatically deleted

Performance:
- idx_todo_user_id: Fast filtering by user (most common query)
- idx_todo_completed: Fast filtering by completion status
- idx_todo_created_at: Fast sorting by creation date (default sort order)
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = '002_create_todos'
down_revision = '001_create_users'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Create the todo table with all constraints and indexes.

    Table: todo
    Columns:
        - id: UUID primary key (auto-generated)
        - user_id: UUID foreign key to user(id), not null, indexed, CASCADE on delete
        - title: VARCHAR(500), not null, indexed for search
        - description: TEXT, nullable
        - completed: BOOLEAN, not null, default false, indexed
        - created_at: TIMESTAMP WITH TIME ZONE, not null, default NOW(), indexed
        - updated_at: TIMESTAMP WITH TIME ZONE, not null, default NOW()

    Indexes:
        - idx_todo_user_id: On user_id column (for user-scoped queries)
        - idx_todo_completed: On completed column (for filtering by status)
        - idx_todo_created_at: On created_at column (for sorting by date, DESC)
        - idx_todo_title: On title column (for search queries)

    Foreign Keys:
        - user_id REFERENCES user(id) ON DELETE CASCADE
    """
    # Create todo table
    op.create_table(
        'todo',
        # Primary key (UUID, auto-generated)
        sa.Column(
            'id',
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text('gen_random_uuid()'),
            nullable=False,
            comment='Unique todo identifier'
        ),

        # Foreign key to User
        sa.Column(
            'user_id',
            UUID(as_uuid=True),
            sa.ForeignKey('user.id', ondelete='CASCADE'),
            nullable=False,
            comment='Owner of the todo (foreign key to users.id, CASCADE on delete)'
        ),

        # Todo fields
        sa.Column(
            'title',
            sa.String(length=500),
            nullable=False,
            comment='Todo title/summary (1-500 characters)'
        ),
        sa.Column(
            'description',
            sa.Text(),
            nullable=True,
            comment='Optional detailed description'
        ),
        sa.Column(
            'completed',
            sa.Boolean(),
            nullable=False,
            server_default='false',
            comment='Completion status (default: false)'
        ),

        # Timestamps
        sa.Column(
            'created_at',
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text('NOW()'),
            comment='Creation timestamp'
        ),
        sa.Column(
            'updated_at',
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text('NOW()'),
            comment='Last update timestamp'
        ),

        # Table comment
        comment='Todo items owned by users (user-scoped with CASCADE delete)'
    )

    # Create indexes for performance
    # 1. user_id index (CRITICAL: most common query pattern)
    op.create_index(
        'idx_todo_user_id',
        'todo',
        ['user_id'],
        postgresql_using='btree',
        postgresql_ops={'user_id': 'uuid_ops'}
    )

    # 2. completed index (for filtering by status)
    op.create_index(
        'idx_todo_completed',
        'todo',
        ['completed'],
        postgresql_using='btree'
    )

    # 3. created_at index (for sorting by creation date, DESC order)
    op.create_index(
        'idx_todo_created_at',
        'todo',
        [sa.text('created_at DESC')],
        postgresql_using='btree'
    )

    # 4. title index (for search queries)
    op.create_index(
        'idx_todo_title',
        'todo',
        ['title'],
        postgresql_using='btree',
        postgresql_ops={'title': 'text_pattern_ops'}  # Optimize for LIKE queries
    )

    # 5. Composite index for common query pattern: user's active/completed todos
    # This covers queries like: WHERE user_id = X AND completed = Y ORDER BY created_at DESC
    op.create_index(
        'idx_todo_user_completed_created',
        'todo',
        ['user_id', 'completed', sa.text('created_at DESC')],
        postgresql_using='btree'
    )


def downgrade() -> None:
    """
    Drop the todo table and all associated indexes.

    Warning:
        This will permanently delete all todo data.
        Ensure you have a backup before running this migration in production.
    """
    # Drop indexes first (optional, CASCADE will handle it)
    op.drop_index('idx_todo_user_completed_created', table_name='todo')
    op.drop_index('idx_todo_title', table_name='todo')
    op.drop_index('idx_todo_created_at', table_name='todo')
    op.drop_index('idx_todo_completed', table_name='todo')
    op.drop_index('idx_todo_user_id', table_name='todo')

    # Drop table (CASCADE will drop dependent objects)
    op.drop_table('todo')
