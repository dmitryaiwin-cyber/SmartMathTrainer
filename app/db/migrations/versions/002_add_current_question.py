"""Add current_question column

Revision ID: 002
Revises: 001
Create Date: 2024-09-16

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Check if column already exists
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('training_sessions')]
    
    if 'current_question' not in columns:
        op.add_column('training_sessions', sa.Column('current_question', sa.String(), nullable=True))


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('training_sessions')]
    
    if 'current_question' in columns:
        op.drop_column('training_sessions', 'current_question')
