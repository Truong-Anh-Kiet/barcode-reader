"""
This module defines the API endpoints for barcode scanning and retrieval.

It uses FastAPI for routing and dependency injection.
"""
import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, Query
from sqlalchemy.ext.asyncio import AsyncSession

from application.schemas import (
    BarcodeItem, BarcodeResponse,
    BoundingBoxSchema, GetBarcodesResponse,
    ScanResultResponse)
from application.use_cases import GetBarcodesUseCase, ScanBarcodeUseCase, DeleteBarcodeUseCase
from application.auth import current_active_user
from infrastructure.cloudinary_storage import CloudinaryStorage
from infrastructure.database import get_db_session
from infrastructure.detector_singleton import get_detector
from infrastructure.image_processor import OpenCVImageProcessor
from infrastructure.repository import PostgresBarcodeRepository
router = APIRouter()

async def get_scan_use_case(session: AsyncSession = Depends(get_db_session)) -> ScanBarcodeUseCase:
    detector = get_detector()
    repository = PostgresBarcodeRepository(session)
    storage = CloudinaryStorage()
    processor = OpenCVImageProcessor()
    return ScanBarcodeUseCase(detector, repository, storage, processor)

@router.post("/scan", response_model=ScanResultResponse, response_model_exclude_none=True, tags=["barcodes"])
async def scan_endpoint(
    file: UploadFile = File(...),
    user=Depends(current_active_user),
    scan_use_case: ScanBarcodeUseCase = Depends(get_scan_use_case)
):
    if not file.content_type.startswith('image/'):
        raise HTTPException(400, "File must be an image")
    if file.size > 5 * 1024 * 1024:
        raise HTTPException(413, "File too large")

    try:
        image_data = await file.read()
        entities = await scan_use_case.execute(image_data, file.filename, user)
        results = [
            BarcodeResponse(
                content=e.content,
                type=e.barcode_type,
                confidence=1.0,
                box=BoundingBoxSchema(
                    x=e.bounding_box[0],
                    y=e.bounding_box[1],
                    width=e.bounding_box[2],
                    height=e.bounding_box[3]
                ),
                image_url=e.image_url,
                processed_image_url=e.processed_image_url
            )
            for e in entities
        ]
        return ScanResultResponse(
            success=True,
            count=len(results),
            data=results
        )
    except Exception as e:
        logging.exception("Error in scan")
        raise HTTPException(500, "Internal server error")

async def get_get_use_case(session: AsyncSession = Depends(get_db_session)) -> GetBarcodesUseCase:
    repository = PostgresBarcodeRepository(session)
    return GetBarcodesUseCase(repository)

@router.get("/list", response_model=GetBarcodesResponse, tags=["barcodes"])
async def list_barcodes(
    user = Depends(current_active_user),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    get_use_case: GetBarcodesUseCase = Depends(get_get_use_case)
):
    entities = await get_use_case.execute(user_id=user.id, limit=limit, offset=offset)
    results = [
        BarcodeItem(
            id=item.id,
            content=item.content,
            barcode_type=item.barcode_type,
            bounding_box=item.bounding_box,
            created_at=item.created_at,
            image_url=item.image_url,
            processed_image_url=item.processed_image_url
        )
        for item in entities
    ]
    return GetBarcodesResponse(success=True, count=len(results), data=results)


async def get_delete_use_case(session: AsyncSession = Depends(get_db_session)) -> DeleteBarcodeUseCase:
    repository = PostgresBarcodeRepository(session)
    storage = CloudinaryStorage()
    return DeleteBarcodeUseCase(repository, storage)

@router.delete("/{id}", tags=["barcodes"])
async def delete_barcode(
    id: int,
    user = Depends(current_active_user),
    delete_use_case: DeleteBarcodeUseCase = Depends(get_delete_use_case)
):
    success = await delete_use_case.execute(id, user)
    if success:
        return {"message": "Deleted successfully"}
    raise HTTPException(404, "Not found")