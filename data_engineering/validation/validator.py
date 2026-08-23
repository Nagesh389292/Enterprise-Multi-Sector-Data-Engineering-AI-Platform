"""
Enterprise Data Quality Engine & Schema Validator.
Applies domain-specific rules, handles quarantine routing, and generates data quality telemetry.
"""

from typing import Any, Dict, List, Tuple
from datetime import datetime, timezone
import json
import uuid
from data_engineering.validation.rules import (
    ValidationRule,
    RequiredFieldsRule,
    DataTypeRule,
    RangeRule,
    CustomBusinessRule
)

class ValidationResult:
    def __init__(self, record_id: str, is_valid: bool, errors: List[str], raw_payload: Dict[str, Any]):
        self.record_id = record_id
        self.is_valid = is_valid
        self.errors = errors
        self.raw_payload = raw_payload
        self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_quarantine_dict(self) -> Dict[str, Any]:
        return {
            "quarantine_id": str(uuid.uuid4()),
            "record_id": self.record_id,
            "timestamp": self.timestamp,
            "failure_reasons": self.errors,
            "error_count": len(self.errors),
            "status": "QUARANTINED",
            "source_payload": self.raw_payload
        }


class DataQualityEngine:
    """Core engine for record validation and quarantine routing."""
    def __init__(self, domain: str, primary_key: str, rules: List[ValidationRule]):
        self.domain = domain
        self.primary_key = primary_key
        self.rules = rules
        self._seen_keys = set()

    def validate_record(self, record: Dict[str, Any]) -> ValidationResult:
        rec_id = str(record.get(self.primary_key, f"UNKNOWN_{uuid.uuid4().hex[:8]}"))
        errors = []

        # Duplicate check
        if rec_id in self._seen_keys:
            errors.append(f"Duplicate primary key '{self.primary_key}': {rec_id}")
        else:
            self._seen_keys.add(rec_id)

        # Run configured rules
        for rule in self.rules:
            passed, err_msg = rule.validate(record)
            if not passed and err_msg:
                errors.append(err_msg)

        is_valid = len(errors) == 0
        return ValidationResult(record_id=rec_id, is_valid=is_valid, errors=errors, raw_payload=record)

    def process_batch(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        valid_records = []
        quarantine_records = []
        rule_failure_counts: Dict[str, int] = {}

        for rec in records:
            res = self.validate_record(rec)
            if res.is_valid:
                valid_records.append(rec)
            else:
                quarantine_records.append(res.to_quarantine_dict())
                for err in res.errors:
                    rule_key = err.split(":")[0] if ":" in err else "GENERAL_ERROR"
                    rule_failure_counts[rule_key] = rule_failure_counts.get(rule_key, 0) + 1

        total = len(records)
        passed = len(valid_records)
        quarantined = len(quarantine_records)
        compliance_rate = (passed / total * 100) if total > 0 else 100.0

        return {
            "domain": self.domain,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "telemetry": {
                "total_records": total,
                "passed_records": passed,
                "quarantined_records": quarantined,
                "compliance_rate_pct": round(compliance_rate, 2),
                "rule_failure_breakdown": rule_failure_counts
            },
            "valid_records": valid_records,
            "quarantine_records": quarantine_records
        }


# --- Domain Rule Specs ---

def get_credit_card_validator() -> DataQualityEngine:
    rules = [
        RequiredFieldsRule(["transaction_id", "customer_id", "amount", "timestamp", "card_type"]),
        DataTypeRule({"amount": float, "customer_id": str, "transaction_id": str}),
        RangeRule("amount", min_val=0.01, max_val=1000000.0),
        CustomBusinessRule(
            name="VALID_CARD_TYPE",
            description="Card type must be valid credit card brand",
            validator_fn=lambda r: (r.get("card_type") in ["VISA", "MASTERCARD", "AMEX", "DISCOVER", "RUPAY"], "Invalid card type brand")
        )
    ]
    return DataQualityEngine(domain="credit_cards", primary_key="transaction_id", rules=rules)


def get_banking_validator() -> DataQualityEngine:
    rules = [
        RequiredFieldsRule(["account_id", "customer_id", "account_type", "balance", "credit_score"]),
        DataTypeRule({"balance": float, "credit_score": int}),
        RangeRule("credit_score", min_val=300, max_val=900),
        RangeRule("balance", min_val=-50000.0, max_val=100000000.0),
        CustomBusinessRule(
            name="VALID_ACCOUNT_TYPE",
            description="Account type must be SAVINGS, CHECKING, LOAN, or INVESTMENT",
            validator_fn=lambda r: (r.get("account_type") in ["SAVINGS", "CHECKING", "LOAN", "INVESTMENT"], "Invalid account type")
        )
    ]
    return DataQualityEngine(domain="banking", primary_key="account_id", rules=rules)


def get_insurance_validator() -> DataQualityEngine:
    rules = [
        RequiredFieldsRule(["claim_id", "policy_id", "claim_amount", "claim_date", "policy_type"]),
        DataTypeRule({"claim_amount": float}),
        RangeRule("claim_amount", min_val=0.0, max_val=5000000.0),
    ]
    return DataQualityEngine(domain="insurance", primary_key="claim_id", rules=rules)


def get_healthcare_validator() -> DataQualityEngine:
    rules = [
        RequiredFieldsRule(["patient_id", "admission_id", "department", "admission_date", "treatment_cost"]),
        DataTypeRule({"treatment_cost": float}),
        RangeRule("treatment_cost", min_val=0.0, max_val=2000000.0),
    ]
    return DataQualityEngine(domain="healthcare", primary_key="admission_id", rules=rules)


def get_clinical_validator() -> DataQualityEngine:
    rules = [
        RequiredFieldsRule(["encounter_id", "patient_id", "diagnosis_code", "readmitted_30d"]),
        DataTypeRule({"readmitted_30d": int}),
        RangeRule("readmitted_30d", min_val=0, max_val=1),
    ]
    return DataQualityEngine(domain="clinical", primary_key="encounter_id", rules=rules)


def get_retail_validator() -> DataQualityEngine:
    rules = [
        RequiredFieldsRule(["order_id", "customer_id", "product_id", "quantity", "unit_price"]),
        DataTypeRule({"quantity": int, "unit_price": float}),
        RangeRule("quantity", min_val=1, max_val=10000),
        RangeRule("unit_price", min_val=0.0, max_val=500000.0),
    ]
    return DataQualityEngine(domain="retail", primary_key="order_id", rules=rules)
