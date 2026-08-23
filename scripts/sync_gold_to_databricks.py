"""
Databricks Multi-Sector Gold Data Sync & Reconciliation Script.

1. Reads canonical local Gold Lakehouse metrics from master_multi_sector_gold.json
2. Syncs/upserts 6 multi-sector Gold Data Marts into Databricks SQL Warehouse
3. Performs strict reconciliation comparing Databricks values to canonical local values.
   (Tolerance: 0.01%)

Usage:
    python scripts/sync_gold_to_databricks.py
"""

import sys
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_engineering.databricks.gold_sync import DatabricksGoldSync
from data_engineering.databricks.health import DatabricksHealthChecker


def main():
    print("=" * 65)
    print("  DATABRICKS GOLD DATA SYNC & RECONCILIATION")
    print("=" * 65)

    checker = DatabricksHealthChecker()
    configured = checker.check_workspace_configured()
    if configured["status"] != "PASS":
        print(f"\n[FAIL] Pre-flight FAIL: {configured['detail']}")
        print("       Set DATABRICKS_TOKEN or DATABRICKS_CLIENT_ID/CLIENT_SECRET in your .env file.")
        sys.exit(1)

    syncer = DatabricksGoldSync()

    print("\n[Gold Sync] Uploading canonical local Gold data to Databricks SQL Warehouse...")
    sync_res = syncer.sync_gold_to_databricks()

    if not sync_res["success"]:
        print(f"  [FAIL] Sync failed: {sync_res.get('detail', 'Unknown error')}")
        sys.exit(1)

    print(f"  [PASS] Successfully synced {sync_res['sectors_synced']}/{sync_res['sectors_total']} sectors to:")
    print(f"         {sync_res['target_table']}")

    print("\n[Reconciliation] Reconciling Databricks Gold against canonical local metrics...")
    rec_res = syncer.reconcile_gold_metrics()

    print(f"  Matched:    {rec_res['sectors_matched']}/{rec_res['sectors_checked']} sectors")
    print(f"  Mismatched: {rec_res['sectors_mismatched']} sectors")

    if rec_res["mismatches"]:
        print("\n  [FAIL] Mismatches detected:")
        for m in rec_res["mismatches"]:
            print(f"    - {m['sector']}: Local={m.get('local_value')} vs Databricks={m.get('databricks_value')} ({m.get('reason')})")

    print("\n" + "=" * 65)
    badge = "[PASS]" if rec_res["success"] else "[FAIL]"
    print(f"  {badge}  RECONCILIATION: {rec_res['detail']}")
    print("=" * 65 + "\n")

    sys.exit(0 if rec_res["success"] else 1)


if __name__ == "__main__":
    main()
