"""
Application Layer: Business Logic Orchestration.

Contains the use cases that coordinate domain entities and infrastructure 
interfaces to perform business operations.
"""

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
        # Upload original image
        image_url = self.storage.upload_image(image_data, filename)

        # Full preprocessing pipeline
        processed_data = self.processor.process_image(image_data)

        # Multi-scale detection
        results = self.processor.multi_scale_detect(processed_data, self.detector)
        for item in results:
            # Post-processing: Crop region and upload crop
            crop_data = self.processor.crop_region(image_data, item.bounding_box)
            crop_filename = f"{filename}_crop_{item.content}"
            processed_image_url = self.storage.upload_image(crop_data, crop_filename)

            item.image_url = image_url
            item.processed_image_url = processed_image_url
            await self.repository.save(item)
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

    async def execute(self) -> List[BarcodeResult]:
        """
        Retrieves all barcode results from the repository.

        Returns:
            List[BarcodeResult]: List of all saved barcode entities.
        """
        db_items = await self.repository.get_all()
        return [BarcodeResult(
            content=item.content,
            barcode_type=item.barcode_type,
            bounding_box=tuple(item.bounding_box),
            image_url=item.image_url
        ) for item in db_items]
    