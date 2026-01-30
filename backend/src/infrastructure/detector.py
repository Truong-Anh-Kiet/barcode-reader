"""
Infrastructure layer: Barcode detection implementation.

This module provides a barcode detector using YOLOv8 for bounding box detection
and ZXing-cpp for decoding. It implements the IBarcodeDetector interface from
the domain layer, following the dependency inversion principle.
"""

import logging
from typing import List, Final
from pathlib import Path

import cv2
import numpy as np
import zxingcpp
from ultralytics import YOLO

from domain.entities import BarcodeResult
from domain.interfaces import IBarcodeDetector

from config.settings import settings

logger = logging.getLogger(__name__)

class YOLOV8BarcodeDetector(IBarcodeDetector):
    """
    Barcode detector using YOLOv8 for bounding box detection and ZXing-cpp for decoding.

    This class loads a pre-trained YOLOv8 model for detecting barcode regions,
    then decodes the content and type from cropped regions using ZXing.
    Supports multi-scale detection for better handling of varying barcode sizes.

    Attributes:
        model (YOLO): The loaded YOLOv8 model.
        conf_threshold (float): Confidence threshold for YOLO detections.
    """

    def __init__(self, conf_threshold: float = 0.3):
        """
        Initializes the detector with the YOLO model.

        Args:
            conf_threshold (float, optional): Minimum confidence for detections. Defaults to 0.3.

        Raises:
            FileNotFoundError: If the model file is not found.
        """
        model_path = Path(settings.YOLO_MODEL_PATH)

        if not model_path.exists():
            raise FileNotFoundError(f"YOLO model not found at {model_path}")
        self.model = YOLO(str(model_path))
        self.conf_threshold = conf_threshold
        logger.info("YOLOv8 Barcode model loaded successfully.")

    def detect(self, image_bytes: bytes) -> List[BarcodeResult]:
        """
        Detects barcodes in the given image bytes.

        Uses YOLO to find bounding boxes, then decodes each crop with ZXing.
        Optionally performs multi-scale detection for improved accuracy on varying sizes.

        Args:
            image_bytes (bytes): Raw binary data of the image.
            use_multi_scale (bool, optional): If True, detects at multiple scales. Defaults to False.

        Returns:
            List[BarcodeResult]: List of detected barcode results (unique by content).

        Raises:
            ValueError: If image decoding fails.
        """
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            logger.error("Cannot decode image!")
            return []
        
        H, W = img.shape[:2]

        results = self.model(img, conf=self.conf_threshold, iou=0.45, verbose=False)[0]

        if not results.boxes:
            logger.info("YOLOv8: No barcode detected.")
            return []
        
        barcode_results: List[BarcodeResult] = []

        for i, box in enumerate(results.boxes):
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            conf = float(box.conf.item())

            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(W, x2), min(H, y2)

            if x2 <= x1 or y2 <= y1:
                continue
            
            crop = self._safe_crop(img, x1, y1, x2, y2)
            zx_results = self._decode_barcode(crop)

            if not zx_results:
                logger.debug(f"ZXing failed on box {i}")
                continue

            for zx in zx_results:
                if not zx.valid:
                    continue
                
                bounding_box = (x1, y1, x2 - x1, y2 - y1)

                barcode_results.append(BarcodeResult(
                    content=zx.text,
                    barcode_type=zx.format.name,
                    bounding_box=bounding_box,
                    confidence=conf,
                ))

        unique = {r.content: r for r in barcode_results}.values()
        results_list = list(unique.values())
        
        logger.info(f"Detected {len(unique)} unique barcode(s)")
        return results_list

    def _safe_crop(self, img: np.ndarray, x1: int, y1: int, x2: int, y2: int) -> np.ndarray:
        """
        Crops the image with padding to include more context, ensuring boundaries.

        Args:
            img (np.ndarray): Image array.
            x1, y1, x2, y2 (int): Bounding box coordinates.

        Returns:
            np.ndarray: Cropped image region.
        """
        pad = int(0.25 * max(x2 - x1, y2 - y1))
        h, w = img.shape[:2]
        x1p = max(0, x1 - pad)
        y1p = max(0, y1 - pad)
        x2p = min(w, x2 + pad)
        y2p = min(h, y2 + pad)

        return img[y1p:y2p, x1p:x2p]

    def _decode_barcode(self, crop_bgr: np.ndarray) -> List[zxingcpp.Barcode]:
        """
        Attempts to decode barcode using multiple preprocessing strategies with ZXing.

        Strategies: raw RGB, grayscale, binary threshold, perspective correction.

        Args:
            crop_bgr (np.ndarray): Cropped BGR image.

        Returns:
            List[zxingcpp.Result]: Decoded results (may be empty).
        """

        strategies = [
            lambda: zxingcpp.read_barcodes(crop_bgr, try_rotate=True),
            lambda: zxingcpp.read_barcodes(cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2GRAY), try_rotate=True),
            lambda: zxingcpp.read_barcodes(
                cv2.threshold(cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2GRAY), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
                try_rotate=True
            ),
        ]

        for strategy in strategies:
            try:
                results = strategy()
                if results:
                    return results
            except Exception as e:
                logger.warning(f"ZXing strategy failed: {e}")

        warped = self._try_perspective(cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2GRAY))
        if warped is not None:
            try:
                results = zxingcpp.read_barcodes(warped, try_rotate=True)
                if results:
                    return results
            except Exception as e:
                logger.warning(f"ZXing warped failed: {e}")

        return []

    def _try_perspective(self, gray: np.ndarray) -> np.ndarray | None:
        """
        Attempts to correct perspective distortion for better decoding.

        Finds the largest quadrilateral contour and warps to rectangular.

        Args:
            gray (np.ndarray): Grayscale image.

        Returns:
            Optional[np.ndarray]: Warped image if successful, else None.
        """
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(
            edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        if not contours:
            return None

        cnt = max(contours, key=cv2.contourArea)
        rect = cv2.minAreaRect(cnt)
        box = cv2.boxPoints(rect)
        box = np.int32(box)

        w, h = int(rect[1][0]), int(rect[1][1])
        if w < 50 or h < 50:
            return None

        dst = np.array(
            [[0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]],
            dtype="float32",
        )

        M = cv2.getPerspectiveTransform(box.astype("float32"), dst)
        warped = cv2.warpPerspective(gray, M, (w, h))

        return warped
    
    def draw_boxes(self, image_bytes: bytes, results: list[BarcodeResult]) -> bytes:
        """
        Draws bounding boxes and labels on the image.

        Args:
            image_bytes (bytes): Original image bytes.
            results (List[BarcodeResult]): Detection results.

        Returns:
            bytes: Image with boxes drawn (JPEG encoded).

        Raises:
            ValueError: If image decoding fails.
        """
        img = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Invalid image data")
        
        for r in results:
            x, y, bw, bh = r.bounding_box
            font_scale = max(0.6, min(1.2, bh / 100))
            thickness = max(2, int(bh / 150))

            cv2.rectangle(img, (x, y), (x + bw, y + bh), (0, 255, 0), thickness)
            label = f"{r.barcode_type}: {r.content} ({r.confidence:.2f})"
            cv2.putText(
                img,
                label,
                (x, max(0, y - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                font_scale,
                (0, 255, 0),
                thickness + 1,
            )

        _, encoded = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 92])
        return encoded.tobytes()

_DETECTOR: Final[YOLOV8BarcodeDetector] = YOLOV8BarcodeDetector()

def get_detector() -> YOLOV8BarcodeDetector:
    return _DETECTOR
    
