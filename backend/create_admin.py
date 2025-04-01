import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent))

from app.db.session import SessionLocal
from app.services.user import create_user
from app.schemas.user import UserCreate

def create_admin_user():
    db = SessionLocal()
    try:
        admin_user = UserCreate(
            email="admin@example.com",
            password="admin123",
            full_name="Admin User",
            is_superuser=True
        )
        user = create_user(db=db, user=admin_user)
        print(f"Created admin user with ID: {user.id}")
    except Exception as e:
        print(f"Error creating admin user: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user() 