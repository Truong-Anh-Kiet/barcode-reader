from pydantic import BaseModel, Field
from typing import List

class BoundingBoxSchema(BaseModel):
    x: int
    y: int
    width: int
    height: int

class BarcodeResponse(BaseModel):
    """Cấu trúc JSON trả về cho 1 barcode đơn lẻ"""
    content: str = Field(..., example="8934565010015")
    type: str = Field(..., example="EAN13")
    confidence: float = Field(default=1.0, ge=0, le=1.0)
    box: BoundingBoxSchema 

class ScanResultResponse(BaseModel):
    """Cấu trúc JSON trả về tổng quát cho 1 lần quét"""
    success: bool
    count: int
    data: List[BarcodeResponse]
    message: str = "Success"