"""
This module contains the implementation of a barcode detector using pyzbar library.

The PyzbarDetector class provides functionality to detect and decode barcodes from
images represented as byte arrays. It returns the results as a list of BarcodeResult objects.
"""

from typing import List

import cv2
import numpy as np
import zxingcpp
from ultralytics import YOLO

from domain.entities import BarcodeResult
from domain.interfaces import IBarcodeDetector


class YOLOV8BarcodeDetector(IBarcodeDetector):
    """
    A barcode detector implementation using YOLOv8 (detection bounding box) + ZXing-cpp (decode content & type).
    Model: Piero2411/YOLOV8s-Barcode-Detection from Hugging Face
    """

    def __init__(self, conf_threshold: float = 0.25):
        self.model = YOLO("Piero2411/YOLOV8s-Barcode-Detection")
        self.conf_threshold = conf_threshold
        print("YOLOv8 Barcode model loaded successfully.")

    def detect(self, image_bytes: bytes) -> List[BarcodeResult]:
        """
        Detects barcodes in the given image bytes using YOLOv8 + ZXing-cpp.

        Args:
            image_bytes (bytes): Raw binary data of the image.

        Returns:
            List[BarcodeResult]: List of detected barcode results.
        """
        # Decode bytes to OpenCV image (BGR format)
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            print("OpenCV could not decode the image!")
            return []

        # pyzbar works directly with the BGR image
        results = self.model(img, conf=self.conf_threshold, iou=0.45, verbose=False)[0]

        if len(results.boxes) == 0:
            print("YOLOv8: No barcode detected.")
            return []
        
        barcode_results: List[BarcodeResult] = []

        for box in results.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            w = x2 - x1
            h = y2 - y1
            
            if w <= 0 or h <= 0:
                continue
            
            # Crop region
            cropped_img = img[y1:y2, x1:x2]

            zx_result = zxingcpp.read_barcode(cropped_img)
            
            if zx_result.valid:
                content = zx_result.text
                barcode_type = zx_result.format.name  # e.g., 'QR_CODE', 'EAN_13', 'CODE_128'
                
                barcode_results.append(BarcodeResult(
                    content=content,
                    barcode_type=barcode_type,
                    bounding_box=(x1, y1, w, h)
                ))
            else:
                continue
        
        # Remove duplicates dựa trên content
        unique_results = {res.content: res for res in barcode_results}.values()
        
        print(f"YOLOv8 + ZXing-cpp detected {len(unique_results)} unique barcode(s)")
        return list(unique_results)