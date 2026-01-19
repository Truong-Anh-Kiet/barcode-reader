# =====================================
# Bước 1: Builder stage (dùng uv để install dependencies)
# =====================================
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim AS builder

# Cài build tools nếu có package cần compile (thường không cần cho pyzbar + opencv-python)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy file cấu hình dependency trước để tận dụng Docker cache
COPY pyproject.toml uv.lock ./

# Install dependencies vào .venv (không dev, không project code)
RUN uv sync --frozen --no-dev --no-install-project

# =====================================
# Bước 2: Runtime stage (image cuối cùng - nhỏ gọn)
# =====================================
FROM python:3.11-slim-bookworm

# Cài các thư viện hệ thống cần thiết
# - libzbar0: bắt buộc cho pyzbar
# - libgl1 + libglib2.0-0: cho OpenCV (cv2)
# - libjpeg62-turbo + libpng16-16: thường cần cho xử lý ảnh
RUN apt-get update && apt-get install -y --no-install-recommends \
    libzbar0 \
    libzbar-dev \
    libjpeg62-turbo \
    libpng16-16 \
    libtiff6 \
    libwebp7 \
    libfreetype6 \
    libfontconfig1 \
    libiconv-hook1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgl1-mesa-glx \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /app

# Copy virtual environment từ builder
COPY --from=builder /app/.venv /app/.venv

# Copy toàn bộ source code
COPY . .

# Thiết lập PATH để dùng python/uv từ venv
ENV PATH="/app/.venv/bin:$PATH"

# Thêm PYTHONPATH để import từ src/ (nếu project dùng sys.path.insert như main.py)
ENV PYTHONPATH=/app:/app/src

# Expose port FastAPI
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
# Hoặc thêm workers nếu cần: --workers 4