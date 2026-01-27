"""
    Domain layer: Core business logic and entities.

    This package contains the core domain entities and interfaces
    that define the business rules and data structures.
"""
from .entities import BarcodeResult
from .interfaces import IBarcodeDetector, IBarcodeRepository, IImageStorage, IImageProcessor

__all__ = [
    "BarcodeResult",
    "IBarcodeDetector",
    "IBarcodeRepository",
    "IImageStorage",
    "IImageProcessor",
]