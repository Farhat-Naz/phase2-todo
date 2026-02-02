"""Create users table

Revision ID: 001_create_users
Revises: None
Create Date: 2026-01-08 00:00:00

This migration creates the initial User table with:
- UUID primary key (auto-generated via gen_random_uuid())
- Email field (unique, indexed)
- Hashed password field
- Optional name field
- Created_at and updated_at timestamps

Security:
- Email is unique and indexed for fast login queries
- Passwords are stored as bcrypt hashes (never plain text)
- UUID primary keys for security and distributed systems
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = '001_create_users'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Create the user table with all constraints and indexes.

    Table: user
    Columns:
        - id: UUID primary key (auto-generated)
        - email: VARCHAR(255), unique, not null, indexed
        - hashed_password: VARCHAR(255), not null
        - name: VARCHAR(255), nullable
        - created_at: TIMESTAMP WITH TIME ZONE, not null, default NOW(), indexed
        - updated_at: TIMESTAMP WITH TIME ZONE, not null, default NOW()

    Indexes:
        - idx_user_email: On email column (unique, for fast login queries)
        - idx_user_created_at: On created_at column (for sorting/filtering)
    """
    # Create user table
    op.create_table(
        'user',
        # Primary key (UUID, auto-generated)
        sa.Column(
            'id',
            UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text('gen_random_uuid()'),
            nullable=False,
            comment='Unique user identifier'
        ),

        # Authentication fields
        sa.Column(
            'email',
            sa.String(length=255),
            nullable=False,
            unique=True,
            comment='Login email address (unique, indexed)'
        ),
        sa.Column(
            'hashed_password',
            sa.String(length=255),
            nullable=False,
            comment='Bcrypt-hashed password (never plain text)'
        ),

        # Profile fields
        sa.Column(
            'name',
            sa.String(length=255),
            nullable=True,
            comment="User's display name"
        ),

        # Timestamps
        sa.Column(
            'created_at',
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text('NOW()'),
            comment='Account creation timestamp'
        ),
        sa.Column(
            'updated_at',
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text('NOW()'),
            comment='Last update timestamp'
        ),

        # Table comment
        comment='User accounts with authentication and profile information'
    )

    # Create indexes
    # Email index (unique) - already created via unique=True constraint
    op.create_index(
        'idx_user_email',
        'user',
        ['email'],
        unique=True,
        postgresql_ops={'email': 'text_pattern_ops'}  # Optimize for LIKE queries
    )

    # Created_at index for sorting and filtering
    op.create_index(
        'idx_user_created_at',
        'user',
        ['created_at'],
        postgresql_using='btree'
    )


def downgrade() -> None:
    """
    Drop the user table and all associated indexes.

    Warning:
        This will permanently delete all user data.
        Ensure you have a backup before running this migration in production.
    """
    # Drop indexes first (optional, CASCADE will handle it)
    op.drop_index('idx_user_created_at', table_name='user')
    op.drop_index('idx_user_email', table_name='user')

    # Drop table (CASCADE will drop dependent objects)
    op.drop_table('user')
