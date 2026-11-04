from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

connect_args = {}
engine_kwargs = {
    "pool_pre_ping": True,  # verify connections before use
}

db_url = settings.clean_database_url

if db_url.startswith("sqlite"):
    # SQLite: local development only
    connect_args = {"check_same_thread": False}
    engine_kwargs["connect_args"] = connect_args
else:
    # PostgreSQL: serverless-safe connection pool settings
    # NullPool prevents connections hanging across serverless invocations
    from sqlalchemy.pool import NullPool
    engine_kwargs["poolclass"] = NullPool

engine = create_engine(db_url, **engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
