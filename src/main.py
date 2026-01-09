from fastapi import FastAPI
import cv2
import zxingcpp

app = FastAPI()

@app.get("/")
def health():
    return {"status": "barcode backend ready"}
