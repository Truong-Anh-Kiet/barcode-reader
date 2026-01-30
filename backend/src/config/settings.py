"""
Central configuration using Pydantic for environment variables.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str
    SMTP_USER: str
    SMTP_PASSWORD: str
    FROM_EMAIL: str
    SMTP_PORT: int = 587
    SMTP_HOST: str
    YOLO_MODEL_PATH: str = "src/assets/models/YOLOV8s_Barcode_Detection.pt"
    FRONTEND_URLS: str = "http://localhost:3000,http://localhost:5173"
    
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

settings = Settings()