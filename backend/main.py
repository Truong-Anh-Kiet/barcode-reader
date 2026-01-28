"""
This module initializes the FastAPI application for the Clean Barcode API.

It sets up the necessary dependencies, creates database tables on startup,
and starts the server using Uvicorn.
"""

import sys
import os
import logging

from dotenv import load_dotenv

load_dotenv()
logging.info(".env file loaded successfully")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from infrastructure.database import engine, Base
from infrastructure.cloudinary_storage import configure_cloudinary
from presentation.api import router as barcode_router
from fastapi.staticfiles import StaticFiles

from application.auth import fastapi_users,auth_backend, current_superuser

from application.schemas import UserRead, UserCreate, UserUpdate

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_cloudinary()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(
    title="Clean Barcode API",
    description="API for scanning barcodes using Clean Architecture principles.",
    version="1.0.0",
    lifespan=lifespan
)

app.mount("/static",
          StaticFiles(directory="src/static"),
          name="static")

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"]
)

app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"]
)

app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(current_superuser)]
)

app.include_router(
    barcode_router,
    prefix="/barcodes",
    tags=["barcodes"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "your-frontend-url.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Barcode Scanner API is running. Go to /docs for API documentation."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)