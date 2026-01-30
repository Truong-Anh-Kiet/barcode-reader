"""
Domain entities for the barcode scanner application.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Tuple, Optional

@dataclass
class BarcodeResult:
    """
    Represents the result of a barcode detection.

    Attributes:
        content: Decoded barcode content.
        barcode_type: Barcode format (e.g., EAN13, QRCode).
        bounding_box: (x, y, width, height) in pixels.
        confidence: Detection confidence (0.0-1.0).
        user_id, image_url, ...: Metadata for persistence.
    """
    content: str
    barcode_type: str
    bounding_box: Tuple[int, int, int, int]
    confidence: float = 1.0
    user_id: Optional[int] = None
    image_url: Optional[str] = None
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