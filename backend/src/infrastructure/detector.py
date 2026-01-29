"""
This module contains the implementation of a barcode detector using pyzbar library.

The PyzbarDetector class provides functionality to detect and decode barcodes from
images represented as byte arrays. It returns the results as a list of BarcodeResult objects.
"""
import logging
from typing import List
from pathlib import Path

import cv2
import numpy as np
import zxingcpp
from ultralytics import YOLO

from domain.entities import BarcodeResult
from domain.interfaces import IBarcodeDetector

logger = logging.getLogger(__name__)

class YOLOV8BarcodeDetector(IBarcodeDetector):
    """
    A barcode detector implementation using YOLOv8 (detection bounding box) + ZXing-cpp (decode content & type).
    Model: Piero2411/YOLOV8s-Barcode-Detection from Hugging Face
    """

    def __init__(self, conf_threshold: float = 0.3):
        base_dir = Path(__file__).resolve().parents[2]
        model_path = base_dir / "src" / "models" / "YOLOV8s_Barcode_Detection.pt"

        if not model_path.exists():
            raise FileNotFoundError(f"YOLO model not found at {model_path}")
        self.model = YOLO(str(model_path))
        self.conf_threshold = conf_threshold

        logger.info("YOLOv8 Barcode model loaded successfully.")

    def detect(self, image_bytes: bytes) -> List[BarcodeResult]:
        """
        Detects barcodes in the given image bytes using YOLOv8 + ZXing-cpp.

        Args:
            image_bytes (bytes): Raw binary data of the image.

        Returns:
            List[BarcodeResult]: List of detected barcode results.
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

            x1 = max(0, min(x1, W - 1))
            y1 = max(0, min(y1, H - 1))
            x2 = max(0, min(x2, W))
            y2 = max(0, min(y2, H))

            if x2 <= x1 or y2 <= y1:
                continue
            
            ui_box = (x1, y1, x2, y2)

            crop = self._safe_crop(img, x1, y1, x2, y2)

            zx_results = self._decode_barcode(crop)

            if not zx_results:
                logger.debug(f"ZXing failed on box {i}")
                continue

            for zx in zx_results:
                if not zx.valid:
                    continue

                barcode_results.append(BarcodeResult(
                    content=zx.text,
                    barcode_type=zx.format.name,
                    bounding_box=ui_box,
                ))

        unique = {r.content: r for r in barcode_results}.values()
        
        logger.info(f"Detected {len(unique)} barcode(s)")
        return list(unique)

    def _safe_crop(self, img, x1, y1, x2, y2):
        """
        Crop with padding and boundary checks
        """
        pad = int(0.25 * max(x2 - x1, y2 - y1))

        h, w = img.shape[:2]
        x1p = max(0, x1 - pad)
        y1p = max(0, y1 - pad)
        x2p = min(w, x2 + pad)
        y2p = min(h, y2 + pad)

        return img[y1p:y2p, x1p:x2p]

    def _decode_barcode(self, crop_bgr):
        """
        Try multiple preprocessing strategies to decode barcode using ZXing-cpp.
        """

        results = zxingcpp.read_barcodes(
            crop_bgr,
            try_rotate=True,
            try_downscale=False,
        )
        if results:
            return results

        gray = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2GRAY)
        results = zxingcpp.read_barcodes(
            gray,
            try_rotate=True,
            try_downscale=False,
        )
        if results:
            return results

        _, bw = cv2.threshold(
            gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
        results = zxingcpp.read_barcodes(
            bw,
            try_rotate=True,
            try_downscale=False,
        )
        if results:
            return results

        warped = self._try_perspective(gray)
        if warped is not None:
            results = zxingcpp.read_barcodes(
                warped,
                try_rotate=True,
                try_downscale=False,
            )
            if results:
                return results

        return []

    def _try_perspective(self, gray):
        """
        Try to correct perspective distortion to help barcode decoding.
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
        img = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)

        for r in results:
            x, y, w, h = r.bounding_box
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(
                img,
                f"{r.barcode_type}: {r.content}",
                (x, max(0, y - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                15,
            )

        _, encoded = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 90])
        return encoded.tobytes()

    
