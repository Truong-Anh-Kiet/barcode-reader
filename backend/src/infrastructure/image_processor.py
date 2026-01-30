"""
Image preprocessing utilities using OpenCV for barcode detection optimization."""

from typing import Tuple

import cv2
import numpy as np

from domain.interfaces import IImageProcessor


class OpenCVImageProcessor(IImageProcessor):
    """Handles image preprocessing and cropping for barcode detection."""

    def process_image(self, image_data: bytes) -> Tuple[bytes, float]:
        """
        Preprocess image: resize (if needed), grayscale, CLAHE, blur.

        Returns:
            (processed_bytes, scale_factor): processed image bytes and factor to scale coordinates back to original.
        """
        img = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Invalid image data")

        original_h, original_w= img.shape[:2]
        max_dim = max(original_h, original_w)
        scale_factor = 1.0

        if max_dim > 1024:
            scale = 1024 / max_dim
            new_w, new_h = int(original_w * scale), int(original_h * scale)
            img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
            scale_factor = 1.0 / scale

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)

        blurred = cv2.GaussianBlur(enhanced, (3, 3), sigmaX=1.5, sigmaY=1.5)

        _, encoded = cv2.imencode('.jpg', blurred, [cv2.IMWRITE_JPEG_QUALITY, 95])
        return encoded.tobytes(), scale_factor

    def crop_region(self, image_data: bytes, bounding_box: Tuple[int, int, int, int]) -> bytes:
        """
        Crops a specific region from the image based on bounding box.

        Args:
            image_data (bytes): Raw binary data of the image.
            bounding_box (Tuple[int, int, int, int]): (x, y, width, height).

        Returns:
            bytes: Cropped image data (JPEG encoded).

        Raises:
            ValueError: If image decoding fails or bounding box is invalid.
        """
        img = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Invalid image data")
        
        x, y, w, h = bounding_box

        y_start = max(0, y)
        y_end = min(img.shape[0], y + h)
        x_start = max(0, x)
        x_end = min(img.shape[1], x + w)

        cropped = img[y_start:y_end, x_start:x_end]
        _, encoded = cv2.imencode('.jpg', cropped)
        return encoded.tobytes()

    