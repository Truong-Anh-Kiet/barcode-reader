"""
This module defines interfaces for barcode detection and repository operations.

It includes abstract base classes for detecting barcodes in images and saving
barcode results to a repository.
"""

from abc import ABC, abstractmethod
from typing import List

from .entities import BarcodeResult


class IBarcodeDetector(ABC):
    """
    Interface for barcode detection.

    This abstract base class defines the structure for implementing a barcode detector.
    Classes inheriting from this interface must provide an implementation for the `detect` method.

    Methods:
        detect(image_bytes: bytes) -> List[BarcodeResult]:
            Abstract method to detect barcodes in the given image data.
            Args:
                image_bytes (bytes): The image data in bytes format.
            Returns:
                List[BarcodeResult]: A list of detected barcode results.
    """
    @abstractmethod
    def detect(self, image_bytes: bytes) -> List[BarcodeResult]:
        """
        Detects barcodes in the given image.

        Args:
            image_bytes (bytes): The image data in bytes format.

        Returns:
            List[BarcodeResult]: A list of detected barcode results.
        """

class IBarcodeRepository(ABC):
    """
    Interface for a barcode repository.

    This abstract base class defines the contract for implementing a barcode repository.
    Classes inheriting from this interface must provide an implementation for the `save` method.

    Methods:
        save(barcode: BarcodeResult) -> bool:
            Abstract method to save a barcode result. Must be implemented by subclasses.
    """
    @abstractmethod
    def save(self, barcode: BarcodeResult) -> bool:
        """
        Saves the provided barcode result.

        Args:
            barcode (BarcodeResult): The barcode result to be saved.

        Returns:
            bool: True if the barcode result was saved successfully, False otherwise.
        """
        