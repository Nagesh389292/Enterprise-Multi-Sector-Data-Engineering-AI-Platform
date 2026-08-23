"""
Enterprise Data Quality & Validation Rules Module.
Defines reusable validation primitives and rule definitions across all business domains.
"""

from typing import Any, Dict, List, Optional, Tuple, Callable
from datetime import datetime
import re

class ValidationRule:
    """Base class for validation rules."""
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def validate(self, record: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        raise NotImplementedError


class RequiredFieldsRule(ValidationRule):
    """Ensures all required fields exist and are non-null."""
    def __init__(self, required_fields: List[str]):
        super().__init__(
            name="REQUIRED_FIELDS",
            description=f"Fields {required_fields} must be present and non-null"
        )
        self.required_fields = required_fields

    def validate(self, record: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        missing = [f for f in self.required_fields if f not in record or record[f] is None or record[f] == ""]
        if missing:
            return False, f"Missing or null required fields: {missing}"
        return True, None


class DataTypeRule(ValidationRule):
    """Validates data types for specified fields."""
    def __init__(self, type_mapping: Dict[str, type]):
        super().__init__(
            name="DATA_TYPES",
            description="Validates target field data types"
        )
        self.type_mapping = type_mapping

    def validate(self, record: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        invalid = []
        for field, expected_type in self.type_mapping.items():
            if field in record and record[field] is not None:
                val = record[field]
                if expected_type in (int, float):
                    try:
                        expected_type(val)
                    except (ValueError, TypeError):
                        invalid.append(f"{field} (expected {expected_type.__name__}, got {type(val).__name__})")
                elif expected_type == datetime:
                    if not isinstance(val, datetime):
                        try:
                            datetime.fromisoformat(str(val))
                        except ValueError:
                            invalid.append(f"{field} invalid datetime format '{val}'")
                elif not isinstance(val, expected_type):
                    invalid.append(f"{field} (expected {expected_type.__name__}, got {type(val).__name__})")
        if invalid:
            return False, f"Invalid data types: {', '.join(invalid)}"
        return True, None


class RangeRule(ValidationRule):
    """Validates numeric range boundaries."""
    def __init__(self, field: str, min_val: Optional[float] = None, max_val: Optional[float] = None):
        super().__init__(
            name=f"RANGE_{field.upper()}",
            description=f"Field {field} must be between {min_val} and {max_val}"
        )
        self.field = field
        self.min_val = min_val
        self.max_val = max_val

    def validate(self, record: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        if self.field not in record or record[self.field] is None:
            return True, None  # Let RequiredFieldsRule handle null checks if mandatory
        
        try:
            val = float(record[self.field])
            if self.min_val is not None and val < self.min_val:
                return False, f"Field '{self.field}' value {val} is below minimum allowed {self.min_val}"
            if self.max_val is not None and val > self.max_val:
                return False, f"Field '{self.field}' value {val} is above maximum allowed {self.max_val}"
        except (ValueError, TypeError):
            return False, f"Field '{self.field}' value '{record[self.field]}' is not numeric for range check"
            
        return True, None


class CustomBusinessRule(ValidationRule):
    """Custom lambda/function for domain-specific business validation."""
    def __init__(self, name: str, description: str, validator_fn: Callable[[Dict[str, Any]], Tuple[bool, str]]):
        super().__init__(name=name, description=description)
        self.validator_fn = validator_fn

    def validate(self, record: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        try:
            passed, msg = self.validator_fn(record)
            if not passed:
                return False, msg
            return True, None
        except Exception as e:
            return False, f"Error evaluating business rule {self.name}: {str(e)}"
