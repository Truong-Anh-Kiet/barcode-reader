"""
Presentation layer: API endpoints and request/response handling.
This package defines the FastAPI routes and integrates with the application layer
to handle barcode scanning and retrieval operations.
"""
from .api import router as barcode_router

__all__ = ["barcode_router"]