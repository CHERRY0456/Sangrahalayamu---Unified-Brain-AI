import sys
import os
from sqlalchemy.orm import Session

# Add backend app directory to pythonpath
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database.postgres import SessionLocal, Base, engine
from app.models.role import Role
from app.models.user import User
from app.core.security import hash_password

ROLES_DATA = [
    {
        "name": "Field Technician",
        "permissions": ["chat", "history", "transparency"]
    },
    {
        "name": "Maintenance Engineer",
        "permissions": ["chat", "upload", "processing", "history", "transparency"]
    },
    {
        "name": "Project Manager",
        "permissions": ["chat", "history", "transparency"]
    },
    {
        "name": "Regulatory & Compliance Manager",
        "permissions": ["history", "transparency", "audit"]
    },
    {
        "name": "Director / Executive",
        "permissions": ["chat", "upload", "processing", "history", "transparency", "audit"]
    },
    {
        "name": "CEO",
        "permissions": ["chat", "upload", "processing", "history", "transparency", "audit"]
    }
]

USERS_DATA = [
    {
        "employee_id": "EMP-2041",
        "name": "Ravi Kumar",
        "email": "ravi.kumar@company.com",
        "department": "Operations",
        "designation": "Lead Field Technician",
        "role_name": "Field Technician"
    },
    {
        "employee_id": "EMP-1024",
        "name": "Priya Sharma",
        "email": "priya.sharma@company.com",
        "department": "Maintenance",
        "designation": "Senior Maintenance Engineer",
        "role_name": "Maintenance Engineer"
    },
    {
        "employee_id": "EMP-3092",
        "name": "Arjun Mehta",
        "email": "arjun.mehta@company.com",
        "department": "Projects",
        "designation": "Technical Project Manager",
        "role_name": "Project Manager"
    },
    {
        "employee_id": "EMP-4401",
        "name": "Neha Iyer",
        "email": "neha.iyer@company.com",
        "department": "Quality Assurance & Compliance",
        "designation": "Corporate Compliance Manager",
        "role_name": "Regulatory & Compliance Manager"
    },
    {
        "employee_id": "EMP-0010",
        "name": "Vikram Rao",
        "email": "vikram.rao@company.com",
        "department": "Executive Board",
        "designation": "Director of Plant Operations",
        "role_name": "Director / Executive"
    },
    {
        "employee_id": "EMP-1001",
        "name": "Cherry",
        "email": "cherry@company.com",
        "department": "Executive Operations",
        "designation": "Chief Executive Officer",
        "role_name": "CEO"
    },
    {
        "employee_id": "EMP-1002",
        "name": "Cherry Jai",
        "email": "cherry.jai@company.com",
        "department": "Executive Operations",
        "designation": "Chief Executive Officer",
        "role_name": "CEO"
    }
]

def seed_database():
    print("Creating all tables in Postgres database...")
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    try:
        print("Seeding roles...")
        role_map = {}
        for r_item in ROLES_DATA:
            role = db.query(Role).filter(Role.name == r_item["name"]).first()
            if not role:
                role = Role(name=r_item["name"], permissions=r_item["permissions"])
                db.add(role)
                db.flush()
                print(f"Created role: {role.name}")
            else:
                # Sync permissions list
                role.permissions = r_item["permissions"]
                print(f"Role already exists: {role.name} (permissions synced)")
            role_map[role.name] = role.id

        print("\nSeeding user profiles...")
        default_pwd_hash = hash_password("password123")
        
        for u_item in USERS_DATA:
            user = db.query(User).filter(User.email == u_item["email"]).first()
            role_id = role_map[u_item["role_name"]]
            
            if not user:
                user = User(
                    employee_id=u_item["employee_id"],
                    name=u_item["name"],
                    email=u_item["email"],
                    hashed_password=default_pwd_hash,
                    department=u_item["department"],
                    designation=u_item["designation"],
                    role_id=role_id,
                    is_active=True
                )
                db.add(user)
                print(f"Created user profile: {user.name} ({user.email})")
            else:
                user.role_id = role_id
                user.employee_id = u_item["employee_id"]
                user.department = u_item["department"]
                user.designation = u_item["designation"]
                print(f"User profile exists: {user.name} ({user.email}) (fields synced)")

        db.commit()
        print("\nDatabase seeded successfully!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
