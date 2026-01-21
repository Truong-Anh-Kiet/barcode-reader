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
    ScanResultResponse, UserRead, UserCreate)
from application.use_cases import GetBarcodesUseCase, ScanBarcodeUseCase, DeleteBarcodeUseCase
from application.auth import current_superuser
from domain.interfaces import IImageProcessor, IImageStorage
from infrastructure.cloudinary_storage import CloudinaryStorage
from infrastructure.database import get_db_session
from infrastructure.detector import PyzbarDetector
from infrastructure.image_processor import OpenCVImageProcessor
from infrastructure.repository import PostgresBarcodeRepository

# Import từ auth
from application.auth import (
    fastapi_users,
    auth_backend,
    current_active_user
)

router = APIRouter()

# Include auth routers từ fastapi-users
router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

# Protected endpoint example: Get info of current logged-in user
@router.get("/users/me", tags=["auth"])
async def read_users_me(user=Depends(current_active_user)):
    """
    Returns information about the currently authenticated user.
    """
    return {
        "id": user.id,
        "email": user.email,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
        "is_verified": user.is_verified
    }

# Dependency cho ScanBarcodeUseCase
async def get_scan_use_case(
    session: AsyncSession = Depends(get_db_session)
) -> ScanBarcodeUseCase:
    """
    Dependency provider for ScanBarcodeUseCase.
    """
    detector = PyzbarDetector()
    repository = PostgresBarcodeRepository(session)
    storage: IImageStorage = CloudinaryStorage()
    processor: IImageProcessor = OpenCVImageProcessor()
    return ScanBarcodeUseCase(detector, repository, storage, processor)

# Dependency cho GetBarcodesUseCase
async def get_get_use_case(
    session: AsyncSession = Depends(get_db_session)
) -> GetBarcodesUseCase:
    """
    Dependency provider for GetBarcodesUseCase.
    """
    repository = PostgresBarcodeRepository(session)
    return GetBarcodesUseCase(repository)

@router.post("/scan", response_model=ScanResultResponse, response_model_exclude_none=True, tags=["barcodes"])
async def scan_endpoint(
    file: UploadFile = File(...),
    user=Depends(current_active_user),  # Yêu cầu phải login (JWT Bearer)
    scan_use_case: ScanBarcodeUseCase = Depends(get_scan_use_case)
):
    """
    Endpoint to scan an uploaded image for barcodes (protected: requires authentication).

    Validates the file type, reads the image, executes the use case, and returns results.
    """
    #if not user.is_superuser:
    #    raise HTTPException(status_code=403, detail="Permission denied")

    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    if file.size > 5 * 1024 * 1024:  # 5MB max
        raise HTTPException(status_code=413, detail="File too large")

    try:
        image_data = await file.read()
        entities = await scan_use_case.execute(image_data, file.filename)
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

    except ValueError as e:
        logging.error("Error: %s", str(e))
        raise HTTPException(status_code=400, detail=f"Value error: {str(e)}") from e

    except Exception as e:
        logging.exception("Unexpected error in scan endpoint")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/list", response_model=GetBarcodesResponse, tags=["barcodes"])
async def list_barcodes(
    limit: int = Query(10, ge=1, le=100),  # Default 10, max 100
    offset: int = Query(0, ge=0),
    get_use_case: GetBarcodesUseCase = Depends(get_get_use_case)
):
    """
    Endpoint to retrieve all saved barcodes (public - no login required).
    If you want to protect it, add: user=Depends(current_active_user)
    """
    entities = await get_use_case.execute(limit=limit, offset=offset)
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
    _=Depends(current_superuser),  # Chỉ superuser
    delete_use_case: DeleteBarcodeUseCase = Depends(get_delete_use_case)
):
    # Trước tiên get entity để lấy urls (hoặc thêm param)
    # Giả sử bạn thêm get_by_id vào repo, rồi execute
    success = await delete_use_case.execute(id, "image_url", "processed_url")  # Thay bằng real urls từ get
    if success:
        return {"message": "Deleted successfully"}
    raise HTTPException(404, "Not found")