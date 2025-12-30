import streamlit as st
import psycopg2
import os
from google.cloud import logging as cloud_logging
from google.auth import default

# Authenticate for GCP
credentials, project = default()

st.title("Aegis Arsenal Agent Dashboard")

# Connect to Supabase
try:
    conn = psycopg2.connect(os.environ.get("SUPABASE_CONN_STRING"))
    cursor = conn.cursor()

    st.title("Aegis Arsenal Agent Dashboard")

    # Fetch checkpoints
    cursor.execute("SELECT * FROM checkpoints ORDER BY created_at DESC LIMIT 10")
    checkpoints = cursor.fetchall()

    st.header("Recent Agent Checkpoints")
    for cp in checkpoints:
        st.write(f"Thread ID: {cp[0]}, State: {cp[1]}, Created: {cp[2]}")

    cursor.close()
    conn.close()
except Exception as e:
    st.error(f"Database error: {e}")

# Aegis Heartbeat Widget
try:
    # Mock metrics - in production, pull from Supabase or BigQuery
    metrics = {
        "cost": 2.45,  # Example token cost
        "success_pct": 98.5,
        "threads": 5
    }
    render_heartbeat_widget(metrics)
except Exception as e:
    st.error(f"Heartbeat error: {e}")

# Fetch logs
try:
    logging_client = cloud_logging.Client(credentials=credentials, project=project)
    entries = logging_client.list_entries(filter_='resource.type="cloud_function"', max_results=10)
    st.header("Recent Logs")
    for entry in entries:
        st.write(f"{entry.timestamp}: {entry.payload}")
except Exception as e:
    st.error(f"Logging error: {e}")

def render_heartbeat_widget(metrics):
    st.subheader("💓 Aegis Swarm Heartbeat")
    col1, col2, col3 = st.columns(3)
    col1.metric("Token Spend (USD)", f"${metrics['cost']:.2f}")
    col2.metric("Success Rate", f"{metrics['success_pct']}%")
    col3.metric("Active Threads", metrics['threads'])