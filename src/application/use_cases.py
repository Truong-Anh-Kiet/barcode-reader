from typing import List
from src.core.interfaces import IBarcodeDetector, IBarcodeRepository
from src.core.entities import BarcodeResult

class ScanBarcodeUseCase:
    def __init__(self, detector: IBarcodeDetector, repository: IBarcodeRepository):
        self.detector = detector
        self.repository = repository

    def execute(self, image_data: bytes) -> List[BarcodeResult]:
        results = self.detector.detect(image_data)
        
        for item in results:
            self.repository.save(item)
            
        return results