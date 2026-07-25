"""
Admin User Creation Script for IndustryBrain-AI
"""
import sys
import logging
from sqlalchemy.orm import Session
from app.database.postgres import SessionLocal
from app.models.user import User
from app.models.role import Role
from app.services.auth.password import get_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_admin_user(email: str = "admin@industrybrain.ai", password: str = "Admin@123456"):
    db: Session = SessionLocal()
    try:
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            logger.info(f"User {email} already exists.")
            return

        admin_role = db.query(Role).filter(Role.name == "Admin").first()
        if not admin_role:
            admin_role = Role(name="Admin", description="System Administrator")
            db.add(admin_role)
            db.commit()
            db.refresh(admin_role)

        admin = User(
            email=email,
            password_hash=get_password_hash(password),
            full_name="System Administrator",
            role_id=admin_role.id,
            is_active=True
        )
        db.add(admin)
        db.commit()
        logger.info(f"Successfully created admin user: {email}")
    except Exception as e:
        logger.error(f"Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    email = sys.argv[1] if len(sys.argv) > 1 else "admin@industrybrain.ai"
    password = sys.argv[2] if len(sys.argv) > 2 else "Admin@123456"
    create_admin_user(email, password)
