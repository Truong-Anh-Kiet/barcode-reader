from fastapi import APIRouter, UploadFile, File, Depends
from src.application.use_cases import ScanBarcodeUseCase

router = APIRouter()

# Lưu ý: Chúng ta sẽ inject use_case từ main.py
def get_barcode_router(scan_use_case: ScanBarcodeUseCase):
    @router.post("/scan")
    async def scan_endpoint(file: UploadFile = File(...)):
        image_data = await file.read()
        results = scan_use_case.execute(image_data)
        return {"count": len(results), "data": results}
    
    return router