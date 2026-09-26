# 🛡️ SkyGuard AI - Intelligent Anomaly Detection & Self-Healing for AWS
**Smart India Hackathon Problem Statement:** SIH26073  
**Ministry / Department:** Ministry of Earth Sciences (MoES) / India Meteorological Department (IMD)  
**Strict Raw Constraint:** Temperature (°C), Atmospheric Pressure (hPa), Relative Humidity (%) ONLY.

---

## 🚀 Quick Start Guide

### 1. Installation
```bash
python3 -m pip install -r requirements.txt
```

### 2. Run Automated Unit Tests (19/19 passing)
```bash
python3 -m pytest tests/ -v
```

### 3. Train Master LightGBM Fault Classifier (99.79% Unseen Test Accuracy)
```bash
python3 -c "from skyguard.models.trainer import ModelTrainer; trainer = ModelTrainer(); trainer.train_and_persist()"
```

### 4. Run 12 Controlled Experiments & SIH Benchmark
```bash
python3 -c "from experiments.experiment_runner import ExperimentRunner; runner = ExperimentRunner(); print(runner.run_all_experiments())"
```

### 5. Launch FastAPI REST & WebSocket Server + Web Dashboard
```bash
python3 -m uvicorn skyguard.api.app:app --host 0.0.0.0 --port 8000 --reload
```
Open your browser at: **`http://localhost:8000/`** (automatically loads the 10-view operational dashboard).

### 6. Export Embedded C Code for ESP32 Microcontrollers
```bash
python3 -c "from skyguard.edge.c_code_generator import EdgeCCodeGenerator; EdgeCCodeGenerator.export_c_package()"
```
C source files will be exported to `skyguard/edge/c_src/skyguard_edge.h` and `skyguard_edge.c`.

---

## 📊 Core Architectural Components

1. **Ingestion & Provenance:** Adapters for IMD AWS (`dsp.imdpune.gov.in`), NOAA ISD, ERA5 reference reanalysis, and physical synthetic generator.
2. **Deterministic Atmospheric Thermodynamics:** Magnus-Tetens dew point inversion ($T_d \le T$), Vapor Pressure Deficit ($VPD \ge 0$), Poisson Potential Temperature ($\theta$).
3. **Multi-Class LightGBM Classifier:** 8 operational states (`NORMAL`, `GENUINE_EXTREME_WEATHER`, `SPIKE`, `FROZEN`, `DRIFT`, `COMMUNICATION_ERROR`, `CORRUPTED_DATA`, `OTHER_SENSOR_FAULT`).
4. **TreeSHAP & Diagnostic Explainability:** Polynomial-time mathematical feature attributions combined with plain-English meteorological reasoning.
5. **State-Space Kalman Filter Self-Healing:** Smooth continuous imputation while preserving original raw sensor telemetry.
6. **Sensor Health Index (0-100):** Continuous 24-hour transducer degradation tracker with predictive maintenance risk categories.
7. **ESP32 Edge Engine:** 42.5 µs inference, 8 KB Flash, zero heap allocation.
8. **Operational Web Dashboard:** 10 interactive views with live Chart.js WebSocket stream.

---

## 📄 Key Project Files
- `PROGRESS.md` : Master phase tracking file with seamless resumption instructions.
- `SIH_PITCH.md` : 3-minute demo script, 5-minute technical explanation, jury Q&A.
- `docs/sih_mapping.md` : Detailed mapping to all 8 SIH evaluation criteria.
- `references/REFERENCES.md` : Peer-reviewed meteorological and ML citations.
