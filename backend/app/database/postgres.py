from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.core.config import settings

DATABASE_URL = settings.database.url
# Try to initialize connection, falling back to local SQLite if Postgres fails (e.g. offline server or invalid password)
try:
    if DATABASE_URL.startswith("postgresql"):
        # Quick check connection with timeout
        test_engine = create_engine(DATABASE_URL)
        # Attempt raw connection to verify authentication
        with test_engine.connect() as conn:
            pass
        engine = create_engine(
            DATABASE_URL, 
            pool_pre_ping=True,
            pool_size=settings.database.pool_size,
            max_overflow=settings.database.max_overflow,
            pool_timeout=settings.database.pool_timeout,
            pool_recycle=settings.database.pool_recycle,
            echo=settings.database.echo
        )
    else:
        engine = create_engine(DATABASE_URL)
except Exception as e:
    print(f"PostgreSQL connection failed: {e}")
    print("Falling back to local SQLite database: 'sangrahalayamu.db'")
    DATABASE_URL = "sqlite:///sangrahalayamu.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# SQLAlchemy 2.0 DeclarativeBase
class Base(DeclarativeBase):
    pass

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
