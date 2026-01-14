"""
Infrastructure layer: Database configuration and models.

Defines the SQLAlchemy Base, engine, and async session setup for PostgreSQL.
Also defines the BarcodeModel representing the database table structure.
"""
import os
from datetime import datetime
from typing import AsyncGenerator
from dotenv import load_dotenv
from sqlalchemy import ARRAY, Column, DateTime, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeMeta

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL not found in environment variables. "
        "Please set it in .env file, e.g.: "
        "DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname"
    )

# Base class for all models
Base: DeclarativeMeta = declarative_base()

class BarcodeModel(Base):
    """
    SQLAlchemy model representing the 'barcodes' table in the database.

    This model stores the results of barcode scans, including content, type,
    bounding box coordinates, optional image URL from Cloudinary, and creation timestamp.

    Attributes:
        id (int): Primary key, auto-incremented.
        content (str): The decoded content of the barcode.
        barcode_type (str): The type/format of the barcode (e.g., EAN13, QRCode).
        bounding_box (list[int]): List of 4 integers [x, y, width, height].
        image_url (str | None): Secure URL of the uploaded image from Cloudinary (optional).
        created_at (datetime): Timestamp when the record was created.
    """

    __tablename__ = "barcodes"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False, index=True)
    barcode_type = Column(String, nullable=False)
    bounding_box = Column(ARRAY(Integer), nullable=False)
    image_url = Column(String, nullable=True)
    processed_image_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now(datetime.timezone.utc), nullable=False)

engine = create_async_engine(DATABASE_URL, echo=False, future=True)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency provider for FastAPI: yields a new async database session per request.

    Usage in FastAPI:
        session: AsyncSession = Depends(get_db_session)

    Yields:
        AsyncSession: Database session for the current request.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def create_tables():
    """Create all tables in the database if they don't exist."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    import asyncio

    asyncio.run(create_tables())
    print("Tables created successfully!")
    