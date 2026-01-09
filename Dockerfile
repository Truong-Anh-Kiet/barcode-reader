############################
# 1️⃣ BUILD STAGE
############################
FROM python:3.11-slim AS builder

WORKDIR /app

# System deps để build opencv, zxing
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency metadata
COPY pyproject.toml .

# Install uv
RUN pip install --no-cache-dir uv

# Create venv
RUN uv venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install python dependencies
RUN uv pip install -e .

############################
# 2️⃣ RUNTIME STAGE
############################
FROM python:3.11-slim

WORKDIR /app

# Runtime deps only (nhẹ hơn)
RUN apt-get update && apt-get install -y \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Copy venv từ builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy source code
COPY src ./src

EXPOSE 8000

# Run FastAPI
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
