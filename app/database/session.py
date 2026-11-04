import ssl
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from app.core.config import settings

def create_app_engine():
    db_url = settings.clean_database_url

    if db_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
        return create_engine(db_url, connect_args=connect_args, pool_pre_ping=True)

    parsed = urlparse(db_url)

    # 1. Try psycopg2 driver if available and functional
    try:
        import psycopg2
        query_psycopg = parse_qs(parsed.query)
        query_psycopg.pop("channel_binding", None)
        if "sslmode" not in query_psycopg:
            query_psycopg["sslmode"] = ["require"]
        clean_psycopg_url = urlunparse((
            "postgresql",
            parsed.netloc,
            parsed.path,
            parsed.params,
            urlencode(query_psycopg, doseq=True),
            parsed.fragment
        ))
        test_engine = create_engine(clean_psycopg_url, poolclass=NullPool, pool_pre_ping=True)
        with test_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("[DB Engine] Connected via psycopg2 driver")
        return test_engine
    except Exception as e:
        print(f"[DB Notice] psycopg2 not available ({e}). Using pure-Python pg8000 driver.")

    # 2. Pure-Python pg8000 driver (guaranteed to work in serverless without C dependencies)
    # Note: pg8000 takes ssl_context in connect_args, NOT sslmode in URL query params
    query_pg8000 = parse_qs(parsed.query)
    query_pg8000.pop("sslmode", None)
    query_pg8000.pop("channel_binding", None)

    clean_pg8000_url = urlunparse((
        "postgresql+pg8000",
        parsed.netloc,
        parsed.path,
        parsed.params,
        urlencode(query_pg8000, doseq=True),
        parsed.fragment
    ))

    ssl_context = ssl.create_default_context()
    return create_engine(
        clean_pg8000_url,
        connect_args={"ssl_context": ssl_context},
        poolclass=NullPool,
        pool_pre_ping=True
    )

engine = create_app_engine()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
