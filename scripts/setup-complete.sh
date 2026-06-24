#!/bin/bash
# Fraud Detection Pipeline - Complete Automated Setup
# By: Praneetha Meda
# Automatically downloads IEEE CIS dataset, trains model, and starts services

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 FRAUD DETECTION PIPELINE - IEEE CIS${NC}"
echo "By: Praneetha Meda"
echo "=============================================="
echo ""

# Check prerequisites
echo -e "${BLUE}1️⃣  Checking prerequisites...${NC}"
command -v docker >/dev/null || { echo "Docker not found"; exit 1; }
command -v python3 >/dev/null || { echo "Python3 not found"; exit 1; }
echo "✅ Prerequisites OK"
echo ""

# Install dependencies
echo -e "${BLUE}2️⃣  Installing dependencies...${NC}"
pip install -q -r requirements.txt 2>/dev/null
echo "✅ Dependencies installed"
echo ""

# Create directories
echo -e "${BLUE}3️⃣  Creating directories...${NC}"
mkdir -p data/{raw,model,preprocessed} logs
echo "✅ Directories created"
echo ""

# Download dataset
echo -e "${BLUE}4️⃣  Downloading IEEE CIS dataset (may take 10 min)...${NC}"

# Check Kaggle API
if [ ! -f ~/.kaggle/kaggle.json ]; then
    echo "❌ Kaggle API key not found!"
    echo ""
    echo "Setup instructions:"
    echo "1. Visit: https://www.kaggle.com/settings/account"
    echo "2. Create New Token"
    echo "3. Move to: ~/.kaggle/kaggle.json"
    echo "4. Run: chmod 600 ~/.kaggle/kaggle.json"
    echo "5. Re-run this script"
    exit 1
fi

python3 << 'EOFPY'
import os
import sys
from pathlib import Path

try:
    import kaggle
    print("Downloading IEEE CIS dataset...")
    os.chdir('data/raw')
    kaggle.api.dataset_download_files('ieee-fraud-detection', unzip=True)
    os.chdir('../..')
    print("✅ Dataset downloaded")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
EOFPY
echo ""

# Preprocess data
echo -e "${BLUE}5️⃣  Preprocessing data...${NC}"
python3 << 'EOFPY'
import pandas as pd
import numpy as np

try:
    print("Loading datasets...")
    df_trans = pd.read_csv('data/raw/train_transaction.csv')
    df_identity = pd.read_csv('data/raw/train_identity.csv')
    
    print(f"Merging...")
    df = df_trans.merge(df_identity, on='TransactionID', how='left')
    
    fraud_count = (df['isFraud'] == 1).sum()
    fraud_pct = fraud_count / len(df) * 100
    print(f"✅ Data ready: {len(df):,} transactions, {fraud_count:,} frauds ({fraud_pct:.2f}%)")
    
    df.to_csv('data/raw/ieee_combined.csv', index=False)
    print("✅ Saved combined dataset")
except Exception as e:
    print(f"Error: {e}")
    exit(1)
EOFPY
echo ""

# Train model
echo -e "${BLUE}6️⃣  Training model (2-3 min)...${NC}"
python3 << 'EOFPY'
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
import pickle
from pathlib import Path

try:
    print("Loading data...")
    df = pd.read_csv('data/raw/ieee_combined.csv')
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    numeric_cols = [col for col in numeric_cols if col not in ['TransactionID', 'isFraud']]
    
    print(f"Using {len(numeric_cols)} features")
    
    X = df[numeric_cols].fillna(df[numeric_cols].median())
    y = df['isFraud']
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.3, random_state=42, stratify=y
    )
    
    print("Training RandomForest...")
    model = RandomForestClassifier(n_estimators=100, max_depth=15, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, y_pred_proba)
    
    print(f"✅ Model trained! ROC-AUC: {auc:.4f}")
    
    Path('data/model').mkdir(exist_ok=True)
    with open('data/model/fraud_model.pkl', 'wb') as f:
        pickle.dump(model, f)
    with open('data/model/scaler.pkl', 'wb') as f:
        pickle.dump(scaler, f)
    with open('data/model/feature_names.pkl', 'wb') as f:
        pickle.dump(numeric_cols, f)
    
    print("✅ Model saved")
except Exception as e:
    print(f"Error: {e}")
    exit(1)
EOFPY
echo ""

# Start Docker
echo -e "${BLUE}7️⃣  Starting Docker services...${NC}"
docker-compose up -d > /dev/null 2>&1
echo "✅ Services started"
sleep 10
echo ""

# Summary
echo -e "${GREEN}✅ SETUP COMPLETE!${NC}"
echo ""
echo "=================================================="
echo "🎉 Everything is ready!"
echo "=================================================="
echo ""
echo "Next: Run these in 3 separate terminals:"
echo ""
echo "📊 Terminal 1:"
echo "  python kafka/producer.py --mode stream --tps 100"
echo ""
echo "⚡ Terminal 2:"
echo "  docker-compose exec spark spark-submit \\"
echo "    --packages org.apache.spark:spark-sql-kafka-0-10_2.13:3.5.0,io.delta:delta-core_2.12:2.4.0 \\"
echo "    /app/spark/streaming_job.py"
echo ""
echo "📱 Terminal 3:"
echo "  streamlit run streamlit/app.py --server.port=8501"
echo ""
echo "📈 Dashboard: http://localhost:8501"
echo ""
echo "=================================================="
echo ""
echo "By: Praneetha Meda"
echo "Good luck! 🚀"
