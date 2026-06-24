import os
import sys
import subprocess
import time

print("=" * 80)
print("FRAUD DETECTION PIPELINE - WINDOWS SETUP")
print("=" * 80)
print()

# Check if CSV files exist
print("1. Checking for dataset files...")
csv_files = [
    "data/raw/train_transaction.csv",
    "data/raw/train_identity.csv",
    "data/raw/test_transaction.csv",
    "data/raw/test_identity.csv"
]

missing_files = [f for f in csv_files if not os.path.exists(f)]

if missing_files:
    print("ERROR: Missing CSV files!")
    print("Missing:", missing_files)
    sys.exit(1)

print("OK - All CSV files found!")
print()

# Create directories
print("2. Creating directories...")
os.makedirs("data/model", exist_ok=True)
os.makedirs("logs", exist_ok=True)
print("OK")
print()

# Preprocess
print("3. Preprocessing data...")
try:
    import pandas as pd
    import numpy as np
    
    print("   Loading datasets...")
    df_trans = pd.read_csv("data/raw/train_transaction.csv")
    df_identity = pd.read_csv("data/raw/train_identity.csv")
    
    print("   Merging...")
    df = df_trans.merge(df_identity, on="TransactionID", how="left")
    
    fraud_count = (df["isFraud"] == 1).sum()
    print(f"   OK - {len(df):,} rows, {fraud_count:,} frauds")
    
    df.to_csv("data/raw/ieee_combined.csv", index=False)
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
print()

# Train model
print("4. Training model (5 minutes)...")
try:
    import pandas as pd
    import numpy as np
    from sklearn.preprocessing import StandardScaler
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import roc_auc_score
    import pickle
    
    print("   Loading data...")
    df = pd.read_csv("data/raw/ieee_combined.csv")
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    numeric_cols = [col for col in numeric_cols if col not in ["TransactionID", "isFraud"]]
    
    X = df[numeric_cols].fillna(df[numeric_cols].median())
    y = df["isFraud"]
    
    print("   Scaling...")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    print("   Splitting...")
    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.3, random_state=42, stratify=y)
    
    print("   Training...")
    model = RandomForestClassifier(n_estimators=100, max_depth=15, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, y_pred_proba)
    
    print(f"   ROC-AUC: {auc:.4f}")
    
    os.makedirs("data/model", exist_ok=True)
    with open("data/model/fraud_model.pkl", "wb") as f:
        pickle.dump(model, f)
    with open("data/model/scaler.pkl", "wb") as f:
        pickle.dump(scaler, f)
    with open("data/model/feature_names.pkl", "wb") as f:
        pickle.dump(numeric_cols, f)
    
    print("   OK - Model saved")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
print()

print("=" * 80)
print("SETUP COMPLETE!")
print("=" * 80)
print()
print("Next: Open 3 PowerShell terminals:")
print()
print("Terminal 1:")
print("  python kafka/producer.py --mode stream --tps 100")
print()
print("Terminal 2:")
print("  docker-compose exec spark spark-submit `")
print("    --packages org.apache.spark:spark-sql-kafka-0-10_2.13:3.5.0,io.delta:delta-core_2.12:2.4.0 `")
print("    /app/spark/streaming_job.py")
print()
print("Terminal 3:")
print("  streamlit run streamlit/app.py --server.port=8501")
print()
print("Dashboard: http://localhost:8501")
