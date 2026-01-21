"""
Application Layer: Business Logic Orchestration.

Contains the use cases that coordinate domain entities and infrastructure 
interfaces to perform business operations.
"""
import logging
from typing import List
from domain.entities import BarcodeResult
from domain.interfaces import IBarcodeDetector, IBarcodeRepository, IImageStorage, IImageProcessor

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

    async def execute(self, image_data: bytes, filename: str) -> List[BarcodeResult]:
        """
        Executes the barcode detection and saves each result asynchronously.

        Args:
            image_data (bytes): Raw binary data of the image to scan.

        Returns:
            List[BarcodeResult]: Collection of all detected barcodes.
        """
        logging.info(f"Starting scan for file: {filename}")
        try:
            # Upload original image
            image_url = self.storage.upload_image(image_data, filename)
        except Exception as e:
            raise ValueError(f"Failed to upload original image: {str(e)}")

        # Full preprocessing pipeline
        processed_data = self.processor.process_image(image_data)

        # Multi-scale detection
        results = self.processor.multi_scale_detect(processed_data, self.detector)
        for item in results:
            # Post-processing: Crop region and upload crop
            crop_data = self.processor.crop_region(image_data, item.bounding_box)
            crop_filename = f"{filename}_crop_{item.content}"
            try:
                processed_image_url = self.storage.upload_image(crop_data, crop_filename)
            except Exception as e:
                raise ValueError(f"Failed to upload processed image: {str(e)}")
            item.image_url = image_url
            item.processed_image_url = processed_image_url
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

    async def execute(self, limit: int = 10, offset: int = 0) -> List[BarcodeResult]:
        """
        Retrieves all barcode results from the repository.

        Returns:
            List[BarcodeResult]: List of all saved barcode entities.
        """
        db_items = await self.repository.get_all(limit=limit, offset=offset)
        return [BarcodeResult(
            content=item.content,
            barcode_type=item.barcode_type,
            bounding_box=tuple(item.bounding_box),
            image_url=item.image_url,
            processed_image_url=item.processed_image_url,
            id=item.id,
            created_at=item.created_at
        ) for item in db_items]

class DeleteBarcodeUseCase:
    def __init__(self, repository: IBarcodeRepository, storage: IImageStorage):
        self.repository = repository
        self.storage = storage

    async def execute(self, id: int, image_url: str, processed_url: str) -> bool:
        # Delete images first
        public_id = image_url.split('/')[-1].split('.')[0]  # Extract public_id
        self.storage.delete_image(public_id)
        if processed_url:
            processed_id = processed_url.split('/')[-1].split('.')[0]
            self.storage.delete_image(processed_id)
        return await self.repository.delete(id)