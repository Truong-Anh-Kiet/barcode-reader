"""
This module defines the API endpoints for barcode scanning.
"""

from fastapi import APIRouter, File, UploadFile

from application.schemas import (BarcodeResponse, BoundingBoxSchema,
                                     ScanResultResponse)

router = APIRouter()

def get_barcode_router(scan_use_case):
    """
    Creates and returns a FastAPI router for barcode scanning.
    Args:
        scan_use_case: An instance of a use case class responsible for executing the barcode 
        scanning logic.
    Returns:
        APIRouter: A FastAPI router with an endpoint for scanning barcodes.
    The router includes the following endpoint:
    - POST /scan: Accepts an image file, processes it to detect barcodes, and returns the results 
        as a list of barcodes with their details.
    """
    @router.post("/scan", response_model=ScanResultResponse) # <-- Định nghĩa kiểu trả về
    async def scan_endpoint(file: UploadFile = File(...)):
        image_data = await file.read()

        entities = scan_use_case.execute(image_data)
        results = [
            BarcodeResponse(
                content=e.content,
                type=e.barcode_type,
                confidence=1.0,
                box=BoundingBoxSchema(x=e.bounding_box[0], y=e.bounding_box[1],
                                      width=e.bounding_box[2], height=e.bounding_box[3])
            ) for e in entities
        ]
        return ScanResultResponse(
            success=True,
            count=len(results),
            data=results
        )
    return router
