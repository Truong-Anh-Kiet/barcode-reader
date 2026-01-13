"""
This module contains use cases for barcode scanning and processing.

It defines the ScanBarcodeUseCase class, which handles barcode detection
and persistence using the provided detector and repository components.
"""

from typing import List

from core.entities import BarcodeResult
from core.interfaces import IBarcodeDetector, IBarcodeRepository


class ScanBarcodeUseCase:
    """Use case for scanning an image for barcodes and persisting the results.
    This class orchestrates barcode detection and storage by delegating detection
    to an IBarcodeDetector and saving each detected BarcodeResult via an
    IBarcodeRepository.
    Args:
        detector: IBarcodeDetector
            Component that extracts barcode data from raw image bytes.
        repository: IBarcodeRepository
            Component that persists detected BarcodeResult instances.
    Methods:
        execute(image_data: bytes) -> List[BarcodeResult]:
            Detects barcodes within image_data, saves each result to the
            repository, and returns the list of detected BarcodeResult objects.
    """

    def __init__(self, detector: IBarcodeDetector, repository: IBarcodeRepository):
        self.detector = detector
        self.repository = repository

    def execute(self, image_data: bytes) -> List[BarcodeResult]:
        """
        Executes the barcode detection process on the provided image data.
        This method uses the detector to identify barcodes in the given image data
        and saves the detected results to the repository.
        Args:
            image_data (bytes): The image data to process for barcode detection.
        Returns:
            List[BarcodeResult]: A list of detected barcode results.
        """
        results  = self.detector.detect(image_data)
        for item in results:
            self.repository.save(item)
        return results
    