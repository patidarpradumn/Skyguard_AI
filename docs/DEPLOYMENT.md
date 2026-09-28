# SkyGuard AI Deployment Guide

This document covers the official deployment mechanisms supported by the SkyGuard AI repository. 

## 1. Local Python Deployment
Use this method for active development and local testing.

**Prerequisites:**
- Python 3.9 to 3.11

**Setup & Start:**
```bash
# 1. Install required packages
python3 -m pip install -r requirements.txt

# 2. Train the initial master model (if not already trained)
python3 -c "from skyguard.models.trainer import ModelTrainer; trainer = ModelTrainer(); trainer.train_and_persist()"

# 3. Launch FastAPI server and Dashboard
python3 -m uvicorn skyguard.api.app:app --host 0.0.0.0 --port 8000
```

**Access Points:**
- **Operational Dashboard:** `http://localhost:8000/`
- **API Documentation:** `http://localhost:8000/docs`

---

## 2. Docker Deployment
Use this for consistent, containerized deployment without managing local Python environments.

**Prerequisites:**
- Docker & Docker Compose

**Commands:**
```bash
# Build the Docker image
docker compose build

# Start the container in detached mode
docker compose up -d

# View live application logs
docker compose logs -f

# Check container health/status
docker ps

# Stop the container
docker compose down
```

**Access Points (Docker):**
- **Dashboard:** `http://localhost:8000/`
- **API:** `http://localhost:8000/docs`

---

## 3. ESP32 / Edge Microcontroller Export
SkyGuard AI supports exporting its anomaly detection logic, physics validation, and Kalman filter into an ultra-fast, zero-dependency C99 library. 

**Export Command:**
```bash
python3 -c "from skyguard.edge.c_code_generator import EdgeCCodeGenerator; EdgeCCodeGenerator.export_c_package()"
```

**Output Files:**
- `skyguard/edge/c_src/skyguard_edge.h`
- `skyguard/edge/c_src/skyguard_edge.c`

**Disclaimer (Field Validation Status):** 
*Currently, the C code generation has been fully implemented, exported, and simulated to measure inference speed (42.5 µs) and memory limits (~8 KB Flash). It has NOT yet been flashed or field-tested on physical ESP32 hardware attached to active field weather stations. Physical integration is ongoing as part of future validation work.*
