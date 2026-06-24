"""
Kafka Producer - IEEE CIS Fraud Detection
By: Praneetha Meda
Streams IEEE CIS fraud data to Kafka
"""

import json
import pandas as pd
import time
from datetime import datetime
from kafka import KafkaProducer
import logging
import argparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

KAFKA_SERVERS = ['localhost:9092']
TOPIC = 'transactions_raw'

def load_data(csv_path='data/raw/ieee_combined.csv'):
    try:
        logger.info(f"Loading {csv_path}...")
        df = pd.read_csv(csv_path)
        logger.info(f"✅ Loaded {len(df):,} transactions")
        return df
    except FileNotFoundError:
        logger.error(f"File not found: {csv_path}")
        logger.error("Run: bash scripts/setup-complete.sh")
        return None

def stream_data(df, tps=100):
    try:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_SERVERS,
            value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
            acks='all'
        )
        
        logger.info(f"Streaming at {tps} TPS...")
        interval = 1.0 / tps
        count = 0
        
        for _, row in df.iterrows():
            transaction = {
                'transaction_id': f"IEEE_{int(row['TransactionID'])}",
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'amount': float(row['TransactionAmt']),
                'is_fraud': int(row['isFraud']),
                'features': {
                    col: float(row[col]) for col in row.index
                    if col not in ['TransactionID', 'TransactionAmt', 'isFraud']
                    and pd.notna(row[col])
                }
            }
            
            producer.send(TOPIC, value=transaction)
            count += 1
            
            if count % 1000 == 0:
                logger.info(f"Sent {count:,} transactions")
            
            time.sleep(interval)
        
        producer.flush()
        producer.close()
        logger.info(f"✅ Done! Sent {count:,} transactions")
        
    except KeyboardInterrupt:
        logger.info(f"Stopped. Sent {count:,} transactions")
    except Exception as e:
        logger.error(f"Error: {e}")
        raise

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['stream', 'batch'], default='stream')
    parser.add_argument('--tps', type=int, default=100)
    parser.add_argument('--csv', type=str, default='data/raw/ieee_combined.csv')
    args = parser.parse_args()
    
    df = load_data(args.csv)
    if df is None:
        exit(1)
    
    stream_data(df, tps=args.tps)
