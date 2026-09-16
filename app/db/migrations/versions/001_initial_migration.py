"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2024-09-16

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_id', 'users', ['id'])
    op.create_index('ix_users_session_id', 'users', ['session_id'], unique=True)
    
    # Create achievements table
    op.create_table(
        'achievements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_achievements_code', 'achievements', ['code'], unique=True)
    
    # Create training_sessions table
    op.create_table(
        'training_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('mode', sa.String(), nullable=False),
        sa.Column('tables', sa.String(), nullable=True),
        sa.Column('question_count', sa.Integer(), nullable=True, server_default='10'),
        sa.Column('time_limit', sa.Integer(), nullable=True),
        sa.Column('started_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('finished_at', sa.DateTime(), nullable=True),
        sa.Column('correct_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('wrong_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('score', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('max_streak', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('current_question', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_training_sessions_id', 'training_sessions', ['id'])
    op.create_index('ix_training_sessions_user_id', 'training_sessions', ['user_id'])
    
    # Create questions table
    op.create_table(
        'questions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('left_operand', sa.Integer(), nullable=False),
        sa.Column('right_operand', sa.Integer(), nullable=False),
        sa.Column('answer', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_questions_id', 'questions', ['id'])
    
    # Create question_results table
    op.create_table(
        'question_results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('question_id', sa.Integer(), nullable=False),
        sa.Column('user_answer', sa.Integer(), nullable=False),
        sa.Column('is_correct', sa.Integer(), nullable=False),
        sa.Column('response_time', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_question_results_id', 'question_results', ['id'])
    op.create_index('ix_question_results_session_id', 'question_results', ['session_id'])
    
    # Create question_stats table
    op.create_table(
        'question_stats',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('question_key', sa.String(), nullable=False),
        sa.Column('attempts', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('correct_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('wrong_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('average_response_time', sa.Float(), nullable=True),
        sa.Column('last_answered_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_question_stats_id', 'question_stats', ['id'])
    op.create_index('ix_question_stats_user_id', 'question_stats', ['user_id'])
    op.create_index('ix_question_stats_question_key', 'question_stats', ['question_key'])
    
    # Create user_achievements table
    op.create_table(
        'user_achievements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('achievement_id', sa.Integer(), nullable=False),
        sa.Column('earned_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_user_achievements_id', 'user_achievements', ['id'])
    op.create_index('ix_user_achievements_user_id', 'user_achievements', ['user_id'])


def downgrade() -> None:
    op.drop_index('ix_user_achievements_user_id', table_name='user_achievements')
    op.drop_index('ix_user_achievements_id', table_name='user_achievements')
    op.drop_table('user_achievements')
    
    op.drop_index('ix_question_stats_question_key', table_name='question_stats')
    op.drop_index('ix_question_stats_user_id', table_name='question_stats')
    op.drop_index('ix_question_stats_id', table_name='question_stats')
    op.drop_table('question_stats')
    
    op.drop_index('ix_question_results_session_id', table_name='question_results')
    op.drop_index('ix_question_results_id', table_name='question_results')
    op.drop_table('question_results')
    
    op.drop_index('ix_questions_id', table_name='questions')
    op.drop_table('questions')
    
    op.drop_index('ix_training_sessions_user_id', table_name='training_sessions')
    op.drop_index('ix_training_sessions_id', table_name='training_sessions')
    op.drop_table('training_sessions')
    
    op.drop_index('ix_achievements_code', table_name='achievements')
    op.drop_table('achievements')
    
    op.drop_index('ix_users_session_id', table_name='users')
    op.drop_index('ix_users_id', table_name='users')
    op.drop_table('users')
