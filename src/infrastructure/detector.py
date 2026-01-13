"""
This module contains the implementation of a barcode detector using the PyZbar library.

The `PyZbarDetector` class provides functionality to detect and decode barcodes from
images represented as byte arrays. It returns the results as a list of `BarcodeResult` objects.
"""

from typing import List

import cv2
import numpy as np
from pyzbar import pyzbar

from core.entities import BarcodeResult
from core.interfaces import IBarcodeDetector


class PyZbarDetector(IBarcodeDetector):
    """
    A barcode detector implementation using the PyZbar library.

    This class provides functionality to detect and decode barcodes from an image
    represented as a byte array. It processes the image, decodes the barcodes, and
    returns the results as a list of `BarcodeResult` objects.

    Methods:
        detect(image_bytes: bytes) -> List[BarcodeResult]:
            Detects and decodes barcodes from the given image bytes.
    """
    def detect(self, image_bytes: bytes) -> List[BarcodeResult]:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR) # type: ignore
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
    