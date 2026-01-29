"""
Infrastructure layer: Cloudinary storage implementation.

Provides methods to upload and delete images using Cloudinary cloud storage service,
following the dependency inversion principle by implementing IImageStorage interface.
"""

import os
import uuid
import logging

import cloudinary
import cloudinary.uploader
from cloudinary.exceptions import Error as CloudinaryError
from typing import Tuple

from domain.interfaces import IImageStorage

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def configure_cloudinary():
    """
    Configure Cloudinary SDK once at application startup.
    Call this function in main.py (lifespan startup) or at module level if needed.
    """

    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
    api_key = os.getenv("CLOUDINARY_API_KEY")
    api_secret = os.getenv("CLOUDINARY_API_SECRET")

    if not all([cloud_name, api_key, api_secret]):
        raise ValueError(
            "Missing Cloudinary credentials in environment variables. "
            "Please set CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, and CLOUDINARY_API_SECRET "
            "in your .env file or environment."
        )

    try:
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
            secure=True
        )
        logger.info("Cloudinary configured successfully")
    except Exception as e:
        logger.error(f"Failed to configure Cloudinary: {str(e)}")
        raise


class CloudinaryStorage(IImageStorage):
    """
    Cloudinary implementation of the image storage service.

    Handles uploading image bytes to Cloudinary and deleting images by public_id.
    Configuration should be done once via configure_cloudinary() at app startup.
    """

    def __init__(self):
        """
        Initialize the storage service.
        Ensures Cloudinary is configured (fallback check).
        """
        if not cloudinary.config().cloud_name:
            logger.warning("Cloudinary not configured yet. Attempting fallback config.")
            configure_cloudinary()

    def upload_image(self, image_data: bytes, filename: str, user_id: int) -> Tuple[str, str]:
        """
        Uploads image data to Cloudinary and returns the secure public URL.

        - Generates a unique public_id using UUID + sanitized filename.
        - Uploads to folder "barcodes".
        - Prevents overwrite by using unique_filename=True.

        Args:
            image_data (bytes): Raw binary data of the image.
            filename (str): Original filename (used to generate readable public_id).

        Returns:
            str: Secure HTTPS URL of the uploaded image.

        Raises:
            ValueError: If upload fails or input invalid.
        """
        if not image_data or len(image_data) == 0:
            raise ValueError("Image data cannot be empty")

        base_name = filename.rsplit('.', 1)[0] if '.' in filename else filename
        safe_name = "".join(c for c in base_name if c.isalnum() or c in ['-', '_']).strip('_-')

        unique_part = uuid.uuid4().hex[:10]
        public_id = f"barcodes/user_{user_id}/{unique_part}_{safe_name[:40]}"
        try:
            result = cloudinary.uploader.upload(
                image_data,
                resource_type="image",
                public_id=public_id,
                overwrite=False,
                unique_filename=True,
                allowed_formats=["jpg", "jpeg", "png", "webp", "gif"],
                tags=["barcode-scanner", "auto"],
            )
            secure_url = result.get("secure_url")
            public_id = result["public_id"]
            if not secure_url:
                raise ValueError("No secure_url returned from Cloudinary")
            
            logger.info(f"Uploaded image: {public_id} → {secure_url}")
            return secure_url, public_id

        except CloudinaryError as e:
            logger.error(f"Cloudinary upload error for {filename}: {str(e)}")
            raise ValueError(f"Failed to upload to Cloudinary: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during upload {filename}: {str(e)}")
            raise ValueError(f"Upload failed: {str(e)}")

    def delete_image(self, public_id: str) -> bool:
        """
        Deletes an image from Cloudinary using its full public_id.

        Args:
            public_id (str): Full public ID (e.g., "barcodes/abc123_myfile").

        Returns:
            bool: True if deletion was successful, False if not found or failed.
        """
        if not public_id:
            logger.warning("Empty public_id provided for delete")
            return False

        try:
            result = cloudinary.uploader.destroy(
                public_id,
                resource_type="image"
            )
            success = result.get("result") == "ok"
            if success:
                logger.info(f"Deleted image: {public_id}")
            else:
                logger.warning(f"Delete result not 'ok' for {public_id}: {result}")
            return success

        except CloudinaryError as e:
            logger.warning(f"Cloudinary delete failed for {public_id}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected delete error for {public_id}: {str(e)}")
            return False