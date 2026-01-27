"""Singleton pattern implementation for YOLOV8BarcodeDetector."""

from infrastructure.detector import YOLOV8BarcodeDetector
from typing import Final

_DETECTOR: Final[YOLOV8BarcodeDetector] = YOLOV8BarcodeDetector(conf_threshold=0.3)

def get_detector() -> YOLOV8BarcodeDetector:
    return _DETECTOR