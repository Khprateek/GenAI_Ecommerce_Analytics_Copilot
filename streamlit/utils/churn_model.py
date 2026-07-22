import os
import pandas as pd
import numpy as np
import streamlit as st
from google.cloud import bigquery
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from utils.bq_client import run_query

@st.cache_data(ttl=300) # Cache for 5 minutes
def get_churn_predictions():
    """
    1. Loads completed orders history.
    2. Constructs a historical snapshot at (MaxDate - 90 days).
    3. Trains a scikit-learn LogisticRegression model (no leakage).
    4. Loads current features from dbt model `int_customer_churn_features`.
    5. Applies the model to predict current churn probabilities.
    6. Joins with customer attributes from `dim_customers`.
    """
    # Load completed orders
    orders_sql = """
        select customer_id, order_date, cast(revenue_usd as float64) as revenue
        from `genai-copilot-enterprisedata.staging.stg_orders`
        where order_status = 'COMPLETED'
    """
    orders_df = run_query(orders_sql)
    if orders_df.empty:
        return pd.DataFrame()
        
    orders_df['order_date'] = pd.to_datetime(orders_df['order_date'])
    
    # Load all customers
    cust_sql = """
        select customer_id
        from `genai-copilot-enterprisedata.staging.stg_customers`
    """
    customers_df = run_query(cust_sql)
    if customers_df.empty:
        return pd.DataFrame()

    max_date = orders_df['order_date'].max()
    cutoff_date = max_date - pd.Timedelta(days=90)

    orders_by_cust = {c: group for c, group in orders_df.groupby('customer_id')}

    training_data = []
    for _, row in customers_df.iterrows():
        cust_id = row['customer_id']
        cust_orders = orders_by_cust.get(cust_id, pd.DataFrame())

        # Features from BEFORE the cutoff
        train_orders = cust_orders[cust_orders['order_date'] <= cutoff_date] if not cust_orders.empty else pd.DataFrame()

        if train_orders.empty:
            days_since = 180
            freq_30 = 0
            trend = 0.0
        else:
            last_date = train_orders['order_date'].max()
            days_since = max(0, (cutoff_date - last_date).days)

            train_30 = train_orders[train_orders['order_date'] >= (cutoff_date - pd.Timedelta(days=30))]
            freq_30 = len(train_30)

            avg_lifetime = train_orders['revenue'].mean()
            avg_30 = train_30['revenue'].mean() if not train_30.empty else 0.0
            trend = avg_30 - avg_lifetime

        # Label: churned = no order after the cutoff
        future_orders = cust_orders[cust_orders['order_date'] > cutoff_date] if not cust_orders.empty else pd.DataFrame()
        is_churned = 1 if future_orders.empty else 0

        training_data.append({
            'customer_id': cust_id,
            'days_since_last_order': days_since,
            'order_frequency_30d': freq_30,
            'avg_order_value_trend': trend,
            'churned': is_churned
        })

    train_df = pd.DataFrame(training_data)

    features = ['days_since_last_order', 'order_frequency_30d', 'avg_order_value_trend']
    X_train = train_df[features]
    y_train = train_df['churned']

    # Scale features so logistic regression works properly
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)

    model = LogisticRegression(random_state=42, max_iter=500, C=0.1)
    model.fit(X_train_scaled, y_train)

    # Load current features from DBT model
    current_sql = """
        select customer_id, days_since_last_order, order_frequency_30d, avg_order_value_trend
        from `genai-copilot-enterprisedata.staging.int_customer_churn_features`
    """
    current_features_df = run_query(current_sql)
    if current_features_df.empty:
        return pd.DataFrame()

    X_current = current_features_df[features]
    X_current_scaled = scaler.transform(X_current)

    probs = model.predict_proba(X_current_scaled)[:, 1]
    current_features_df = current_features_df.copy()
    current_features_df['churn_probability'] = probs

    # Load customer attributes from dim_customers
    dim_cust_sql = """
        select customer_id, full_name, email, state_name, city_name, rfm_segment, lifetime_value_usd
        from `genai-copilot-enterprisedata.marts.dim_customers`
    """
    dim_cust_df = run_query(dim_cust_sql)
    if dim_cust_df.empty:
        return pd.DataFrame()

    merged_df = pd.merge(dim_cust_df, current_features_df, on='customer_id', how='inner')

    # Use quantile-based thresholds so the risk distribution is always meaningful
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
