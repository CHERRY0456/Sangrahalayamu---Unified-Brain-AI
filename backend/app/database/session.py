from typing import Generator
from sqlalchemy.orm import Session
from .postgres import SessionLocal

def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency. Yields active transactions and ensures closed state post-execution.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
