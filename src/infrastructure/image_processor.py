"""
Infrastructure layer: Image processing implementation using OpenCV.

Provides methods to preprocess and post-process images for barcode detection,
implementing the IImageProcessor interface. Includes full pipeline for optimal detection.
"""

from typing import List, Tuple

import cv2
import numpy as np

from domain.entities import BarcodeResult
from domain.interfaces import IBarcodeDetector, IImageProcessor


class OpenCVImageProcessor(IImageProcessor):
    """
    OpenCV implementation for image processing in the barcode pipeline.

    Handles ingestion, preprocessing (resize, grayscale, contrast, noise reduction,
    thresholding, edge detection, perspective fix), multi-scale detection, and cropping.
    """

    def process_image(self, image_data: bytes) -> bytes:
        """
        Full preprocessing pipeline to optimize image for barcode detection.

        Steps:
        1. Ingestion: Convert bytes to NumPy array.
        2. Resize: Scale to max 1024px for performance.
        3. Grayscale: Convert to 8-bit grayscale.
        4. Contrast Enhancement: Apply CLAHE for better visibility.
        5. Noise Reduction: Gaussian Blur to remove high-frequency noise.
        6. Adaptive Thresholding: Binarize to handle shadows/lighting.
        7. Edge Detection: Canny to highlight barcode edges.
        8. Perspective Fix: Detect contours and straighten tilted barcodes.

        Args:
            image_data (bytes): Raw binary data of the image.

        Returns:
            bytes: Processed image data (JPEG encoded).
        """
        # # 1. Ingestion: Bytes to NumPy array
        # img = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)
        # if img is None:
        #     raise ValueError("Invalid image data")

        # # 2. Resize
        # h, w = img.shape[:2]
        # if max(h, w) > 1024:
        #     scale = 1024 / max(h, w)
        #     img = cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)

        # # 3. Grayscale
        # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # # 4. Contrast Enhancement
        # clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        # enhanced = clahe.apply(gray)

        # # 5. Noise Reduction: Gaussian Blur
        # blurred = cv2.GaussianBlur(enhanced, (5, 5), 0)

        # # 6. Adaptive Thresholding
        # binary = cv2.adaptiveThreshold(
        #     blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        # )

        # # 7. Edge Detection
        # edges = cv2.Canny(binary, 50, 150)

        # # 8. Perspective Fix: Detect contours and warp
        # contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # if contours:
        #     largest_contour = max(contours, key=cv2.contourArea)
        #     if len(largest_contour) >= 4:
        #         rect = cv2.minAreaRect(largest_contour)
        #         box = cv2.boxPoints(rect)
        #         box = np.intp(box)

        #         # Warp perspective to straighten
        #         width, height = int(rect[1][0]), int(rect[1][1])
        #         src_pts = box.astype("float32")
        #         dst_pts = np.array([[0, height-1],[0, 0], [width-1, 0], [width-1, height-1]],
        #                            dtype="float32")
        #         perspective_matrix = cv2.getPerspectiveTransform(src_pts, dst_pts)
        #         warped = cv2.warpPerspective(img, perspective_matrix, (width, height))

        #         # Convert warped back to grayscale/binary if needed
        #         processed_img = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
        #     else:
        #         processed_img = edges
        # else:
        #     processed_img = edges

        # # Encode back to bytes
        # _, encoded = cv2.imencode('.jpg', processed_img)
        # return encoded.tobytes()
        return image_data

    def crop_region(self, image_data: bytes, bounding_box: Tuple[int, int, int, int]) -> bytes:
        """
        Crops a specific region from the image based on bounding box.

        Args:
            image_data (bytes): Raw binary data of the image.
            bounding_box (Tuple[int, int, int, int]): (x, y, width, height)

        Returns:
            bytes: Cropped image data as bytes.
        """
        img = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("Invalid image data")

        x, y, w, h = bounding_box
        cropped = img[y:y+h, x:x+w]

        # Encode back to bytes
        _, encoded = cv2.imencode('.jpg', cropped)
        return encoded.tobytes()

    def multi_scale_detect(self,
                           processed_data: bytes,
                           detector: IBarcodeDetector) -> List[BarcodeResult]:
        """
        Performs detection at multiple scales to handle small/large barcodes.

        Scales: 0.5x, 1x, 1.5x; merges unique results.

        Args:
            processed_data (bytes): Preprocessed image data.
            detector (IBarcodeDetector): The detector to use.

        Returns:
            List[BarcodeResult]: Merged detection results.
        """
        img = cv2.imdecode(np.frombuffer(processed_data, np.uint8), cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise ValueError("Invalid processed data")

        results = []
        for scale in [0.5, 1.0, 1.5]:
            scaled_img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
            _, encoded_scaled = cv2.imencode('.jpg', scaled_img)
            scaled_results = detector.detect(encoded_scaled.tobytes())

            # Adjust bounding_box back to original scale
            for res in scaled_results:
                x, y, w, h = res.bounding_box
                res.bounding_box = (int(x / scale), int(y / scale), int(w / scale), int(h / scale))
            results.extend(scaled_results)

        # Remove duplicates (simple: based on content)
        unique_results = {res.content: res for res in results}.values()
        return list(unique_results)
    