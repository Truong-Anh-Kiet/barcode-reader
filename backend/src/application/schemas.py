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
    """
    x: int
    y: int
    width: int
    height: int

class BarcodeResponse(BaseModel):
    """
    Response model for a detected barcode.
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
    """
    success: bool
    count: int
    data: List[BarcodeResponse]
    message: str = "Success"

class BarcodeItem(BaseModel):
    """
    Schema for a single barcode item retrieved from the database.
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
    Schema for reading user information.
    """
    id: int
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False

    class Config:
        from_attributes = True


class UserCreate(schemas.BaseUserCreate):
    """
    Schema for creating a new user.
    """
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters long.")
    full_name: Optional[str] = None

class UserUpdate(schemas.BaseUserUpdate):
    """
    Schema for updating user information.
    """
    full_name: Optional[str] = None
    phone_number: Optional[str] = None