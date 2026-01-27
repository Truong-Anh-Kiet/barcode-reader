"""
Application Layer: Business Logic Orchestration.

Contains the use cases that coordinate domain entities and infrastructure 
interfaces to perform business operations.
"""
import logging
from typing import List
from domain.entities import BarcodeResult
from domain.interfaces import IBarcodeDetector, IBarcodeRepository, IImageStorage, IImageProcessor
from application.auth import current_active_user
from infrastructure.database import UserModel

class ScanBarcodeUseCase:
    """
    Orchestrates the process of scanning an image and persisting the findings.

    This use case handles barcode detection from image data and saves the results
    to the repository asynchronously.

    Attributes:
        detector (IBarcodeDetector): The barcode detector interface.
        repository (IBarcodeRepository): The barcode repository interface.
    """

    def __init__(self,
                 detector: IBarcodeDetector,
                 repository: IBarcodeRepository,
                 storage: IImageStorage,
                 processor: IImageProcessor):
        self.detector = detector
        self.repository = repository
        self.storage = storage
        self.processor = processor

    async def execute(self, image_data: bytes, filename: str, user: UserModel) -> List[BarcodeResult]:
        """
        Executes the barcode detection and saves each result asynchronously.

        Args:
            image_data (bytes): Raw binary data of the image to scan.

        Returns:
            List[BarcodeResult]: Collection of all detected barcodes.
        """
        logging.info(f"Starting scan for file: {filename}")
        # Full preprocessing pipeline
        processed_data = self.processor.process_image(image_data)
        processed_filename = f"processed_{filename}"

        # Detect
        original_url, original_public_id = self.storage.upload_image(image_data, filename)
        processed_url, processed_public_id = self.storage.upload_image(processed_data, processed_filename)
        results = self.processor.multi_scale_detect(processed_data, self.detector)

        for item in results:
            item.image_url = original_url
            item.processed_image_url = processed_url
            item.original_public_id = original_public_id
            item.processed_public_id = processed_public_id
            item.user_id = user.id
            await self.repository.save(item)
        logging.info(f"Detected {len(results)} barcodes")
        return results

class GetBarcodesUseCase:
    """
    Orchestrates the retrieval of all saved barcode results.

    This use case fetches barcode data from the repository.

    Attributes:
        repository (IBarcodeRepository): The barcode repository interface.
    """

    def __init__(self, repository: IBarcodeRepository):
        self.repository = repository

    async def execute(self, user_id: int, limit: int = 10, offset: int = 0) -> List[BarcodeResult]:
        """
        Retrieves all barcode results from the repository.

        Returns:
            List[BarcodeResult]: List of all saved barcode entities.
        """
        db_items = await self.repository.get_all(limit=limit, offset=offset, user_id=user_id)
        return [
            BarcodeResult(
                content=item.content,
                barcode_type=item.barcode_type,
                bounding_box=tuple(item.bounding_box),
                image_url=item.image_url,
                processed_image_url=item.processed_image_url,
                original_public_id=item.original_public_id,
                processed_public_id=item.processed_public_id,
                id=item.id,
                created_at=item.created_at,
                user_id=item.user_id
            )
            for item in db_items
        ]

class DeleteBarcodeUseCase:
    def __init__(self, repository: IBarcodeRepository, storage: IImageStorage):
        self.repository = repository
        self.storage = storage

    async def execute(self, id: int, user: UserModel) -> bool:
        user_id_filter = None if user.is_superuser else user.id
        entity = await self.repository.get_by_id(id, user_id=user_id_filter)
        if not entity:
            return False
        if entity.original_public_id:
            self.storage.delete_image(entity.original_public_id)
        if entity.processed_public_id:
            self.storage.delete_image(entity.processed_public_id)
        return await self.repository.delete(id, user_id=user_id_filter)