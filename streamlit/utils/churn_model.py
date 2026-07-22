import os
import pandas as pd
import numpy as np
import streamlit as st
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from utils.bq_client import run_query

@st.cache_data(ttl=300) # Cache for 5 minutes
def get_churn_predictions():
    """
    Trains a Logistic Regression model on the quick-commerce feature vector.
    """
    PROJECT = os.environ.get("GCP_PROJECT_ID", "your-project")
    
    # 1. Fetch features
    features_sql = f"""
        select 
            customer_id, 
            days_since_last_order, 
            orders_30d, 
            aov_trend,
            delivery_time_trend,
            issue_rate_trend,
            active_days_30d
        from `{PROJECT}.staging.int_customer_churn_features`
    """
    df_features = run_query(features_sql)
    if df_features.empty:
        return pd.DataFrame()
        
    # Create proxy label: Churned if days_since_last_order > 45
    df_features['is_churned'] = (df_features['days_since_last_order'] > 45).astype(int)
    
    # Define features
    feature_cols = ['days_since_last_order', 'orders_30d', 'aov_trend', 'delivery_time_trend', 'issue_rate_trend', 'active_days_30d']
    X = df_features[feature_cols]
    y = df_features['is_churned']
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    model = LogisticRegression(random_state=42, max_iter=500, C=0.1)
    model.fit(X_scaled, y)
    
    probs = model.predict_proba(X_scaled)[:, 1]
    df_features['churn_probability'] = probs
    
    # 2. Fetch customer dimensions
    cust_sql = f"""
        select 
            customer_id, 
            full_name, 
            email, 
            state_name, 
            city_name, 
            is_pass_member,
            rfm_segment, 
            churn_risk_tier as bq_risk_tier,
            lifetime_revenue
        from `{PROJECT}.marts.dim_customers`
    """
    dim_cust_df = run_query(cust_sql)
    if dim_cust_df.empty:
        return pd.DataFrame()
        
    merged_df = pd.merge(dim_cust_df, df_features, on='customer_id', how='inner')
    
    # Risk labeling based on ML predictions
    p33 = merged_df['churn_probability'].quantile(0.33)
    p66 = merged_df['churn_probability'].quantile(0.66)

    def risk_label(p):
        if p <= p33:
            return 'Low'
        elif p <= p66:
            return 'Medium'
        else:
            return 'High'

    merged_df['risk_tier'] = merged_df['churn_probability'].apply(risk_label)
    merged_df = merged_df.sort_values(by='churn_probability', ascending=False)
    
    return merged_df
