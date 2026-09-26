# 🏛️ SkyGuard AI - System Architecture Document

```
+-----------------------------------------------------------------------------------+
|                           ESP32 / EDGE LAYER                                     |
|  1. Sensor Read (T, P, RH)                                                        |
|  2. Hard Range & Plausibility Validation                                          |
|  3. Lightweight Magnus Dew Point & VPD Physics Engine                             |
|  4. Temporal EWMA & Stuck Pin Detection                                           |
|  5. Compact Tree Decision Classifier & 1D Kalman Self-Healer                      |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          | Transmit (HTTP / MQTT / Telemetry)
                                          v
+-----------------------------------------------------------------------------------+
|                        CLOUD & SERVER ENGINE (Python)                             |
|  6. INGESTION & DATA PROVENANCE (IMD AWS, NOAA ISD, ERA5 Ref, Synthetic)          |
|  7. DETERMINISTIC THERMODYNAMICS (Bolton, Alduchov & Eskridge, Poisson Theta)    |
|  8. TEMPORAL & DIURNAL CYCLES (Harmonic Solar Baselines, Rolling Statistics)      |
|  9. MULTIVARIATE & MAHALANOBIS (Joint T-P-RH Covariance & Coherence)              |
| 10. SPATIAL CORROBORATION (Neighbor Consensus & Graceful Degradation)             |
| 11. MULTI-CLASS LIGHTGBM CLASSIFIER (8 Fault & Extreme Weather Classes)          |
| 12. TREESHAP & DIAGNOSTIC EXPLAINABILITY (Physical Rules + Mathematical XAI)      |
| 13. STATE-SPACE KALMAN FILTER SELF-HEALING (Raw Data Preserved)                  |
| 14. 0-100 SENSOR HEALTH & DEGRADATION TRACKER (Predictive Maintenance Risk)       |
+-----------------------------------------+-----------------------------------------+
                                          |
                     +--------------------+--------------------+
                     |                                         |
                     v                                         v
+-----------------------------------------+ +-----------------------------------------+
|     REST API & WEBSOCKET ENGINE         | |     10-VIEW OPERATIONAL DASHBOARD       |
|  FastAPI Endpoints + WebSocket /ws/live | |  Interactive Dark-Themed UI (Chart.js) |
+-----------------------------------------+ +-----------------------------------------+
```
