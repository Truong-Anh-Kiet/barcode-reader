from src.core.interfaces import IBarcodeRepository
from src.core.entities import BarcodeResult

class InMemoryBarcodeRepository(IBarcodeRepository):
    """Lưu tạm vào bộ nhớ (Có thể thay bằng SQL ở đây)"""
    def __init__(self):
        self.db = []

    def save(self, barcode: BarcodeResult) -> bool:
        self.db.append(barcode)
        print(f"[Repo] Saved barcode: {barcode.content}")
        return True