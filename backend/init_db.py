import os
import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent))

from app.db.session import engine
from app.models.base import Base
from alembic.config import Config
from alembic import command

def init_db():
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Run migrations
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!") 