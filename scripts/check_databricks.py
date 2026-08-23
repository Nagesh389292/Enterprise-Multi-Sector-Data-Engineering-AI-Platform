"""
Databricks Platform Health Check Script.

Checks all Databricks configuration and connectivity layers
WITHOUT starting compute or executing SQL.

Run this first to confirm configuration before running verify_databricks_runtime.py.

Usage:
    python scripts/check_databricks.py
"""

import sys
import os

# Load .env file if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_engineering.databricks.health import DatabricksHealthChecker


def main():
    checker = DatabricksHealthChecker()
    checker.print_report()

    report = checker.get_health_report()
    overall = report["overall"]

    if overall == "PASS":
        print("[PASS] All configuration and connectivity checks passed.")
        print("       Next step: python scripts/verify_databricks_runtime.py")
        sys.exit(0)
    else:
        print("[FAIL] One or more checks failed. Review the report above.")
        print("       Ensure DATABRICKS_TOKEN or DATABRICKS_CLIENT_ID/CLIENT_SECRET is set in your local .env file.")
        sys.exit(1)


if __name__ == "__main__":
    main()
