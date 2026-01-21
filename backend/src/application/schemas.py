"""
This module defines schemas for barcode scanning responses.

It includes models for bounding boxes, barcode responses, and scan results
using Pydantic for validation and serialization.
"""

from typing import List, Optional
from datetime import datetime

from pydantic import BaseModel, Field, EmailStr
from fastapi_users import schemas

class BoundingBoxSchema(BaseModel):
    """
    Schema representing an axis-aligned bounding box.

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
    """
    Response model for a detected barcode.

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
    image_url: Optional[str] = None
    processed_image_url: Optional[str] = None

class ScanResultResponse(BaseModel):
    """
    Response model for barcode scan results.

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

class BarcodeItem(BaseModel):
    """
    Schema for a single barcode item retrieved from the database.

    Attributes:
        id (int): Unique identifier of the barcode.
        content (str): The decoded barcode string.
        barcode_type (str): Type of the barcode.
        bounding_box (List[int]): Bounding box as [x, y, w, h].
        created_at (datetime): Timestamp when the barcode was created.
    """
    id: int
    content: str
    barcode_type: str
    bounding_box: List[int]
    created_at: datetime
    image_url: Optional[str] = None
    processed_image_url: Optional[str] = None

class GetBarcodesResponse(BaseModel):
    """
    Response model for retrieving all barcodes.

    Attributes:
        success (bool): True if the operation completed successfully.
        count (int): Number of barcode items returned.
        data (List[BarcodeItem]): List of barcode items.
        message (str): Informational message (defaults to "Success").
    """
    success: bool
    count: int
    data: List[BarcodeItem]
    message: str = "Success"

class UserRead(schemas.BaseUser[int]):
    """
    Schema trả về thông tin user sau khi đăng ký hoặc lấy thông tin (read-only).
    Không chứa hashed_password.
    """
    id: int
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False

    class Config:
        from_attributes = True  # Cho phép chuyển từ SQLAlchemy model


class UserCreate(schemas.BaseUserCreate):
    """
    Schema nhận dữ liệu từ body khi đăng ký (register).
    """
    email: EmailStr
    password: str = Field(..., min_length=8, description="Mật khẩu ít nhất 8 ký tự")
    full_name: Optional[str] = None