"""
Financial Guard - Budget Enforcement for Aegis Arsenal
Part of the Aegis Arsenal Swarm Engine
Implements financial hard-stops and budget monitoring
"""

import os
import asyncio
from datetime import datetime, timedelta
import psycopg2
from typing import Dict, Any

# Budget limits
DAILY_BUDGET_LIMIT = 10.00  # $10 per day
HOURLY_BUDGET_LIMIT = 2.00  # $2 per hour

async def get_daily_usage_from_db() -> float:
    """
    Query Supabase for total token spend in the last 24 hours.
    """
    try:
        conn = psycopg2.connect(os.environ.get("SUPABASE_CONN_STRING"))
        cursor = conn.cursor()

        # Query for sum of costs in last 24 hours (assuming a cost tracking table)
        query = """
        SELECT COALESCE(SUM(cost), 0) as total_cost
        FROM token_usage
        WHERE created_at >= NOW() - INTERVAL '24 hours'
        """
        cursor.execute(query)
        result = cursor.fetchone()
        total_cost = float(result[0]) if result else 0.0

        cursor.close()
        conn.close()
        return total_cost
    except Exception as e:
        print(f"Failed to get daily usage: {e}")
        return 0.0  # Default to 0 if DB error

async def get_hourly_usage_from_db() -> float:
    """
    Query for token spend in the last hour.
    """
    try:
        conn = psycopg2.connect(os.environ.get("SUPABASE_CONN_STRING"))
        cursor = conn.cursor()

        query = """
        SELECT COALESCE(SUM(cost), 0) as total_cost
        FROM token_usage
        WHERE created_at >= NOW() - INTERVAL '1 hour'
        """
        cursor.execute(query)
        result = cursor.fetchone()
        total_cost = float(result[0]) if result else 0.0

        cursor.close()
        conn.close()
        return total_cost
    except Exception as e:
        print(f"Failed to get hourly usage: {e}")
        return 0.0

async def verify_budget_ceiling(current_thread_cost: float = 0.0) -> Dict[str, Any]:
    """
    Action: Prevents execution if the daily/hourly limit is exceeded.
    Returns dict with status and any lockdown actions.
    """
    daily_spend = await get_daily_usage_from_db()
    hourly_spend = await get_hourly_usage_from_db()

    total_projected = daily_spend + current_thread_cost

    if total_projected >= DAILY_BUDGET_LIMIT:
        # Trigger lockdown
        await trigger_temporary_lockdown()
        return {
            "status": "LOCKDOWN",
            "reason": "Daily budget limit exceeded",
            "daily_spend": daily_spend,
            "limit": DAILY_BUDGET_LIMIT,
            "flag": "$$SSC_FINANCIAL_LIMIT_REACHED"
        }
    elif hourly_spend >= HOURLY_BUDGET_LIMIT:
        return {
            "status": "WARNING",
            "reason": "Hourly budget limit approached",
            "hourly_spend": hourly_spend,
            "limit": HOURLY_BUDGET_LIMIT,
            "flag": "$$SSC_HOURLY_LIMIT_WARNING"
        }
    else:
        return {
            "status": "OK",
            "daily_spend": daily_spend,
            "hourly_spend": hourly_spend,
            "remaining_daily": DAILY_BUDGET_LIMIT - daily_spend,
            "remaining_hourly": HOURLY_BUDGET_LIMIT - hourly_spend
        }

async def trigger_temporary_lockdown():
    """
    Impulsive Activation: Revoke Secret Access for 24h to prevent further spending.
    In production, this would use GCP IAM APIs.
    """
    print("$$SSC_FINANCIAL_LOCKDOWN_ACTIVATED: Temporarily revoking LLM API access")
    # In real implementation:
    # - Revoke service account access to OpenAI/Anthropic secrets
    # - Send alert notification
    # - Schedule re-enable after 24h

async def log_token_usage(thread_id: str, cost: float, model: str):
    """
    Log token usage to Supabase for budget tracking.
    """
    try:
        conn = psycopg2.connect(os.environ.get("SUPABASE_CONN_STRING"))
        cursor = conn.cursor()

        # Insert into token_usage table (assuming it exists)
        cursor.execute("""
        INSERT INTO token_usage (thread_id, cost, model, created_at)
        VALUES (%s, %s, %s, NOW())
        """, (thread_id, cost, model))

        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Failed to log token usage: {e}")

# Export for integration
FINANCIAL_GUARD = {
    "verify_budget": verify_budget_ceiling,
    "log_usage": log_token_usage,
    "daily_limit": DAILY_BUDGET_LIMIT,
    "hourly_limit": HOURLY_BUDGET_LIMIT
}