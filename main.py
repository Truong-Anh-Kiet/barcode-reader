import uvicorn
from fastapi import FastAPI
from src.infrastructure.detector import PyZbarDetector
from src.infrastructure.repository import InMemoryBarcodeRepository
from src.application.use_cases import ScanBarcodeUseCase
from src.presentation.api import get_barcode_router

detector = PyZbarDetector()
repository = InMemoryBarcodeRepository()

scan_use_case = ScanBarcodeUseCase(detector, repository)

app = FastAPI(title="Clean Barcode API")

app.include_router(get_barcode_router(scan_use_case))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)