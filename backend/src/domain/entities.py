"""
This module defines the BarcodeResult entity, which represents the result of a barcode scan.

Entities are domain objects that hold business data without behavior.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Tuple, Optional
from fastapi_users import schemas

@dataclass
class BarcodeResult:
    """
    Represents the result of a barcode detection.

    This is an immutable dataclass for thread-safety and simplicity.

    Attributes:
        content (str): The decoded content of the barcode.
        barcode_type (str): The type or format of the barcode (e.g., QR code, Code 128).
        bounding_box (Tuple[int, int, int, int]): The bounding box of the detected barcode, 
            represented as a tuple (x, y, width, height).
    """
    content: str
    barcode_type: str
    bounding_box: Tuple[int, int, int, int]  # (x, y, w, h)
    image_url: Optional[str] = None  # URL to the image containing the barcode, if applicable
    processed_image_url: Optional[str] = None
    original_public_id: Optional[str] = None
    processed_public_id: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None

    def __post_init__(self):
        if not self.content:
            raise ValueError("Barcode content cannot be empty.")
        if not self.barcode_type:
            raise ValueError("Barcode type cannot be empty.")
        if len(self.bounding_box) != 4:
            raise ValueError("Bounding box must be a tuple of four integers (x, y, width, height).")
        if self.image_url is not None and not self.image_url.startswith(("http://", "https://")):
            raise ValueError("Image URL must be a valid URL starting with http:// or https://")