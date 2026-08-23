"""
PostgreSQL & Relational Database Sync Engine for Multi-Sector Gold Data Marts.

Persists PySpark Gold Data Marts (Credit Card, Banking, Healthcare, Clinical, Insurance, Retail)
into PostgreSQL (if configured) or SQLite relational tables for REST APIs, BI Dashboards, and AI Copilot tools.
"""

import os
import json
import sqlite3
from datetime import datetime, timezone
from typing import Dict, Any

LAKE_GOLD_DIR = os.path.join(os.getcwd(), "data", "lake", "gold")
SQLITE_DB_PATH = os.path.join(os.getcwd(), "platform_analytics.db")
POSTGRES_URL = os.environ.get("POSTGRES_URL") or os.environ.get("DATABASE_URL")


class PostgresGoldSync:
    """Syncs PySpark Gold Data Marts to Relational Analytics Database."""

    def __init__(self, db_url_or_path: str = None):
        self.db_target = db_url_or_path or POSTGRES_URL or SQLITE_DB_PATH

    def get_connection(self):
        """Attempts PostgreSQL connection first. SQLite fallback is restricted to development mode."""
        target = str(self.db_target)
        env = os.environ.get("ENVIRONMENT", "development").lower()

        if target.startswith("postgres"):
            try:
                import psycopg2
                conn = psycopg2.connect(target)
                return conn, "PostgreSQL (psycopg2)"
            except Exception as e:
                if env == "production":
                    raise RuntimeError(
                        f"[PostgresGoldSync] PRODUCTION DATABASE OUTAGE: Connection to PostgreSQL failed ({e}). "
                        "SQLite fallback is strictly disabled in production environment to prevent data drift."
                    )
                print(f"[PostgresGoldSync] PostgreSQL connection failed ({e}), falling back to SQLite (development mode).")

        conn = sqlite3.connect(SQLITE_DB_PATH)
        return conn, "SQLite (platform_analytics.db fallback)"

    def sync_all_marts(self) -> Dict[str, Any]:
        """Creates tables and populates Gold summaries across all 6 enterprise sectors."""
        conn, engine_name = self.get_connection()
        cursor = conn.cursor()

        # Create multi-sector summary table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gold_multi_sector_summary (
                sector VARCHAR(100) PRIMARY KEY,
                total_records INTEGER,
                primary_metric VARCHAR(100),
                primary_metric_value DOUBLE PRECISION,
                secondary_metric VARCHAR(100),
                secondary_metric_value DOUBLE PRECISION,
                updated_at VARCHAR(100)
            )
        """)

        # Load PySpark Master Gold JSON
        master_json_path = os.path.join(LAKE_GOLD_DIR, "master_multi_sector_gold.json")
        synced_sectors = {}

        if os.path.exists(master_json_path):
            with open(master_json_path, "r") as f:
                master_data = json.load(f)

            sectors = master_data.get("sectors", {})
            now_iso = datetime.now(timezone.utc).isoformat()

            for sec, data in sectors.items():
                if "sqlite" in engine_name.lower():
                    upsert_sql = """
                        INSERT OR REPLACE INTO gold_multi_sector_summary 
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """
                else:
                    upsert_sql = """
                        INSERT INTO gold_multi_sector_summary (sector, total_records, primary_metric, primary_metric_value, secondary_metric, secondary_metric_value, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (sector) DO UPDATE SET
                            total_records = EXCLUDED.total_records,
                            primary_metric_value = EXCLUDED.primary_metric_value,
                            secondary_metric_value = EXCLUDED.secondary_metric_value,
                            updated_at = EXCLUDED.updated_at
                    """

                if sec == "credit_card":
                    cursor.execute(upsert_sql, ("Credit Card Fraud", data["total_transactions"], "fraud_rate_pct", data["fraud_rate_pct"], "total_volume_usd", data["total_volume_usd"], now_iso))
                    synced_sectors["credit_card"] = data

                elif sec == "banking":
                    cursor.execute(upsert_sql, ("Banking Loan Risk", data["total_loans"], "default_rate_pct", data["default_rate_pct"], "total_credit_granted_usd", data["total_credit_granted_usd"], now_iso))
                    synced_sectors["banking"] = data

                elif sec == "healthcare":
                    cursor.execute(upsert_sql, ("Healthcare OGD", data["total_hospitals_reporting"], "avg_bed_occupancy_pct", data["avg_bed_occupancy_pct"], "avg_opd_ipd_ratio", data["avg_opd_ipd_ratio"], now_iso))
                    synced_sectors["healthcare"] = data

                elif sec == "clinical":
                    cursor.execute(upsert_sql, ("Clinical EHR Readmission", data["total_patients_analyzed"], "readmission_rate_pct", data["readmission_rate_pct"], "avg_hospital_stay_days", data["avg_hospital_stay_days"], now_iso))
                    synced_sectors["clinical"] = data

                elif sec == "insurance":
                    cursor.execute(upsert_sql, ("Insurance Claims Fraud", data["total_claims_processed"], "claims_fraud_rate_pct", data["claims_fraud_rate_pct"], "total_claim_amount_usd", data["total_claim_amount_usd"], now_iso))
                    synced_sectors["insurance"] = data

                elif sec == "retail":
                    cursor.execute(upsert_sql, ("Retail Sales & Demand", data["total_invoices"], "gross_revenue_usd", data["gross_revenue_usd"], "total_items_sold", float(data["total_items_sold"]), now_iso))
                    synced_sectors["retail"] = data

        conn.commit()
        conn.close()

        print(f"[PostgresGoldSync] Synced {len(synced_sectors)} Gold Data Marts via Engine: {engine_name}")
        return {
            "status": "SUCCESS",
            "database_engine": engine_name,
            "synced_sectors_count": len(synced_sectors),
            "synced_sectors": list(synced_sectors.keys())
        }


if __name__ == "__main__":
    sync = PostgresGoldSync()
    res = sync.sync_all_marts()
    print(res)
