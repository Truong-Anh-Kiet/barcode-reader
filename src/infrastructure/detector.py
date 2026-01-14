"""
This module contains the implementation of a barcode detector using the ZXing library.

The ZxingDetector class provides functionality to detect and decode barcodes from
images represented as byte arrays. It returns the results as a list of BarcodeResult objects.
"""

from typing import List

import cv2
import numpy as np
import zxingcpp

from domain.entities import BarcodeResult
from domain.interfaces import IBarcodeDetector

class ZxingDetector(IBarcodeDetector):
    """
    A barcode detector implementation using the ZXing library.

    This class decodes images from bytes, processes them with ZXing,
    and extracts barcode metadata including content, type, and bounding box.

    Attributes:
        None (implements IBarcodeDetector interface).
    """

    def detect(self, image_bytes: bytes) -> List[BarcodeResult]:
        """
        Detects barcodes in the given image bytes.

        Processes the image using OpenCV and ZXing, then maps results to BarcodeResult entities.

        Args:
            image_bytes (bytes): Raw binary data of the image.

        Returns:
            List[BarcodeResult]: List of detected barcode results. 
            Empty if no barcodes or invalid image.
        """
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return []

        results = zxingcpp.read_barcodes(img)
        barcode_results = []
        for res in results:
            position = res.position
            x_coords = [position.top_left.x, position.top_right.x,
                        position.bottom_right.x, position.bottom_left.x]
            y_coords = [position.top_left.y, position.top_right.y,
                        position.bottom_right.y, position.bottom_left.y]
            x, y = min(x_coords), min(y_coords)
            w, h = max(x_coords) - x, max(y_coords) - y
            barcode_results.append(BarcodeResult(
                content=res.text,
                barcode_type=str(res.format).rsplit('.', maxsplit=1)[-1],
                bounding_box=(int(x), int(y), int(w), int(h))
            ))
        return barcode_results
    