"""
Synthetic Data Generator for 6 Enterprise Business Domains.
Generates realistic datasets with intentional edge cases to test validation and quarantine pipelines.
"""

import random
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any

# Domain Options
CARD_TYPES = ["VISA", "MASTERCARD", "AMEX", "DISCOVER", "RUPAY"]
ACCOUNT_TYPES = ["SAVINGS", "CHECKING", "LOAN", "INVESTMENT"]
INSURANCE_TYPES = ["HEALTH", "AUTO", "PROPERTY", "LIFE"]
DEPARTMENTS = ["EMERGENCY", "CARDIOLOGY", "NEUROLOGY", "ORTHOPEDICS", "PEDIATRICS"]
DIAGNOSES = ["E11.9", "I10", "J44.9", "J18.9", "I50.9"]  # ICD-10 codes
PRODUCT_CATEGORIES = ["ELECTRONICS", "APPAREL", "HOME", "BEAUTY", "GROCERY"]


def generate_credit_card_data(count: int = 500, corrupt_rate: float = 0.05) -> List[Dict[str, Any]]:
    records = []
    base_time = datetime.now(timezone.utc) - timedelta(days=30)

    for i in range(1, count + 1):
        is_corrupt = random.random() < corrupt_rate
        rec_id = f"TXN_{100000 + i}"
        cust_id = f"CUST_{random.randint(1000, 1999)}"
        amount = round(random.uniform(5.0, 5000.0), 2)
        card_type = random.choice(CARD_TYPES)
        timestamp = (base_time + timedelta(minutes=random.randint(1, 43200))).isoformat()
        is_fraud = random.choices([0, 1], weights=[0.95, 0.05])[0]

        # Inject corrupt patterns for quarantine testing
        if is_corrupt:
            corrupt_type = random.choice(["negative_amount", "invalid_card", "null_customer"])
            if corrupt_type == "negative_amount":
                amount = -150.00
            elif corrupt_type == "invalid_card":
                card_type = "INVALID_BRAND"
            elif corrupt_type == "null_customer":
                cust_id = ""

        records.append({
            "transaction_id": rec_id,
            "customer_id": cust_id,
            "amount": amount,
            "card_type": card_type,
            "timestamp": timestamp,
            "merchant_category": random.choice(["RETAIL", "TRAVEL", "DINING", "ENTERTAINMENT", "SERVICES"]),
            "is_fraud": is_fraud
        })
    return records


def generate_banking_data(count: int = 300, corrupt_rate: float = 0.05) -> List[Dict[str, Any]]:
    records = []
    for i in range(1, count + 1):
        is_corrupt = random.random() < corrupt_rate
        acc_id = f"ACC_{200000 + i}"
        cust_id = f"CUST_{random.randint(1000, 1999)}"
        acc_type = random.choice(ACCOUNT_TYPES)
        balance = round(random.uniform(100.0, 250000.0), 2)
        credit_score = random.randint(350, 850)
        loan_amount = round(random.uniform(1000.0, 50000.0), 2) if acc_type == "LOAN" else 0.0
        is_default = random.choices([0, 1], weights=[0.90, 0.10])[0] if acc_type == "LOAN" else 0

        if is_corrupt:
            credit_score = 1200  # Invalid > 900

        records.append({
            "account_id": acc_id,
            "customer_id": cust_id,
            "account_type": acc_type,
            "balance": balance,
            "credit_score": credit_score,
            "loan_amount": loan_amount,
            "is_default": is_default
        })
    return records


def generate_insurance_data(count: int = 300) -> List[Dict[str, Any]]:
    records = []
    base_time = datetime.now(timezone.utc) - timedelta(days=60)
    for i in range(1, count + 1):
        claim_id = f"CLM_{300000 + i}"
        policy_id = f"POL_{random.randint(5000, 5999)}"
        claim_amount = round(random.uniform(500.0, 75000.0), 2)
        policy_type = random.choice(INSURANCE_TYPES)
        claim_date = (base_time + timedelta(days=random.randint(1, 60))).strftime("%Y-%m-%d")
        fraud_suspicion = random.choices([0, 1], weights=[0.92, 0.08])[0]

        descriptions = [
            "Vehicle collision damage at intersection",
            "Water leakage damage to property kitchen",
            "Medical hospitalization for surgical procedure",
            "Stolen electronic items from residential apartment"
        ]

        records.append({
            "claim_id": claim_id,
            "policy_id": policy_id,
            "policy_type": policy_type,
            "claim_amount": claim_amount,
            "claim_date": claim_date,
            "fraud_suspicion": fraud_suspicion,
            "description": random.choice(descriptions)
        })
    return records


def generate_healthcare_data(count: int = 300) -> List[Dict[str, Any]]:
    records = []
    base_time = datetime.now(timezone.utc) - timedelta(days=90)
    for i in range(1, count + 1):
        adm_id = f"ADM_{400000 + i}"
        patient_id = f"PAT_{random.randint(7000, 7999)}"
        department = random.choice(DEPARTMENTS)
        length_of_stay = random.randint(1, 21)
        treatment_cost = round(length_of_stay * random.uniform(1200.0, 3500.0), 2)
        adm_date = (base_time + timedelta(days=random.randint(1, 90))).strftime("%Y-%m-%d")

        records.append({
            "admission_id": adm_id,
            "patient_id": patient_id,
            "department": department,
            "admission_date": adm_date,
            "length_of_stay_days": length_of_stay,
            "treatment_cost": treatment_cost
        })
    return records


def generate_clinical_data(count: int = 300) -> List[Dict[str, Any]]:
    records = []
    for i in range(1, count + 1):
        enc_id = f"ENC_{500000 + i}"
        patient_id = f"PAT_{random.randint(7000, 7999)}"
        diagnosis_code = random.choice(DIAGNOSES)
        readmitted_30d = random.choices([0, 1], weights=[0.82, 0.18])[0]
        days_to_event = random.randint(1, 180) if readmitted_30d else random.randint(30, 365)
        charlson_index = random.randint(0, 8)

        records.append({
            "encounter_id": enc_id,
            "patient_id": patient_id,
            "diagnosis_code": diagnosis_code,
            "readmitted_30d": readmitted_30d,
            "days_to_event": days_to_event,
            "charlson_comorbidity_index": charlson_index
        })
    return records


def generate_retail_data(count: int = 400) -> List[Dict[str, Any]]:
    records = []
    base_time = datetime.now(timezone.utc) - timedelta(days=45)
    for i in range(1, count + 1):
        order_id = f"ORD_{600000 + i}"
        cust_id = f"CUST_{random.randint(1000, 1999)}"
        product_id = f"PROD_{random.randint(50, 99)}"
        category = random.choice(PRODUCT_CATEGORIES)
        quantity = random.randint(1, 5)
        unit_price = round(random.uniform(15.0, 1200.0), 2)
        order_date = (base_time + timedelta(days=random.randint(1, 45))).strftime("%Y-%m-%d")

        records.append({
            "order_id": order_id,
            "customer_id": cust_id,
            "product_id": product_id,
            "product_category": category,
            "quantity": quantity,
            "unit_price": unit_price,
            "total_price": round(quantity * unit_price, 2),
            "order_date": order_date
        })
    return records
