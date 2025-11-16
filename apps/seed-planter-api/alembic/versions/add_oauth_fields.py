"""add oauth fields to users

Revision ID: add_oauth_fields
Revises: 
Create Date: 2025-11-16

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_oauth_fields'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add OAuth fields to users table
    op.add_column('users', sa.Column('oauth_provider', sa.String(), nullable=True))
    op.add_column('users', sa.Column('oauth_id', sa.String(), nullable=True))
    
    # Create index on oauth_id for faster lookups
    op.create_index(op.f('ix_users_oauth_id'), 'users', ['oauth_id'], unique=True)


def downgrade():
    # Remove index and columns
    op.drop_index(op.f('ix_users_oauth_id'), table_name='users')
    op.drop_column('users', 'oauth_id')
    op.drop_column('users', 'oauth_provider')
