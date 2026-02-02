"""Add auth enhancement tables and fields

Revision ID: 20260113_0004
Revises: 20260108_0003
Create Date: 2026-01-13

This migration adds:
- email_verified and last_login fields to users table
- sessions table for refresh token management
- password_reset_tokens table for password reset flow
- email_verification_tokens table for email verification flow
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20260113_0004'
down_revision: Union[str, None] = '003_add_priority'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Upgrade database schema to add auth enhancement tables and fields.

    Changes:
    1. Add email_verified and last_login to user table
    2. Create session table for refresh token management
    3. Create password_reset_token table for password reset flow
    4. Create email_verification_token table for email verification flow
    """

    # 1. Add email_verified and last_login fields to user table
    op.add_column('user', sa.Column('email_verified', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('user', sa.Column('last_login', sa.DateTime(), nullable=True))
    op.create_index('ix_user_last_login', 'user', ['last_login'], unique=False)

    # 2. Create session table
    op.create_table('session',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('refresh_token_hash', sa.String(length=255), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('last_activity', sa.DateTime(), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=False),
        sa.Column('user_agent', sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_session_user_id', 'session', ['user_id'], unique=False)
    op.create_index('ix_session_expires_at', 'session', ['expires_at'], unique=False)

    # 3. Create password_reset_token table
    op.create_table('password_reset_token',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('token_hash', sa.String(length=255), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('used', sa.Boolean(), nullable=False, server_default='false'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_password_reset_token_user_id', 'password_reset_token', ['user_id'], unique=False)
    op.create_index('ix_password_reset_token_expires_at', 'password_reset_token', ['expires_at'], unique=False)

    # 4. Create email_verification_token table
    op.create_table('email_verification_token',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('token_hash', sa.String(length=255), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_email_verification_token_user_id', 'email_verification_token', ['user_id'], unique=False)
    op.create_index('ix_email_verification_token_expires_at', 'email_verification_token', ['expires_at'], unique=False)


def downgrade() -> None:
    """
    Downgrade database schema to remove auth enhancement tables and fields.

    Reverses all changes made in upgrade().
    """

    # Drop tables in reverse order
    op.drop_index('ix_email_verification_token_expires_at', table_name='email_verification_token')
    op.drop_index('ix_email_verification_token_user_id', table_name='email_verification_token')
    op.drop_table('email_verification_token')

    op.drop_index('ix_password_reset_token_expires_at', table_name='password_reset_token')
    op.drop_index('ix_password_reset_token_user_id', table_name='password_reset_token')
    op.drop_table('password_reset_token')

    op.drop_index('ix_session_expires_at', table_name='session')
    op.drop_index('ix_session_user_id', table_name='session')
    op.drop_table('session')

    # Remove columns from user table
    op.drop_index('ix_user_last_login', table_name='user')
    op.drop_column('user', 'last_login')
    op.drop_column('user', 'email_verified')
