"""
Infrastructure layer: Cloudinary storage implementation.

Provides methods to upload and delete images using Cloudinary cloud storage service,
following the dependency inversion principle by implementing IImageStorage interface.
"""

import os
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

from domain.interfaces import IImageStorage


class CloudinaryStorage(IImageStorage):
    """
    Cloudinary implementation of the image storage service.

    This class handles uploading image bytes to Cloudinary and deleting images by public_id.
    It loads configuration from environment variables for security.

    Attributes:
        None (configuration is loaded during initialization).
    """

    def __init__(self):
        """
        Initializes the Cloudinary configuration.

        Loads credentials from environment variables (.env file) and sets up secure connection.
        Raises ValueError if required environment variables are missing.
        """
        load_dotenv()

        cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
        api_key = os.getenv("CLOUDINARY_API_KEY")
        api_secret = os.getenv("CLOUDINARY_API_SECRET")

        if not all([cloud_name, api_key, api_secret]):
            raise ValueError(
                "Missing Cloudinary credentials in environment variables. "
                "Please set CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, and CLOUDINARY_API_SECRET."
            )

        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
            secure=True
        )

    def upload_image(self, image_data: bytes, filename: str) -> str:
        """
        Uploads image data to Cloudinary and returns the secure public URL.

        The image is stored in the 'barcodes' folder with public_id derived from the filename
        (without extension). Uses 'image' resource type.

        Args:
            image_data (bytes): Raw binary data of the image to upload.
            filename (str): Original filename (used to generate public_id).

        Returns:
            str: Secure HTTPS URL of the uploaded image.

        Raises:
            cloudinary.exceptions.Error: If upload fails due to network/API issues.
            ValueError: If image_data is invalid or empty.
        """
        if not image_data:
            raise ValueError("Image data cannot be empty")

        public_id = filename.rsplit('.', 1)[0] if '.' in filename else filename

        result = cloudinary.uploader.upload(
            image_data,
            resource_type="image",
            public_id=public_id,
            folder="barcodes",
            overwrite=True,
            unique_filename=False
        )

        return result["secure_url"]

    def delete_image(self, public_id: str) -> bool:
        """
        Deletes an image from Cloudinary using its public_id.

        Args:
            public_id (str): The public ID of the image to delete (without folder prefix).

        Returns:
            bool: True if deletion was successful, False otherwise.

        Raises:
            cloudinary.exceptions.Error: If deletion fails due to invalid public_id or API error.
        """
        if not public_id:
            return False

        result = cloudinary.uploader.destroy(public_id)

        return result.get("result") == "ok"
    