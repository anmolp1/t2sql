"""fix use cases table

Revision ID: 002_fix_use_cases
Revises: 001_initial
Create Date: 2024-03-19 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002_fix_use_cases'
down_revision = '001_initial'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Drop the existing use_cases table
    op.drop_table('use_cases')
    
    # Recreate the use_cases table with correct column names
    op.create_table(
        'use_cases',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('example_query', sa.Text(), nullable=True),
        sa.Column('natural_language_example', sa.Text(), nullable=True),
        sa.Column('database_connection_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['database_connection_id'], ['database_connections.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_use_cases_id'), 'use_cases', ['id'], unique=False)
    op.create_index(op.f('ix_use_cases_name'), 'use_cases', ['name'], unique=False)

def downgrade() -> None:
    # Drop the fixed use_cases table
    op.drop_index(op.f('ix_use_cases_name'), table_name='use_cases')
    op.drop_index(op.f('ix_use_cases_id'), table_name='use_cases')
    op.drop_table('use_cases')
    
    # Recreate the original use_cases table
    op.create_table(
        'use_cases',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('example_query', sa.Text(), nullable=False),
        sa.Column('natural_language_example', sa.Text(), nullable=False),
        sa.Column('database_connection_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['database_connection_id'], ['database_connections.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_use_cases_id'), 'use_cases', ['id'], unique=False)
    op.create_index(op.f('ix_use_cases_title'), 'use_cases', ['title'], unique=False) 