# SkyGuard AI - Evaluation Results

This directory contains the automated evaluation artifacts generated directly from the SkyGuard AI project's `experiments/` pipeline and model outputs. 

## Dataset and Setup
The evaluation was run on a synthetic multi-station benchmark dataset simulating 30+ days of 15-minute resolution weather station data, including genuine extreme weather events (heatwaves, squalls) and injected anomalies across 26 different fault modes (spikes, drift, frozen sensors, communication errors).

- **Model Evaluated:** SkyGuardLightGBMClassifier
- **Input Features:** Temperature (°C), Pressure (hPa), Relative Humidity (%), plus derived physics invariants (Dew Point, VPD, Potential Temperature), temporal features, and spatial corroboration metrics.
- **Classes (8):** `NORMAL`, `GENUINE_EXTREME_WEATHER`, `SPIKE`, `FROZEN`, `DRIFT`, `COMMUNICATION_ERROR`, `CORRUPTED_DATA`, `OTHER_SENSOR_FAULT`.

## Results
- **Test Set Size:** 2875 samples (Unseen Temporal Holdout)
- **Overall Accuracy:** 99.79%
- **Evaluation Type:** Controlled Experiment / Unseen Test Set
- **Status:** These metrics reflect model-level performance in a controlled simulation environment. Field validation on real physical IMD AWS units is currently ongoing.

## Files
- `accuracy_metrics.json`: High-level metrics including Accuracy, Precision, Recall, and F1-Score.
- `confusion_matrix.png`: Multi-class confusion matrix on the unseen test set, demonstrating the model's ability to disentangle genuine extreme weather from sensor faults.
- `roc_curve.png`: Receiver Operating Characteristic (ROC) curve per class.
- `precision_recall_curve.png`: Precision-Recall curve per class.
- `test_predictions.csv`: A 100-sample preview of the model's predictions versus actual labels.

## Reproducibility
To regenerate these artifacts, run the evaluation script:
```bash
python3 generate_results.py
```
To run the full 12-experiment SIH Benchmark suite, use:
```bash
python3 -c "from experiments.experiment_runner import ExperimentRunner; r = ExperimentRunner(); print(r.run_all_experiments())"
```
