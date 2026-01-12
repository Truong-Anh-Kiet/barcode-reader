from fastapi import APIRouter, UploadFile, File
from src.application.schemas import ScanResultResponse, BarcodeResponse, BoundingBoxSchema

router = APIRouter()

def get_barcode_router(scan_use_case):
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