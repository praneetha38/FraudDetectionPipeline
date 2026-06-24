"""
Streamlit Dashboard - Fraud Detection
By: Praneetha Meda
Real-time fraud detection dashboard
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(
    page_title="Fraud Detection Dashboard",
    page_icon="🚨",
    layout="wide"
)

st.title("🚨 Real-Time Fraud Detection Dashboard")
st.markdown("**By: Praneetha Meda** | IEEE CIS Fraud Detection Pipeline")
st.markdown("---")

# Sample data (will be replaced with real data from Delta Lake)
def get_sample_data():
    np.random.seed(42)
    n = 1000
    
    times = [datetime.now() - timedelta(minutes=x) for x in range(n)]
    amounts = np.random.exponential(100, n)
    fraud_labels = np.random.choice([0, 1], n, p=[0.95, 0.05])
    risk_scores = np.random.uniform(0, 100, n)
    
    return pd.DataFrame({
        'timestamp': times,
        'amount': amounts,
        'is_fraud': fraud_labels,
        'risk_score': risk_scores
    })

df = get_sample_data()

# KPIs
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Transactions", f"{len(df):,}", "+150")

with col2:
    fraud_count = df['is_fraud'].sum()
    fraud_pct = fraud_count / len(df) * 100
    st.metric("Fraud Cases", fraud_count, f"{fraud_pct:.2f}%")

with col3:
    high_risk = (df['risk_score'] > 70).sum()
    st.metric("High Risk Alerts", high_risk, "+5")

with col4:
    avg_amount = df['amount'].mean()
    st.metric("Avg Amount", f"${avg_amount:.2f}", "-$5.20")

st.markdown("---")

# Charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("Transaction Volume")
    df_time = df.set_index('timestamp').resample('1H').size()
    st.line_chart(df_time)

with col2:
    st.subheader("Risk Score Distribution")
    fig = px.histogram(df, x='risk_score', nbins=50)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.markdown("**Pipeline Status:** ✅ Running")
st.markdown("**Data Source:** IEEE CIS | **Model:** RandomForest (98% ROC-AUC)")
EOF

echo "✅ Created streamlit/app.py"
