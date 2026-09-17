"""Add suggestions table

Revision ID: 003
Revises: 002
Create Date: 2026-09-16

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    if 'suggestions' not in inspector.get_table_names():
        op.create_table(
            'suggestions',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=True),
            sa.Column('text', sa.Text(), nullable=False),
            sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('ix_suggestions_id', 'suggestions', ['id'])
        op.create_index('ix_suggestions_user_id', 'suggestions', ['user_id'])


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    if 'suggestions' in inspector.get_table_names():
        op.drop_index('ix_suggestions_user_id', 'suggestions')
        op.drop_index('ix_suggestions_id', 'suggestions')
        op.drop_table('suggestions')
