"""
This module defines schemas for barcode scanning responses.

It includes models for bounding boxes, barcode responses, and scan results.
"""

from typing import List

from pydantic import BaseModel, Field


class BoundingBoxSchema(BaseModel):
    """Schema representing an axis-aligned bounding box.
    Attributes:
        x (int): X-coordinate of the top-left corner (pixels).
        y (int): Y-coordinate of the top-left corner (pixels).
        width (int): Width of the bounding box (pixels).
        height (int): Height of the bounding box (pixels).
    Notes:
        Coordinates are relative to the image origin (top-left). All values are integers.
    """
    x: int
    y: int
    width: int
    height: int

class BarcodeResponse(BaseModel):
    """Response model for a detected barcode.

    Attributes:
        content (str): The decoded barcode string (e.g. "8934565010015").
        type (str): Barcode symbology/type (e.g. "EAN13").
        confidence (float): Confidence score between 0.0 and 1.0 (default 1.0).
        box (BoundingBoxSchema): Bounding box describing the barcode location.
    """
    content: str = Field(..., example="8934565010015")
    type: str = Field(..., example="EAN13")
    confidence: float = Field(default=1.0, ge=0, le=1.0)
    box: BoundingBoxSchema

class ScanResultResponse(BaseModel):
    """Response model for barcode scan results.

    Attributes:
        success (bool): True if the scan operation completed successfully.
        count (int): Number of barcode items returned in the response.
        data (List[BarcodeResponse]): List of barcode result objects.
        message (str): Informational message about the scan result (defaults to "Success").
    """
    success: bool
    count: int
    data: List[BarcodeResponse]
    message: str = "Success"
