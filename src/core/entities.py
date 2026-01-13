"""
This module defines the BarcodeResult entity, which represents the result of a barcode scan.
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class BarcodeResult:
    """
    Represents the result of a barcode detection.

    Attributes:
        content (str): The decoded content of the barcode.
        barcode_type (str): The type or format of the barcode (e.g., QR code, Code 128).
        bounding_box (Tuple[int, int, int, int]): The bounding box of the detected barcode, 
            represented as a tuple (x, y, width, height).
    """
    content: str
    barcode_type: str
    bounding_box: Tuple[int, int, int, int]  # (x, y, w, h)
    