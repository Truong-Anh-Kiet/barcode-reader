import cv2
import numpy as np
from pyzbar import pyzbar
from typing import List
from src.core.interfaces import IBarcodeDetector
from src.core.entities import BarcodeResult

class PyZbarDetector(IBarcodeDetector):
    def detect(self, image_bytes: bytes) -> List[BarcodeResult]:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return []

        decoded_objects = pyzbar.decode(img)
        results = []
        
        for obj in decoded_objects:
            (x, y, w, h) = obj.rect
            results.append(BarcodeResult(
                content=obj.data.decode("utf-8"),
                barcode_type=obj.type,
                bounding_box=(x, y, w, h)
            ))
        return results