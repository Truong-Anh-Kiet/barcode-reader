"""
Infrastructure layer implementations for storage, image processing,
and barcode detection.
This package provides concrete implementations of interfaces defined
in the domain layer, facilitating interactions with external systems
and services.
"""
from .detector_singleton import get_detector
from .cloudinary_storage import CloudinaryStorage
from .image_processor import OpenCVImageProcessor
from .repository import PostgresBarcodeRepository

__all__ = [
    "get_detector",
    "CloudinaryStorage",
    "OpenCVImageProcessor",
    "PostgresBarcodeRepository",
]