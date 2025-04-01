"""initial

Revision ID: 001_initial
Revises: 
Create Date: 2024-03-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_superuser', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # Create database_connections table
    op.create_table(
        'database_connections',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('connection_type', sa.String(), nullable=False),
        sa.Column('host', sa.String(), nullable=True),
        sa.Column('port', sa.String(), nullable=True),
        sa.Column('database_name', sa.String(), nullable=True),
        sa.Column('username', sa.String(), nullable=True),
        sa.Column('project_id', sa.String(), nullable=True),
        sa.Column('credentials_json', sa.JSON(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('db_metadata', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_database_connections_id'), 'database_connections', ['id'], unique=False)
    op.create_index(op.f('ix_database_connections_name'), 'database_connections', ['name'], unique=False)

    # Create database_metadata table
    op.create_table(
        'database_metadata',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('database_connection_id', sa.Integer(), nullable=False),
        sa.Column('datasets', sa.JSON(), nullable=True),
        sa.Column('tables', sa.JSON(), nullable=True),
        sa.Column('relationships', sa.JSON(), nullable=True),
        sa.Column('constraints', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['database_connection_id'], ['database_connections.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_database_metadata_id'), 'database_metadata', ['id'], unique=False)

    # Create use_cases table
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

def downgrade() -> None:
    op.drop_index(op.f('ix_use_cases_title'), table_name='use_cases')
    op.drop_index(op.f('ix_use_cases_id'), table_name='use_cases')
    op.drop_table('use_cases')
    
    op.drop_index(op.f('ix_database_metadata_id'), table_name='database_metadata')
    op.drop_table('database_metadata')
    
    op.drop_index(op.f('ix_database_connections_name'), table_name='database_connections')
    op.drop_index(op.f('ix_database_connections_id'), table_name='database_connections')
    op.drop_table('database_connections')
    
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users') 