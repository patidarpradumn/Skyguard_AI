import os
import json
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
import matplotlib.pyplot as plt
from sklearn.preprocessing import label_binarize

from skyguard.models.trainer import ModelTrainer
from skyguard.models.lgbm_classifier import CLASS_MAP, REVERSE_CLASS_MAP

def main():
    results_dir = Path("/Volumes/T7/SIH/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    
    print("Initializing ModelTrainer...")
    trainer = ModelTrainer()
    
    print("Preparing dataset...")
    df = trainer.prepare_dataset(n_days=40)
    train_df, val_df, test_df = trainer.temporal_split(df)
    
    print("Training model...")
    trainer.model.fit(train_df, train_df["label"], val_data=(val_df, val_df["label"]))
    
    print("Running predictions on test set...")
    labels, preds_int, probs = trainer.model.predict(test_df)
    
    # We need integer labels for scikit-learn metrics
    if pd.api.types.is_numeric_dtype(test_df["label"]):
        y_true_int = test_df["label"].astype(int).values
    else:
        y_true_int = test_df["label"].astype(str).map(REVERSE_CLASS_MAP).fillna(7).astype(int).values
        
    y_pred_int = preds_int
    
    print("Calculating metrics...")
    acc = accuracy_score(y_true_int, y_pred_int)
    precision = precision_score(y_true_int, y_pred_int, average='weighted', zero_division=0)
    recall = recall_score(y_true_int, y_pred_int, average='weighted', zero_division=0)
    f1 = f1_score(y_true_int, y_pred_int, average='weighted', zero_division=0)
    
    # ROC AUC needs probability matrix
    y_true_bin = label_binarize(y_true_int, classes=range(8))
    # Handle case if not all classes are present in test set
    try:
        roc_auc = roc_auc_score(y_true_bin, probs, average='weighted', multi_class='ovr')
    except Exception as e:
        print(f"ROC AUC calculation failed: {e}")
        roc_auc = None

    metrics = {
        "model": "LightGBM Fault Classifier",
        "test_set_size": len(test_df),
        "accuracy": acc,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "roc_auc": roc_auc,
        "evaluation_type": "unseen test set / controlled experiment",
        "validation_status": "model-level evaluation",
        "field_validation_status": "ongoing"
    }
    
    with open(results_dir / "accuracy_metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
        
    print("Metrics saved to accuracy_metrics.json")
    
    # Save a sample of test predictions
    test_df_out = test_df.copy()
    test_df_out["predicted_label"] = labels
    test_df_out[["timestamp", "temperature", "pressure", "relative_humidity", "label", "predicted_label"]].head(100).to_csv(results_dir / "test_predictions.csv", index=False)
    
    print("Sample test predictions saved to test_predictions.csv")
    
    try:
        from sklearn.metrics import ConfusionMatrixDisplay
        cm = confusion_matrix(y_true_int, y_pred_int, labels=range(8))
        disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=[CLASS_MAP[i] for i in range(8)])
        fig, ax = plt.subplots(figsize=(12, 10))
        disp.plot(ax=ax, cmap="Blues", xticks_rotation=45)
        plt.tight_layout()
        plt.savefig(results_dir / "confusion_matrix.png")
        plt.close()
        print("Confusion matrix saved to confusion_matrix.png")
        
        # ROC curve plot
        from sklearn.metrics import roc_curve, auc
        plt.figure(figsize=(10, 8))
        for i in range(8):
            if np.sum(y_true_bin[:, i]) > 0:
                fpr, tpr, _ = roc_curve(y_true_bin[:, i], probs[:, i])
                roc_auc_class = auc(fpr, tpr)
                plt.plot(fpr, tpr, lw=2, label=f'Class {CLASS_MAP[i]} (area = {roc_auc_class:.2f})')
        plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('Receiver Operating Characteristic - Multi-class')
        plt.legend(loc="lower right")
        plt.savefig(results_dir / "roc_curve.png")
        plt.close()
        print("ROC curve saved to roc_curve.png")
        
        # PR curve plot
        from sklearn.metrics import precision_recall_curve, average_precision_score
        plt.figure(figsize=(10, 8))
        for i in range(8):
            if np.sum(y_true_bin[:, i]) > 0:
                prec, rec, _ = precision_recall_curve(y_true_bin[:, i], probs[:, i])
                ap = average_precision_score(y_true_bin[:, i], probs[:, i])
                plt.plot(rec, prec, lw=2, label=f'Class {CLASS_MAP[i]} (AP = {ap:.2f})')
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.title('Precision-Recall Curve - Multi-class')
        plt.legend(loc="lower left")
        plt.savefig(results_dir / "precision_recall_curve.png")
        plt.close()
        print("PR curve saved to precision_recall_curve.png")
        
    except Exception as e:
        print(f"Plotting failed: {e}")
        
    print("Results generation complete.")

if __name__ == "__main__":
    main()
