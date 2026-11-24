import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.engine import URL, make_url
from sqlalchemy.exc import ArgumentError

from app.core.config import settings

logger = logging.getLogger(__name__)

Base = declarative_base()


def create_app_engine():
    """
    Connects to the database with graceful fallback:
    1. Remote DATABASE_URL if configured and reachable.
    2. Local MySQL on localhost:3306 if available.
    3. File-based SQLite as an automatic cloud demo fallback so Render never fails with 500 errors.
    """
    # 1. Try provided DATABASE_URL
    raw_url = settings.DATABASE_URL
    if raw_url and isinstance(raw_url, str):
        cleaned = raw_url.strip().strip("'\"")
        if "://" in cleaned:
            if cleaned.startswith("mysql://"):
                cleaned = "mysql+pymysql://" + cleaned[len("mysql://"):]
            elif cleaned.startswith("postgres://"):
                cleaned = "postgresql+psycopg2://" + cleaned[len("postgres://"):]
            
            try:
                parsed = make_url(cleaned)
                eng = create_engine(parsed, pool_pre_ping=True)
                with eng.connect():
                    pass
                logger.info("Connected to remote DATABASE_URL successfully.")
                return eng
            except Exception as err:
                logger.warning(f"Could not connect to remote DATABASE_URL: {err}. Attempting fallback.")

    # 2. Try Local MySQL (for development on local machine)
    try:
        local_url = URL.create(
            drivername="mysql+pymysql",
            username=settings.DATABASE_USER or "root",
            password=settings.DATABASE_PASSWORD or "",
            host=settings.DATABASE_HOST or "localhost",
            port=settings.DATABASE_PORT or 3306,
            database=settings.DATABASE_NAME or "stockflow_db",
        )
        eng = create_engine(local_url, pool_pre_ping=True)
        with eng.connect():
            pass
        logger.info("Connected to local MySQL successfully.")
        return eng
    except Exception as err:
        logger.warning(f"Local MySQL unavailable ({err}). Falling back to SQLite for seamless deployment.")

    # 3. Safe fallback to local SQLite (for Render/Cloud demo when no external DB is configured)
    sqlite_url = "sqlite:///./stockflow.db"
    return create_engine(sqlite_url, connect_args={"check_same_thread": False})


engine = create_app_engine()

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
