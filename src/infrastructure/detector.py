"""
This module contains the implementation of a barcode detector using pyzbar library.

The PyzbarDetector class provides functionality to detect and decode barcodes from
images represented as byte arrays. It returns the results as a list of BarcodeResult objects.
"""

from typing import List

import cv2
import numpy as np
from pyzbar.pyzbar import decode

from domain.entities import BarcodeResult
from domain.interfaces import IBarcodeDetector


class PyzbarDetector(IBarcodeDetector):
    """
    A barcode detector implementation using the pyzbar library (based on ZBar).

    This is a reliable, fast alternative to zxingcpp, especially good for:
    - 1D barcodes: EAN13, UPC, Code128, Code39, etc.
    - QR codes and some other 2D formats

    Works well on Windows, Linux, and most environments after installing libzbar0.
    """

    def detect(self, image_bytes: bytes) -> List[BarcodeResult]:
        """
        Detects barcodes in the given image bytes using pyzbar.

        Args:
            image_bytes (bytes): Raw binary data of the image.

        Returns:
            List[BarcodeResult]: List of detected barcode results.
            Empty if no barcodes or invalid image.
        """
        # Decode bytes to OpenCV image (BGR format)
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            print("OpenCV could not decode the image!")
            return []

        # pyzbar works directly with the BGR image
        barcodes = decode(img)

        if not barcodes:
            print("pyzbar: No barcodes detected in the image.")
            return []

        barcode_results = []

        for barcode in barcodes:
            # Extract content and type
            content = barcode.data.decode('utf-8')
            barcode_type = barcode.type  # e.g. 'EAN13', 'QRCODE', 'CODE128'...

            # Get bounding box (left, top, width, height) - exactly what we need
            rect = barcode.rect
            x, y, w, h = rect.left, rect.top, rect.width, rect.height

            # Skip invalid bounding boxes
            if w <= 0 or h <= 0:
                continue

            barcode_results.append(BarcodeResult(
                content=content,
                barcode_type=barcode_type,
                bounding_box=(int(x), int(y), int(w), int(h))
            ))

        print(f"pyzbar found {len(barcode_results)} barcode(s)")
        return barcode_results