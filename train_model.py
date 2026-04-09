"""
Model training for DDoS detection.
Trains and evaluates an SVM model.
"""
import os
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from feature_extraction import extract_features, FEATURE_COLUMNS


def ensure_training_log_exists(log_path='traffic_log.csv'):
    """Create synthetic traffic log data if missing, with all 3 classes."""
    if os.path.exists(log_path):
        return

    rng = np.random.default_rng(42)
    rows_per_class = 100
    endpoints = np.array(['/', '/login', '/api/data', '/api/submit'])
    methods = np.array(['GET', 'POST'])
    now = datetime.utcnow()

    records = []

    def generate_class_rows(label, req_min, req_max, ia_min, ia_max, err_min, err_max, payload_min, payload_max):
        current_ts = now
        for idx in range(rows_per_class):
            ip = f"10.{label}.{idx // 25}.{(idx % 25) + 1}"
            endpoint = rng.choice(endpoints)
            method = 'POST' if endpoint == '/api/submit' else str(rng.choice(methods))
            inter_arrival = float(rng.uniform(ia_min, ia_max))
            current_ts = current_ts + timedelta(seconds=inter_arrival)
            error_rate = float(rng.uniform(err_min, err_max))
            is_error = rng.random() < error_rate
            status_code = int(rng.choice([429, 500, 503])) if is_error else 200
            payload_size = int(rng.integers(payload_min, payload_max + 1))

            records.append({
                'timestamp': current_ts.isoformat(),
                'ip': ip,
                'endpoint': str(endpoint),
                'method': method,
                'status_code': status_code,
                'payload_size': payload_size,
                'label': label
            })

    # Normal: low request rate profile, high inter-arrival, low errors
    generate_class_rows(0, 1, 5, 0.5, 2.0, 0.0, 0.1, 100, 1000)
    # Suspicious: medium request rate profile, medium inter-arrival, medium errors
    generate_class_rows(1, 10, 30, 0.1, 0.5, 0.1, 0.3, 500, 2000)
    # Attack: very high request rate profile, very low inter-arrival, high errors
    generate_class_rows(2, 80, 200, 0.001, 0.05, 0.3, 0.8, 3000, 6000)

    synthetic_df = pd.DataFrame(records)
    synthetic_df.to_csv(log_path, index=False)
    print(f"[TRAINING] Synthetic traffic log generated at {log_path} ({len(synthetic_df)} rows)")


def train_model(log_path='traffic_log.csv'):
    ensure_training_log_exists(log_path)

    # Load features
    print("[TRAINING] Loading features")
    features_df = extract_features(log_path)
    
    if len(features_df) == 0:
        print("[ERROR] No features extracted.")
        return
    
    print(f"[TRAINING] Loaded {len(features_df)} feature vectors")
    print(f"[TRAINING] Feature DataFrame shape: {features_df.shape}")
    print(f"[TRAINING] Label distribution:\n{features_df['label'].value_counts()}")
    
    # Separate features and labels
    X = features_df[FEATURE_COLUMNS]
    y = features_df['label']
    
    # Drop rows with NaN (just in case)
    X = X.dropna()
    y = y[X.index]
    
    print(f"[TRAINING] After dropping NaN: {X.shape}")
    
    # Split data: 80% train, 20% test with stratification
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"[TRAINING] Train set size: {X_train.shape[0]}")
    print(f"[TRAINING] Test set size: {X_test.shape[0]}")
    
    # Train SVM
    print("\n[TRAINING] Training SVM...")
    svm_model = SVC(kernel='rbf', probability=True, random_state=42)
    svm_model.fit(X_train, y_train)

    # Evaluate SVM
    y_pred_svm = svm_model.predict(X_test)
    print("[EVALUATION] SVM Classification Report:")
    print(classification_report(y_test, y_pred_svm, target_names=['Normal', 'Suspicious', 'Attack']))

    svm_accuracy = (y_pred_svm == y_test).mean()
    print(f"\n[COMPARISON] SVM Accuracy: {svm_accuracy:.4f}")

    print("\n[SAVING] Saving SVM model as ddos_model.pkl...")
    joblib.dump(svm_model, 'ddos_model.pkl')
    print("[SAVING] Model saved successfully!")
    
    # Plot and save confusion matrix for SVM
    print("\n[VISUALIZATION] Generating confusion matrix...")
    cm = confusion_matrix(y_test, y_pred_svm)
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['Normal', 'Suspicious', 'Attack'],
                yticklabels=['Normal', 'Suspicious', 'Attack'])
    plt.title('Confusion Matrix - SVM DDoS Detector')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    plt.savefig('confusion_matrix.png', dpi=100, bbox_inches='tight')
    print("[VISUALIZATION] Confusion matrix saved as confusion_matrix.png")
    
    print("\n[TRAINING] Training complete!")


if __name__ == '__main__':
    ensure_training_log_exists('traffic_log.csv')
    train_model('traffic_log.csv')
