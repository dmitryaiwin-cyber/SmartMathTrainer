"""Add operation_mode column

Revision ID: 004
Revises: 003
Create Date: 2026-09-16

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('training_sessions')]
    
    if 'operation_mode' not in columns:
        op.add_column('training_sessions', sa.Column('operation_mode', sa.String(), nullable=False, server_default='multiply'))


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('training_sessions')]
    
    if 'operation_mode' in columns:
        op.drop_column('training_sessions', 'operation_mode')
