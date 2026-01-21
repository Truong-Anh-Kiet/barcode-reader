"""
Infrastructure layer: Database configuration and models.

Defines the SQLAlchemy Base, engine, and async session setup for PostgreSQL.
Also defines the BarcodeModel representing the database table structure.
"""
import os
from datetime import datetime, timezone
from typing import AsyncGenerator
from dotenv import load_dotenv
from fastapi_users.db import SQLAlchemyBaseUserTable
from sqlalchemy import ARRAY, Column, DateTime, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeMeta, Mapped, mapped_column

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
    """

    __tablename__ = "barcodes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    content: Mapped[str] = mapped_column(nullable=False, index=True)
    barcode_type: Mapped[str] = mapped_column(nullable=False)
    bounding_box: Mapped[list[int]] = mapped_column(ARRAY(Integer), nullable=False)
    image_url: Mapped[str | None] = mapped_column(nullable=True)
    processed_image_url: Mapped[str | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), 
                                                 default=lambda: datetime.now(timezone.utc), 
                                                 nullable=False)
    
class UserModel(SQLAlchemyBaseUserTable[int], Base):
    """
    SQLAlchemy model representing the 'users' table in the database.
    """
    __tablename__ = "users"

    # Field custom thêm vào
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(100), nullable=True)          # Họ tên đầy đủ, có thể NULL
    phone_number: Mapped[str] = mapped_column(String(15), unique=True, nullable=True)  # Số điện thoại, unique
    avatar_url: Mapped[str] = mapped_column(String(255), nullable=True)         # Link ảnh đại diện
    is_premium: Mapped[bool] = mapped_column(default=False)                     # Boolean, mặc định False
    country: Mapped[str] = mapped_column(String(50), nullable=False, default="Vietnam")

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
    