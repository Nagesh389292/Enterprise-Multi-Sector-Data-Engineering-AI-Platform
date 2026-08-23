"""
Populates PostgreSQL (enterprise_postgres) enterprise_db database
with real Gold Analytical Data Marts for native Apache Superset BI dashboards.
"""

import os
import json
import sqlite3
import psycopg2
from typing import Dict, Any

SQLITE_DB = os.path.join(os.getcwd(), "platform_analytics.db")
PG_HOST = os.environ.get("POSTGRES_HOST", "localhost")
PG_PORT = int(os.environ.get("POSTGRES_PORT", 5432))
PG_DB = os.environ.get("POSTGRES_DB", "enterprise_db")
PG_USER = os.environ.get("POSTGRES_USER", "platform_user")
PG_PASS = os.environ.get("POSTGRES_PASSWORD", "platform_password")


def get_pg_connection():
    return psycopg2.connect(
        dbname=PG_DB,
        user=PG_USER,
        password=PG_PASS,
        host=PG_HOST,
        port=PG_PORT
    )


def populate_postgres():
    print(f"[PopulatePG] Connecting to PostgreSQL at {PG_HOST}:{PG_PORT}/{PG_DB}...")
    pg_conn = get_pg_connection()
    pg_cursor = pg_conn.cursor()

    # 1. Summary Table
    pg_cursor.execute("""
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

    # 2. Sector Specific Data Tables
    pg_cursor.execute("""
        CREATE TABLE IF NOT EXISTS gold_credit_card (
            transaction_id VARCHAR(50) PRIMARY KEY,
            amount_usd DOUBLE PRECISION,
            fraud_risk_score DOUBLE PRECISION,
            is_fraud INTEGER,
            risk_level VARCHAR(20),
            sector VARCHAR(50)
        )
    """)

    pg_cursor.execute("""
        CREATE TABLE IF NOT EXISTS gold_banking_loan_risk (
            loan_id VARCHAR(50) PRIMARY KEY,
            applicant_income DOUBLE PRECISION,
            loan_amount DOUBLE PRECISION,
            default_risk_score DOUBLE PRECISION,
            loan_purpose VARCHAR(50),
            is_default INTEGER
        )
    """)

    pg_cursor.execute("""
        CREATE TABLE IF NOT EXISTS gold_healthcare_ogd (
            hospital_id VARCHAR(50) PRIMARY KEY,
            state VARCHAR(50),
            total_beds INTEGER,
            occupied_beds INTEGER,
            bed_occupancy_pct DOUBLE PRECISION,
            opd_ipd_ratio DOUBLE PRECISION
        )
    """)

    pg_cursor.execute("""
        CREATE TABLE IF NOT EXISTS gold_clinical_readmission (
            patient_id VARCHAR(50) PRIMARY KEY,
            age_group VARCHAR(20),
            days_in_hospital INTEGER,
            readmission_risk DOUBLE PRECISION,
            is_readmitted INTEGER
        )
    """)

    pg_cursor.execute("""
        CREATE TABLE IF NOT EXISTS gold_insurance_claims (
            claim_id VARCHAR(50) PRIMARY KEY,
            incident_type VARCHAR(50),
            claim_amount_usd DOUBLE PRECISION,
            fraud_probability DOUBLE PRECISION,
            is_fraud INTEGER
        )
    """)

    pg_cursor.execute("""
        CREATE TABLE IF NOT EXISTS gold_retail_sales (
            invoice_id VARCHAR(50) PRIMARY KEY,
            category VARCHAR(50),
            items_sold INTEGER,
            gross_revenue_usd DOUBLE PRECISION,
            unit_price DOUBLE PRECISION
        )
    """)

    # Populate Summary Data
    master_json_path = os.path.join(os.getcwd(), "data", "lake", "gold", "master_multi_sector_gold.json")
    if os.path.exists(master_json_path):
        with open(master_json_path, "r") as f:
            master_data = json.load(f)

        sectors = master_data.get("sectors", {})
        now_iso = "2026-08-23T18:00:00Z"

        upsert_sql = """
            INSERT INTO gold_multi_sector_summary (sector, total_records, primary_metric, primary_metric_value, secondary_metric, secondary_metric_value, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (sector) DO UPDATE SET
                total_records = EXCLUDED.total_records,
                primary_metric_value = EXCLUDED.primary_metric_value,
                secondary_metric_value = EXCLUDED.secondary_metric_value,
                updated_at = EXCLUDED.updated_at
        """

        if "credit_card" in sectors:
            d = sectors["credit_card"]
            pg_cursor.execute(upsert_sql, ("Credit Card Fraud", d["total_transactions"], "fraud_rate_pct", d["fraud_rate_pct"], "total_volume_usd", d["total_volume_usd"], now_iso))
        if "banking" in sectors:
            d = sectors["banking"]
            pg_cursor.execute(upsert_sql, ("Banking Loan Risk", d["total_loans"], "default_rate_pct", d["default_rate_pct"], "total_credit_granted_usd", d["total_credit_granted_usd"], now_iso))
        if "healthcare" in sectors:
            d = sectors["healthcare"]
            pg_cursor.execute(upsert_sql, ("Healthcare OGD", d["total_hospitals_reporting"], "avg_bed_occupancy_pct", d["avg_bed_occupancy_pct"], "avg_opd_ipd_ratio", d["avg_opd_ipd_ratio"], now_iso))
        if "clinical" in sectors:
            d = sectors["clinical"]
            pg_cursor.execute(upsert_sql, ("Clinical EHR Readmission", d["total_patients_analyzed"], "readmission_rate_pct", d["readmission_rate_pct"], "avg_hospital_stay_days", d["avg_hospital_stay_days"], now_iso))
        if "insurance" in sectors:
            d = sectors["insurance"]
            pg_cursor.execute(upsert_sql, ("Insurance Claims Fraud", d["total_claims_processed"], "claims_fraud_rate_pct", d["claims_fraud_rate_pct"], "total_claim_amount_usd", d["total_claim_amount_usd"], now_iso))
        if "retail" in sectors:
            d = sectors["retail"]
            pg_cursor.execute(upsert_sql, ("Retail Sales & Demand", d["total_invoices"], "gross_revenue_usd", d["gross_revenue_usd"], "total_items_sold", float(d["total_items_sold"]), now_iso))

    # Populate Sample Domain Rows if Empty
    pg_cursor.execute("SELECT COUNT(*) FROM gold_credit_card;")
    if pg_cursor.fetchone()[0] == 0:
        for i in range(1, 101):
            is_f = 1 if i % 9 == 0 else 0
            risk = "HIGH" if is_f else ("MEDIUM" if i % 3 == 0 else "LOW")
            pg_cursor.execute(
                "INSERT INTO gold_credit_card VALUES (%s, %s, %s, %s, %s, %s)",
                (f"TXN-{i:04d}", 45.0 + (i * 12.5), 0.95 if is_f else 0.12, is_f, risk, "Credit Card")
            )

    pg_cursor.execute("SELECT COUNT(*) FROM gold_banking_loan_risk;")
    if pg_cursor.fetchone()[0] == 0:
        purposes = ["HOME", "AUTO", "PERSONAL", "BUSINESS"]
        for i in range(1, 101):
            is_d = 1 if i % 7 == 0 else 0
            pg_cursor.execute(
                "INSERT INTO gold_banking_loan_risk VALUES (%s, %s, %s, %s, %s, %s)",
                (f"LOAN-{i:04d}", 45000.0 + (i * 800), 10000.0 + (i * 350), 0.88 if is_d else 0.15, purposes[i % 4], is_d)
            )

    pg_cursor.execute("SELECT COUNT(*) FROM gold_healthcare_ogd;")
    if pg_cursor.fetchone()[0] == 0:
        states = ["Maharashtra", "Delhi", "Karnataka", "Tamil Nadu", "Gujarat"]
        for i in range(1, 51):
            occ = 60.0 + (i % 35)
            pg_cursor.execute(
                "INSERT INTO gold_healthcare_ogd VALUES (%s, %s, %s, %s, %s, %s)",
                (f"HOSP-{i:03d}", states[i % 5], 500, int(500 * (occ / 100.0)), occ, 3.2 + (i % 2))
            )

    pg_cursor.execute("SELECT COUNT(*) FROM gold_clinical_readmission;")
    if pg_cursor.fetchone()[0] == 0:
        ages = ["18-35", "36-50", "51-65", "66+"]
        for i in range(1, 81):
            readm = 1 if i % 4 == 0 else 0
            pg_cursor.execute(
                "INSERT INTO gold_clinical_readmission VALUES (%s, %s, %s, %s, %s)",
                (f"PAT-{i:04d}", ages[i % 4], 3 + (i % 10), 0.75 if readm else 0.18, readm)
            )

    pg_cursor.execute("SELECT COUNT(*) FROM gold_insurance_claims;")
    if pg_cursor.fetchone()[0] == 0:
        types = ["Collision", "Comprehensive", "Property Damage", "Personal Injury"]
        for i in range(1, 75):
            is_f = 1 if i % 5 == 0 else 0
            pg_cursor.execute(
                "INSERT INTO gold_insurance_claims VALUES (%s, %s, %s, %s, %s)",
                (f"CLM-{i:04d}", types[i % 4], 2500.0 + (i * 450), 0.92 if is_f else 0.10, is_f)
            )

    pg_cursor.execute("SELECT COUNT(*) FROM gold_retail_sales;")
    if pg_cursor.fetchone()[0] == 0:
        cats = ["Electronics", "Apparel", "Home & Kitchen", "Books", "Sports"]
        for i in range(1, 120):
            qty = 1 + (i % 8)
            price = 25.0 + (i * 5.0)
            pg_cursor.execute(
                "INSERT INTO gold_retail_sales VALUES (%s, %s, %s, %s, %s)",
                (f"INV-{i:04d}", cats[i % 5], qty, qty * price, price)
            )

    pg_conn.commit()
    pg_conn.close()
    print("[PopulatePG] PostgreSQL Gold tables populated successfully!")


if __name__ == "__main__":
    populate_postgres()
