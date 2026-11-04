from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from app.core.config import settings

def create_app_engine():
    db_url = settings.clean_database_url
    connect_args = {}
    engine_kwargs = {
        "pool_pre_ping": True,
    }

    if db_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
        engine_kwargs["connect_args"] = connect_args
        return create_engine(db_url, **engine_kwargs)
    else:
        # PostgreSQL on Serverless: use NullPool to avoid connection pooling issues
        engine_kwargs["poolclass"] = NullPool
        try:
            # First try standard driver (psycopg2-binary)
            return create_engine(db_url, **engine_kwargs)
        except Exception as e:
            print(f"[DB Warning] Standard Postgres driver notice: {e}. Trying pg8000 fallback.")
            if "postgresql://" in db_url:
                pg8000_url = db_url.replace("postgresql://", "postgresql+pg8000://", 1)
                return create_engine(pg8000_url, **engine_kwargs)
            raise

engine = create_app_engine()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
