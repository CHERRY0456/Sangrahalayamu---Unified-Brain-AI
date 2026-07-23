import sys
import os

# Add backend directory to Python path so we can import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.database.postgres import SessionLocal, engine
from sqlalchemy import text

def check_seeded_data():
    print(f"Connected to Database URL: {engine.url}")
    db = SessionLocal()
    try:
        print("\n--- ROLES ---")
        roles = db.execute(text("SELECT id, name, description FROM roles")).fetchall()
        if not roles:
            print("No roles found.")
        for role in roles:
            print(f"ID: {role[0]}, Name: {role[1]}, Desc: {role[2]}")

        print("\n--- USERS ---")
        users = db.execute(text("SELECT id, email, full_name, is_active FROM users")).fetchall()
        if not users:
            print("No users found.")
        for user in users:
            print(f"ID: {user[0]}, Email: {user[1]}, Name: {user[2]}, Active: {user[3]}")
            
    except Exception as e:
        print(f"Error querying database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_seeded_data()
