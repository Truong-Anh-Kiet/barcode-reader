"""
Infrastructure layer: Database repository implementation.

Provides methods to persist and retrieve barcode results into a PostgreSQL database 
using SQLAlchemy AsyncSession.
"""
from typing import List, Optional
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from domain.entities import BarcodeResult
from domain.interfaces import IBarcodeRepository
from .database import BarcodeModel

class PostgresBarcodeRepository(IBarcodeRepository):
    """
    PostgreSQL implementation of the barcode repository.

    Handles CRUD operations for barcode data using an injected async session.

    Attributes:
        session (AsyncSession): The database session injected via FastAPI.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, barcode: BarcodeResult) -> bool:
        """
        Asynchronously saves the provided barcode result to the database.

        Args:
            barcode (BarcodeResult): The barcode entity to save.

        Returns:
            bool: True if the save was successful.
        """
        # Check duplicate
        stmt = select(BarcodeModel).where(
            BarcodeModel.content == barcode.content,
            BarcodeModel.barcode_type == barcode.barcode_type,
            BarcodeModel.image_url == barcode.image_url
        )
        result = await self.session.execute(stmt)
        if result.scalar_one_or_none():
            return False  # Hoặc raise DuplicateError nếu muốn throw exception

        db_item = BarcodeModel(
            content=barcode.content,
            barcode_type=barcode.barcode_type,
            bounding_box=list(barcode.bounding_box),
            image_url=barcode.image_url,
            processed_image_url=barcode.processed_image_url
        )
        self.session.add(db_item)
        await self.session.commit()
        return True

    async def get_all(self, limit: int = 10, offset: int = 0) -> List[BarcodeResult]:
        """
        Retrieves all barcode models from the database, ordered by creation time descending,
        and converts them to domain entities.

        Returns:
            List[BarcodeResult]: List of domain barcode entities.
        """
        stmt = select(BarcodeModel).order_by(BarcodeModel.created_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        db_items = result.scalars().all()
        return [
            BarcodeResult(
                content=item.content,
                barcode_type=item.barcode_type,
                bounding_box=tuple(item.bounding_box),
                image_url=item.image_url,
                processed_image_url=item.processed_image_url,
                id=item.id,
                created_at=item.created_at
            )
            for item in db_items
        ]
    
    async def delete(self, id: int) -> bool:
        stmt = delete(BarcodeModel).where(BarcodeModel.id == id)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0
    
    async def get_by_id(self, id: int) -> Optional[BarcodeResult]:
        stmt = select(BarcodeModel).where(BarcodeModel.id == id)
        result = await self.session.execute(stmt)
        item = result.scalar_one_or_none()
        if not item:
            return None
        return BarcodeResult(
            content=item.content,
            barcode_type=item.barcode_type,
            bounding_box=tuple(item.bounding_box),
            image_url=item.image_url,
            processed_image_url=item.processed_image_url,
            id=item.id,
            created_at=item.created_at
        )
