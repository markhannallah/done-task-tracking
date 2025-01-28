"""add archive fields

Revision ID: add_archive_fields
Revises: 
Create Date: 2025-01-28 13:22:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_archive_fields'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Add archive fields to task table
    op.add_column('task', sa.Column('archived', sa.Boolean(), nullable=False, server_default='0'))
    op.add_column('task', sa.Column('archived_at', sa.DateTime(), nullable=True))

def downgrade():
    # Remove archive fields from task table
    op.drop_column('task', 'archived_at')
    op.drop_column('task', 'archived')
