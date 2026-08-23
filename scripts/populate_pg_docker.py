"""
Populates enterprise_postgres directly via docker exec psql.
"""

import subprocess
import json
import os

def run_psql(sql: str):
    cmd = ["docker", "exec", "-i", "enterprise_postgres", "psql", "-U", "platform_user", "-d", "enterprise_db"]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = proc.communicate(input=sql)
    if proc.returncode != 0:
        print("PSQL Error:", err)
    return out

def populate():
    print("[DockerPG] Creating Gold tables in enterprise_postgres...")
    
    sql_schema = """
    CREATE TABLE IF NOT EXISTS gold_multi_sector_summary (
        sector VARCHAR(100) PRIMARY KEY,
        total_records INTEGER,
        primary_metric VARCHAR(100),
        primary_metric_value DOUBLE PRECISION,
        secondary_metric VARCHAR(100),
        secondary_metric_value DOUBLE PRECISION,
        updated_at VARCHAR(100)
    );

    CREATE TABLE IF NOT EXISTS gold_credit_card (
        transaction_id VARCHAR(50) PRIMARY KEY,
        amount_usd DOUBLE PRECISION,
        fraud_risk_score DOUBLE PRECISION,
        is_fraud INTEGER,
        risk_level VARCHAR(20),
        sector VARCHAR(50)
    );

    CREATE TABLE IF NOT EXISTS gold_banking_loan_risk (
        loan_id VARCHAR(50) PRIMARY KEY,
        applicant_income DOUBLE PRECISION,
        loan_amount DOUBLE PRECISION,
        default_risk_score DOUBLE PRECISION,
        loan_purpose VARCHAR(50),
        is_default INTEGER
    );

    CREATE TABLE IF NOT EXISTS gold_healthcare_ogd (
        hospital_id VARCHAR(50) PRIMARY KEY,
        state VARCHAR(50),
        total_beds INTEGER,
        occupied_beds INTEGER,
        bed_occupancy_pct DOUBLE PRECISION,
        opd_ipd_ratio DOUBLE PRECISION
    );

    CREATE TABLE IF NOT EXISTS gold_clinical_readmission (
        patient_id VARCHAR(50) PRIMARY KEY,
        age_group VARCHAR(20),
        days_in_hospital INTEGER,
        readmission_risk DOUBLE PRECISION,
        is_readmitted INTEGER
    );

    CREATE TABLE IF NOT EXISTS gold_insurance_claims (
        claim_id VARCHAR(50) PRIMARY KEY,
        incident_type VARCHAR(50),
        claim_amount_usd DOUBLE PRECISION,
        fraud_probability DOUBLE PRECISION,
        is_fraud INTEGER
    );

    CREATE TABLE IF NOT EXISTS gold_retail_sales (
        invoice_id VARCHAR(50) PRIMARY KEY,
        category VARCHAR(50),
        items_sold INTEGER,
        gross_revenue_usd DOUBLE PRECISION,
        unit_price DOUBLE PRECISION
    );
    """
    run_psql(sql_schema)

    # Insert summary
    master_json_path = os.path.join(os.getcwd(), "data", "lake", "gold", "master_multi_sector_gold.json")
    if os.path.exists(master_json_path):
        with open(master_json_path, "r") as f:
            master_data = json.load(f)

        sectors = master_data.get("sectors", {})
        now_iso = "2026-08-23T18:00:00Z"
        
        insert_sqls = []
        if "credit_card" in sectors:
            d = sectors["credit_card"]
            insert_sqls.append(f"INSERT INTO gold_multi_sector_summary VALUES ('Credit Card Fraud', {d['total_transactions']}, 'fraud_rate_pct', {d['fraud_rate_pct']}, 'total_volume_usd', {d['total_volume_usd']}, '{now_iso}') ON CONFLICT (sector) DO UPDATE SET primary_metric_value={d['fraud_rate_pct']};")
        if "banking" in sectors:
            d = sectors["banking"]
            insert_sqls.append(f"INSERT INTO gold_multi_sector_summary VALUES ('Banking Loan Risk', {d['total_loans']}, 'default_rate_pct', {d['default_rate_pct']}, 'total_credit_granted_usd', {d['total_credit_granted_usd']}, '{now_iso}') ON CONFLICT (sector) DO UPDATE SET primary_metric_value={d['default_rate_pct']};")
        if "healthcare" in sectors:
            d = sectors["healthcare"]
            insert_sqls.append(f"INSERT INTO gold_multi_sector_summary VALUES ('Healthcare OGD', {d['total_hospitals_reporting']}, 'avg_bed_occupancy_pct', {d['avg_bed_occupancy_pct']}, 'avg_opd_ipd_ratio', {d['avg_opd_ipd_ratio']}, '{now_iso}') ON CONFLICT (sector) DO UPDATE SET primary_metric_value={d['avg_bed_occupancy_pct']};")
        if "clinical" in sectors:
            d = sectors["clinical"]
            insert_sqls.append(f"INSERT INTO gold_multi_sector_summary VALUES ('Clinical EHR Readmission', {d['total_patients_analyzed']}, 'readmission_rate_pct', {d['readmission_rate_pct']}, 'avg_hospital_stay_days', {d['avg_hospital_stay_days']}, '{now_iso}') ON CONFLICT (sector) DO UPDATE SET primary_metric_value={d['readmission_rate_pct']};")
        if "insurance" in sectors:
            d = sectors["insurance"]
            insert_sqls.append(f"INSERT INTO gold_multi_sector_summary VALUES ('Insurance Claims Fraud', {d['total_claims_processed']}, 'claims_fraud_rate_pct', {d['claims_fraud_rate_pct']}, 'total_claim_amount_usd', {d['total_claim_amount_usd']}, '{now_iso}') ON CONFLICT (sector) DO UPDATE SET primary_metric_value={d['claims_fraud_rate_pct']};")
        if "retail" in sectors:
            d = sectors["retail"]
            insert_sqls.append(f"INSERT INTO gold_multi_sector_summary VALUES ('Retail Sales & Demand', {d['total_invoices']}, 'gross_revenue_usd', {d['gross_revenue_usd']}, 'total_items_sold', {float(d['total_items_sold'])}, '{now_iso}') ON CONFLICT (sector) DO UPDATE SET primary_metric_value={d['gross_revenue_usd']};")

        run_psql("\n".join(insert_sqls))

    # Insert sample domain rows
    cc_sqls = ["DELETE FROM gold_credit_card;"]
    for i in range(1, 101):
        is_f = 1 if i % 9 == 0 else 0
        risk = "HIGH" if is_f else ("MEDIUM" if i % 3 == 0 else "LOW")
        cc_sqls.append(f"INSERT INTO gold_credit_card VALUES ('TXN-{i:04d}', {45.0 + (i * 12.5)}, {0.95 if is_f else 0.12}, {is_f}, '{risk}', 'Credit Card');")
    run_psql("\n".join(cc_sqls))

    bank_sqls = ["DELETE FROM gold_banking_loan_risk;"]
    purposes = ["HOME", "AUTO", "PERSONAL", "BUSINESS"]
    for i in range(1, 101):
        is_d = 1 if i % 7 == 0 else 0
        bank_sqls.append(f"INSERT INTO gold_banking_loan_risk VALUES ('LOAN-{i:04d}', {45000.0 + (i * 800)}, {10000.0 + (i * 350)}, {0.88 if is_d else 0.15}, '{purposes[i % 4]}', {is_d});")
    run_psql("\n".join(bank_sqls))

    health_sqls = ["DELETE FROM gold_healthcare_ogd;"]
    states = ["Maharashtra", "Delhi", "Karnataka", "Tamil Nadu", "Gujarat"]
    for i in range(1, 51):
        occ = 60.0 + (i % 35)
        health_sqls.append(f"INSERT INTO gold_healthcare_ogd VALUES ('HOSP-{i:03d}', '{states[i % 5]}', 500, {int(500 * (occ / 100.0))}, {occ}, {3.2 + (i % 2)});")
    run_psql("\n".join(health_sqls))

    clin_sqls = ["DELETE FROM gold_clinical_readmission;"]
    ages = ["18-35", "36-50", "51-65", "66+"]
    for i in range(1, 81):
        readm = 1 if i % 4 == 0 else 0
        clin_sqls.append(f"INSERT INTO gold_clinical_readmission VALUES ('PAT-{i:04d}', '{ages[i % 4]}', {3 + (i % 10)}, {0.75 if readm else 0.18}, {readm});")
    run_psql("\n".join(clin_sqls))

    ins_sqls = ["DELETE FROM gold_insurance_claims;"]
    types = ["Collision", "Comprehensive", "Property Damage", "Personal Injury"]
    for i in range(1, 75):
        is_f = 1 if i % 5 == 0 else 0
        ins_sqls.append(f"INSERT INTO gold_insurance_claims VALUES ('CLM-{i:04d}', '{types[i % 4]}', {2500.0 + (i * 450)}, {0.92 if is_f else 0.10}, {is_f});")
    run_psql("\n".join(ins_sqls))

    retail_sqls = ["DELETE FROM gold_retail_sales;"]
    cats = ["Electronics", "Apparel", "Home & Kitchen", "Books", "Sports"]
    for i in range(1, 120):
        qty = 1 + (i % 8)
        price = 25.0 + (i * 5.0)
        retail_sqls.append(f"INSERT INTO gold_retail_sales VALUES ('INV-{i:04d}', '{cats[i % 5]}', {qty}, {qty * price}, {price});")
    run_psql("\n".join(retail_sqls))

    print("[DockerPG] Gold tables created and populated successfully inside enterprise_postgres!")

if __name__ == "__main__":
    populate()
