"""
Unit tests for Data Quality Engine & Schema Validation Framework.
"""

import pytest
from data_engineering.validation.validator import (
    get_credit_card_validator,
    get_banking_validator,
    get_healthcare_validator
)

def test_credit_card_validation_pass():
    validator = get_credit_card_validator()
    records = [
        {
            "transaction_id": "TXN_001",
            "customer_id": "CUST_100",
            "amount": 250.50,
            "timestamp": "2026-08-22T10:00:00Z",
            "card_type": "VISA"
        },
        {
            "transaction_id": "TXN_002",
            "customer_id": "CUST_101",
            "amount": 1200.00,
            "timestamp": "2026-08-22T10:05:00Z",
            "card_type": "MASTERCARD"
        }
    ]
    result = validator.process_batch(records)
    assert result["telemetry"]["total_records"] == 2
    assert result["telemetry"]["passed_records"] == 2
    assert result["telemetry"]["quarantined_records"] == 0
    assert result["telemetry"]["compliance_rate_pct"] == 100.0


def test_credit_card_validation_quarantine():
    validator = get_credit_card_validator()
    records = [
        # Good record
        {
            "transaction_id": "TXN_001",
            "customer_id": "CUST_100",
            "amount": 250.50,
            "timestamp": "2026-08-22T10:00:00Z",
            "card_type": "VISA"
        },
        # Bad record 1: Negative amount & Invalid card type
        {
            "transaction_id": "TXN_002",
            "customer_id": "CUST_101",
            "amount": -50.00,
            "timestamp": "2026-08-22T10:05:00Z",
            "card_type": "INVALID_BRAND"
        },
        # Bad record 2: Missing required customer_id
        {
            "transaction_id": "TXN_003",
            "customer_id": "",
            "amount": 100.00,
            "timestamp": "2026-08-22T10:10:00Z",
            "card_type": "AMEX"
        },
        # Bad record 3: Duplicate transaction_id
        {
            "transaction_id": "TXN_001",
            "customer_id": "CUST_104",
            "amount": 500.00,
            "timestamp": "2026-08-22T10:15:00Z",
            "card_type": "DISCOVER"
        }
    ]
    result = validator.process_batch(records)
    assert result["telemetry"]["total_records"] == 4
    assert result["telemetry"]["passed_records"] == 1
    assert result["telemetry"]["quarantined_records"] == 3
    assert result["telemetry"]["compliance_rate_pct"] == 25.0

    # Verify quarantine structure
    quarantine = result["quarantine_records"]
    assert len(quarantine) == 3
    assert any("Duplicate primary key" in q["failure_reasons"][0] for q in quarantine)


def test_banking_validation_range_and_business_rules():
    validator = get_banking_validator()
    records = [
        # Valid banking record
        {
            "account_id": "ACC_1001",
            "customer_id": "CUST_500",
            "account_type": "SAVINGS",
            "balance": 15000.00,
            "credit_score": 750
        },
        # Invalid credit score out of range
        {
            "account_id": "ACC_1002",
            "customer_id": "CUST_501",
            "account_type": "CHECKING",
            "balance": 500.00,
            "credit_score": 1500  # max 900
        }
    ]
    result = validator.process_batch(records)
    assert result["telemetry"]["passed_records"] == 1
    assert result["telemetry"]["quarantined_records"] == 1
