# SkyGuard AI - Production Multi-Stage Dockerfile (SIH26073)
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000

# Install system dependencies including OpenMP for LightGBM
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install python packages
COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=1000 --retries 10 -r requirements.txt

# Copy application source code and configurations
COPY skyguard/ /app/skyguard/
COPY configs/ /app/configs/
COPY dashboard/ /app/dashboard/
COPY references/ /app/references/
COPY docs/ /app/docs/
COPY evaluation/ /app/evaluation/
COPY experiments/ /app/experiments/
COPY tests/ /app/tests/

# Pre-train and persist master model if not already present
RUN python -c "from skyguard.models.trainer import ModelTrainer; trainer = ModelTrainer(); trainer.train_and_persist(n_days=15)"

# Expose API and Web Dashboard Port
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/metrics || exit 1

# Start FastAPI and WebSocket Live Stream server
CMD ["uvicorn", "skyguard.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
