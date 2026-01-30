"""
Infrastructure layer: Database configuration and models.

Defines the SQLAlchemy Base, engine, and async session setup for PostgreSQL.
Also defines the BarcodeModel representing the database table structure.
"""
import logging
from datetime import datetime
from typing import AsyncGenerator, Optional

from fastapi.params import Depends
from fastapi_users.db import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase

from sqlalchemy import ARRAY, DateTime, Integer, String, ForeignKey, func
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from config.settings import settings

logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

class BarcodeModel(Base):
    """
    SQLAlchemy model representing the 'barcodes' table in the database.
    """

    __tablename__ = "barcodes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    content: Mapped[str] = mapped_column(nullable=False, index=True)
    barcode_type: Mapped[str] = mapped_column(nullable=False)
    bounding_box: Mapped[list[int]] = mapped_column(ARRAY(Integer), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    image_url: Mapped[str | None] = mapped_column(nullable=True)
    processed_image_url: Mapped[str | None] = mapped_column(nullable=True)
    original_public_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    processed_public_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), 
                                                nullable=False,
                                                server_default=func.now())
    
class UserModel(Base, SQLAlchemyBaseUserTable[int]):    
    """
    SQLAlchemy model representing the 'users' table in the database.
    """
    __tablename__ = "users"

    # Field custom thêm vào
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(length=255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(length=1024), nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=True)
    phone_number: Mapped[str] = mapped_column(String(15), unique=True, nullable=True)
    avatar_url: Mapped[str] = mapped_column(String(255), nullable=True)
    is_premium: Mapped[bool] = mapped_column(default=False)
    country: Mapped[str] = mapped_column(String(50), nullable=False, default="Vietnam")

engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency provider for FastAPI: yields a new async database session per request.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            logger.exception(f"DB session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()

async def get_user_db(session: AsyncSession = Depends(get_db_session)):
    """
    Get the user database instance.
    """
    yield SQLAlchemyUserDatabase(session, UserModel)

    