"""
This module initializes the FastAPI application for the Clean Barcode API.

It sets up the necessary dependencies, creates database tables on startup,
and starts the server using Uvicorn.
"""

import sys
import os
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from infrastructure.database import engine, Base
from infrastructure.cloudinary_storage import configure_cloudinary
from presentation.api import router as barcode_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

@asynccontextmanager
async def lifespan(_app: FastAPI):
    """
    Manages the lifespan of the FastAPI application.

    Handles startup (create database tables) and shutdown events.

    Args:
        _app (FastAPI): The FastAPI app instance.

    Yields:
        None
    """
    # Startup:
    configure_cloudinary()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown: (add cleanup if needed, e.g., close connections)

app = FastAPI(
    title="Clean Barcode API",
    description="API for scanning barcodes using Clean Architecture principles.",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(barcode_router, prefix="/barcodes", tags=["barcodes"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "your-frontend-url.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """
    Handles the root endpoint of the API.

    Provides a simple message to confirm the API is running.

    Returns:
        dict: A dictionary containing a status message.
    """
    return {"message": "Barcode Scanner API is running. Go to /docs for API documentation."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
    