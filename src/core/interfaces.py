from abc import ABC, abstractmethod
from .entities import BarcodeResult
from typing import List

class IBarcodeDetector(ABC):
    @abstractmethod
    def detect(self, image_bytes: bytes) -> List[BarcodeResult]:
        pass

class IBarcodeRepository(ABC):
    @abstractmethod
    def save(self, barcode: BarcodeResult) -> bool:
        pass