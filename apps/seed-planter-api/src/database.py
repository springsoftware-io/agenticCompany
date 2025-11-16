"""Database configuration and session management."""
import logging
import time
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import config as settings

logger = logging.getLogger(__name__)

# Create database engine with Cloud SQL optimizations
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,  # Verify connections before using
    pool_size=5,  # Reduced for Cloud Run
    max_overflow=10,  # Reduced for Cloud Run
    pool_recycle=1800,  # Recycle connections after 30 minutes
    connect_args={
        "connect_timeout": 10,  # 10 second connection timeout
    } if not settings.database_url.startswith("sqlite") else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """Database dependency for FastAPI routes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db(max_retries: int = 3, retry_delay: int = 2):
    """Initialize database tables with retry logic.
    
    Args:
        max_retries: Maximum number of connection attempts
        retry_delay: Seconds to wait between retries
    """
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempting database initialization (attempt {attempt + 1}/{max_retries})...")
            Base.metadata.create_all(bind=engine)
            logger.info("✅ Database tables initialized successfully")
            return
        except Exception as e:
            logger.warning(f"Database initialization attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("❌ Failed to initialize database after all retries")
                # Don't raise - allow app to start even if DB init fails
                # The app will fail gracefully on first DB operation
                logger.warning("⚠️ Starting without database initialization - DB operations may fail")
