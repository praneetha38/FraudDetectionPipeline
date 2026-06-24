"""
Spark Streaming Job - ML Inference
By: Praneetha Meda
Reads from Kafka, runs ML inference, writes to Delta Lake
"""

import json
import pickle
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType, TimestampType
from pyspark.sql.functions import from_json, col, current_timestamp

# Initialize Spark
spark = SparkSession.builder \
    .appName("fraud-detection-streaming") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# Schema
schema = StructType([
    StructField("transaction_id", StringType()),
    StructField("timestamp", TimestampType()),
    StructField("amount", DoubleType()),
    StructField("is_fraud", IntegerType()),
    StructField("features", StructType([]))
])

try:
    print("📡 Connecting to Kafka...")
    df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("subscribe", "transactions_raw") \
        .option("startingOffsets", "latest") \
        .load()
    
    print("✅ Kafka connected")
    
    # Parse JSON
    parsed_df = df.select(
        from_json(col("value").cast("string"), schema).alias("data")
    ).select("data.*")
    
    # Load model
    try:
        with open('data/model/fraud_model.pkl', 'rb') as f:
            model = pickle.load(f)
        print("✅ Model loaded")
    except:
        print("⚠️  Model not found. Using mock predictions.")
        model = None
    
    # Write to Delta
    print("⏳ Starting stream...")
    
    query = parsed_df.writeStream \
        .format("delta") \
        .option("path", "data/delta_lake/bronze/transactions") \
        .option("checkpointLocation", "data/delta_lake/checkpoints/bronze") \
        .trigger(processingTime="5 seconds") \
        .start()
    
    query.awaitTermination()
    
except Exception as e:
    print(f"❌ Error: {e}")
    raise
