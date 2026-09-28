# Changelog

## v1.0.0-MVP (Current Status)

### Completed
- Data ingestion pipeline (Adapters for IMD, NOAA, ERA5, Synthetic)
- Data quality pipeline (WMO bounds, unit standardization, sentinel removal)
- Physics feature engine (Magnus-Tetens Dew Point, Vapor Pressure Deficit, Potential Temperature)
- 26-mode anomaly simulation & Extreme Weather injector
- Supervised Multi-Class LightGBM classifier (8 operational classes)
- Temporal analysis engine (Rolling stats, EWMA, diurnal cycles)
- Multivariate coherence analysis (T-P-RH Mahalanobis distances)
- Spatial corroboration engine (Neighbor consensus)
- Unified Evidence Fusion Layer
- TreeSHAP explainability engine for diagnostic reasoning
- 1D/3D State-Space Kalman filter for self-healing & imputation
- Continuous Sensor Health Index tracking
- High-throughput streaming and replay simulation engine
- FastAPI REST API & WebSocket server
- 10-view interactive Operational Dashboard
- ESP32 pure C99 edge code generation
- Rigorous evaluation suite (19/19 tests, 12 controlled experiments)
- Docker deployment support

### In Progress
- Continuous tuning of LightGBM model hyperparameters
- Dashboard enhancements for mobile responsiveness
- Further optimization of edge memory footprint

### Future Work
- Field validation (Deployment and physical testing on actual IMD AWS hardware)
- Integration with live national meteorological networks
- Advanced long-term anomaly pattern mining across seasonal cycles
- Battery autonomy field testing
