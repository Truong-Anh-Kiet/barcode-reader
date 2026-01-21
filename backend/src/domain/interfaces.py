"""
This module defines interfaces for barcode detection and repository operations.

It includes abstract base classes for detecting barcodes in images and saving
barcode results to a repository, following the dependency inversion principle.
"""

from abc import ABC, abstractmethod
from typing import List, Tuple

from .entities import BarcodeResult

class IBarcodeDetector(ABC):
    """
    Interface for barcode detection logic.

    Defines the contract for detecting barcodes from image data.
    """

    @abstractmethod
    def detect(self, image_bytes: bytes) -> List[BarcodeResult]:
        """
        Detects barcodes in the given image data.

        Args:
            image_bytes (bytes): Raw binary data of the image.

        Returns:
            List[BarcodeResult]: List of detected barcode results.
        """

class IBarcodeRepository(ABC):
    """
    Interface for barcode data persistence.

    Defines the contract for saving and retrieving barcode results.
    """

    @abstractmethod
    async def save(self, barcode: BarcodeResult) -> bool:
        """
        Asynchronously saves the provided barcode result.

        Args:
            barcode (BarcodeResult): The barcode entity to save.

        Returns:
            bool: True if save was successful.
        """

    @abstractmethod
    async def get_all(self) -> List[BarcodeResult]:
        """
        Retrieves all saved barcode models.

        Returns:
            List[BarcodeResult]: List of all barcode models in the database.
        """

    @abstractmethod
    async def delete(self, id: int) -> bool:
        """
        Deletes a barcode by its ID.
        """
        
class IImageStorage(ABC):
    """
    Interface for image storage operations.
    Defines contract for uploading and managing images.
    """

    @abstractmethod
    def upload_image(self, image_data: bytes, filename: str) -> str:
        """
        Uploads image data and returns the secure URL.

        Args:
            image_data (bytes): Raw binary data of the image.
            filename (str): Original filename for reference.

        Returns:
            str: Secure URL of the uploaded image.
        """

    @abstractmethod
    def delete_image(self, public_id: str) -> bool:
        """
        Deletes an image by public_id.

        Args:
            public_id (str): Public ID of the image.

        Returns:
            bool: True if deletion was successful.
        """
class IImageProcessor(ABC):
    """
    Interface for image processing operations.
    Defines contract for preprocessing and post-processing images in the barcode detection pipeline.
    """

    @abstractmethod
    def process_image(self, image_data: bytes) -> bytes:
        """
        Full preprocessing pipeline: ingestion, resize, grayscale, contrast enhancement,
        noise reduction, adaptive thresholding, edge detection, and perspective fix.

        Args:
            image_data (bytes): Raw binary data of the image.

        Returns:
            bytes: Processed image data ready for detection.
        """

    @abstractmethod
    def crop_region(self, image_data: bytes, bounding_box: Tuple[int, int, int, int]) -> bytes:
        """
        Crops a specific region from the image based on bounding box.

        Args:
            image_data (bytes): Raw binary data of the image.
            bounding_box (Tuple[int, int, int, int]): (x, y, width, height)

        Returns:
            bytes: Cropped image data as bytes.
        """

    @abstractmethod
    def multi_scale_detect(self,
                           processed_data: bytes,
                           detector: IBarcodeDetector) -> List[BarcodeResult]:
        """
        Performs detection at multiple scales to handle small/large barcodes.

        Args:
            processed_data (bytes): Preprocessed image data.
            detector (IBarcodeDetector): The detector to use.

        Returns:
            List[BarcodeResult]: Merged detection results from multiple scales.
        """
        