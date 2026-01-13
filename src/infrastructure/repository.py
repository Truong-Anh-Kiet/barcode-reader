"""
This module contains the implementation of an in-memory barcode repository.

The `InMemoryBarcodeRepository` class provides a temporary storage solution
for barcode results, implementing the `IBarcodeRepository` interface.
"""

from core.entities import BarcodeResult
from core.interfaces import IBarcodeRepository


class InMemoryBarcodeRepository(IBarcodeRepository):
    """
    An in-memory implementation of the IBarcodeRepository interface.
    This repository is used to store barcode results in memory for temporary
    storage and testing purposes. It maintains a list of barcodes and provides
    methods to save new barcodes.
    Attributes:
        db (list): A list that acts as the in-memory database for storing barcode results.
    """
    def __init__(self):
        self.db = []

    def save(self, barcode: BarcodeResult) -> bool:
        self.db.append(barcode)
        print(f"[Repo] Saved barcode: {barcode.content}")
        return True
    