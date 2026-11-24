import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.engine import URL, make_url
from sqlalchemy.exc import ArgumentError

from app.core.config import settings

logger = logging.getLogger(__name__)


def build_database_url():
    """
    Safely resolves and sanitizes the database URL for local and production cloud deployments.
    Supports direct cloud MySQL URIs (auto-converts mysql:// to mysql+pymysql://).
    """
    raw_url = settings.DATABASE_URL

    if raw_url and isinstance(raw_url, str):
        cleaned = raw_url.strip().strip("'\"")
        # Ensure it has a valid protocol
        if "://" in cleaned:
            if cleaned.startswith("mysql://"):
                cleaned = "mysql+pymysql://" + cleaned[len("mysql://"):]
            elif cleaned.startswith("postgres://"):
                cleaned = "postgresql+psycopg2://" + cleaned[len("postgres://"):]
            
            try:
                # Validate that SQLAlchemy can parse this URL
                return make_url(cleaned)
            except (ArgumentError, ValueError) as err:
                logger.warning(f"Could not parse DATABASE_URL ({err}). Falling back to discrete parameters.")

    # Fallback to discrete parameters
    return URL.create(
        drivername="mysql+pymysql",
        username=settings.DATABASE_USER or "root",
        password=settings.DATABASE_PASSWORD or "",
        host=settings.DATABASE_HOST or "localhost",
        port=settings.DATABASE_PORT or 3306,
        database=settings.DATABASE_NAME or "stockflow_db",
    )


db_url = build_database_url()

engine = create_engine(
    db_url,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
