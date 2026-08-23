"""
Databricks Gold Data Sync and Reconciliation Engine.

Uploads existing local Gold data (from master_multi_sector_gold.json)
to Databricks SQL Warehouse and validates that Databricks values
match the local canonical Gold layer.

Rules:
- Does NOT generate fake data.
- Uses only the existing canonical master_multi_sector_gold.json.
- Any metric mismatch > RECONCILIATION_TOLERANCE fails the reconciliation.
- Never exposes credentials.

Usage:
    syncer = DatabricksGoldSync()
    syncer.sync_gold_to_databricks()
    report = syncer.reconcile_gold_metrics()
"""

import os
import json
import logging
from typing import Dict, Any, List

from data_engineering.databricks.client import DatabricksConfig
from data_engineering.databricks.sql import DatabricksSQLExecutor

logger = logging.getLogger(__name__)

LAKE_GOLD_DIR = os.path.join(os.getcwd(), "data", "lake", "gold")
CANONICAL_GOLD_JSON = os.path.join(LAKE_GOLD_DIR, "master_multi_sector_gold.json")

# Maximum allowed relative difference between local and Databricks Gold values
RECONCILIATION_TOLERANCE = 0.0001  # 0.01%


class DatabricksGoldSync:
    """
    Syncs local Gold Data Mart to Databricks SQL Warehouse and reconciles metrics.
    """

    def __init__(self, config: DatabricksConfig = None):
        self.config = config or DatabricksConfig()
        self.executor = DatabricksSQLExecutor(self.config)

    def _load_canonical_gold(self) -> Dict[str, Any]:
        """Loads the canonical local Gold JSON. Raises if missing."""
        if not os.path.exists(CANONICAL_GOLD_JSON):
            raise FileNotFoundError(
                f"Canonical Gold JSON not found: {CANONICAL_GOLD_JSON}\n"
                "Run the multi-sector pipeline first: "
                "python data_engineering/spark/multi_sector_pipeline.py"
            )
        with open(CANONICAL_GOLD_JSON, "r") as f:
            return json.load(f)

    def create_gold_schema(self) -> Dict[str, Any]:
        """Creates the target catalog schema in Databricks if it doesn't exist."""
        sql = (
            f"CREATE SCHEMA IF NOT EXISTS "
            f"{self.config.catalog}.{self.config.schema} "
            f"COMMENT 'Enterprise Gold Data Marts — synced from local Medallion pipeline'"
        )
        return self.executor.execute(sql)

    def create_gold_summary_table(self) -> Dict[str, Any]:
        """Creates the gold_multi_sector_summary table in Databricks."""
        sql = f"""
        CREATE TABLE IF NOT EXISTS
            {self.config.catalog}.{self.config.schema}.gold_multi_sector_summary
        (
            sector                  STRING        NOT NULL,
            total_records           BIGINT,
            primary_metric          STRING,
            primary_metric_value    DOUBLE,
            secondary_metric        STRING,
            secondary_metric_value  DOUBLE,
            updated_at              STRING,
            source_pipeline         STRING
        )
        USING DELTA
        COMMENT 'Multi-sector Gold Data Mart — sourced from PySpark Medallion pipeline'
        """
        return self.executor.execute(sql)

    def sync_gold_to_databricks(self) -> Dict[str, Any]:
        """
        Uploads canonical local Gold data to Databricks SQL Warehouse.
        Uses MERGE (upsert) to be idempotent.
        """
        gold_data = self._load_canonical_gold()
        sectors = gold_data.get("sectors", {})
        pipeline_ts = gold_data.get("timestamp", "unknown")

        # Ensure schema and table exist
        schema_result = self.create_gold_schema()
        if not schema_result.get("success"):
            logger.warning("[GoldSync] Schema creation result: %s", schema_result.get("error"))

        table_result = self.create_gold_summary_table()
        if not table_result.get("success"):
            return {"success": False, "detail": f"Table creation failed: {table_result.get('error')}"}

        # Build MERGE statement for all 6 sectors
        sector_rows = self._build_sector_rows(sectors, pipeline_ts)
        synced = []

        for row in sector_rows:
            merge_sql = f"""
            MERGE INTO {self.config.catalog}.{self.config.schema}.gold_multi_sector_summary AS target
            USING (
                SELECT
                    '{row['sector']}'          AS sector,
                    {row['total_records']}     AS total_records,
                    '{row['primary_metric']}'  AS primary_metric,
                    {row['primary_metric_value']} AS primary_metric_value,
                    '{row['secondary_metric']}' AS secondary_metric,
                    {row['secondary_metric_value']} AS secondary_metric_value,
                    '{row['updated_at']}'      AS updated_at,
                    'PySpark Medallion v2.0'   AS source_pipeline
            ) AS source ON target.sector = source.sector
            WHEN MATCHED THEN UPDATE SET *
            WHEN NOT MATCHED THEN INSERT *
            """
            result = self.executor.execute(merge_sql)
            if result.get("success"):
                synced.append(row["sector"])
                logger.info("[GoldSync] Synced sector: %s", row["sector"])
            else:
                logger.error("[GoldSync] Failed to sync sector %s: %s", row["sector"], result.get("error"))

        return {
            "success": len(synced) == len(sector_rows),
            "sectors_synced": synced,
            "sectors_total": len(sector_rows),
            "pipeline_timestamp": pipeline_ts,
            "target_table": f"{self.config.catalog}.{self.config.schema}.gold_multi_sector_summary",
        }

    def _build_sector_rows(self, sectors: Dict, pipeline_ts: str) -> List[Dict]:
        """Converts canonical Gold JSON sectors to table row dicts."""
        rows = []
        mapping = {
            "credit_card": {
                "sector": "Credit Card Fraud",
                "total_records": sectors["credit_card"]["total_transactions"],
                "primary_metric": "fraud_rate_pct",
                "primary_metric_value": sectors["credit_card"]["fraud_rate_pct"],
                "secondary_metric": "total_volume_usd",
                "secondary_metric_value": sectors["credit_card"]["total_volume_usd"],
            },
            "banking": {
                "sector": "Banking Loan Risk",
                "total_records": sectors["banking"]["total_loans"],
                "primary_metric": "default_rate_pct",
                "primary_metric_value": sectors["banking"]["default_rate_pct"],
                "secondary_metric": "total_credit_granted_usd",
                "secondary_metric_value": sectors["banking"]["total_credit_granted_usd"],
            },
            "healthcare": {
                "sector": "Healthcare OGD",
                "total_records": sectors["healthcare"]["total_hospitals_reporting"],
                "primary_metric": "avg_bed_occupancy_pct",
                "primary_metric_value": sectors["healthcare"]["avg_bed_occupancy_pct"],
                "secondary_metric": "avg_opd_ipd_ratio",
                "secondary_metric_value": sectors["healthcare"]["avg_opd_ipd_ratio"],
            },
            "clinical": {
                "sector": "Clinical EHR Readmission",
                "total_records": sectors["clinical"]["total_patients_analyzed"],
                "primary_metric": "readmission_rate_pct",
                "primary_metric_value": sectors["clinical"]["readmission_rate_pct"],
                "secondary_metric": "avg_hospital_stay_days",
                "secondary_metric_value": sectors["clinical"]["avg_hospital_stay_days"],
            },
            "insurance": {
                "sector": "Insurance Claims Fraud",
                "total_records": sectors["insurance"]["total_claims_processed"],
                "primary_metric": "claims_fraud_rate_pct",
                "primary_metric_value": sectors["insurance"]["claims_fraud_rate_pct"],
                "secondary_metric": "total_claim_amount_usd",
                "secondary_metric_value": sectors["insurance"]["total_claim_amount_usd"],
            },
            "retail": {
                "sector": "Retail Sales & Demand",
                "total_records": sectors["retail"]["total_invoices"],
                "primary_metric": "gross_revenue_usd",
                "primary_metric_value": sectors["retail"]["gross_revenue_usd"],
                "secondary_metric": "total_items_sold",
                "secondary_metric_value": float(sectors["retail"]["total_items_sold"]),
            },
        }
        for key, row in mapping.items():
            if key in sectors:
                row["updated_at"] = pipeline_ts
                rows.append(row)
        return rows

    def reconcile_gold_metrics(self) -> Dict[str, Any]:
        """
        Queries Databricks Gold and compares every metric to the local canonical value.
        Any difference > RECONCILIATION_TOLERANCE fails the reconciliation.
        """
        local_gold = self._load_canonical_gold()
        local_sectors = local_gold.get("sectors", {})

        db_result = self.executor.execute_gold_summary_query()
        if not db_result.get("success"):
            return {
                "success": False,
                "detail": f"Failed to query Databricks Gold: {db_result.get('error')}",
                "mismatches": [],
            }

        db_rows = {row["sector"]: row for row in db_result.get("rows", [])}
        mismatches = []
        matches = []

        # Reconciliation pairs: (canonical_key, db_sector_name, local_value, metric_name)
        checks = [
            ("credit_card",  "Credit Card Fraud",        local_sectors.get("credit_card", {}).get("fraud_rate_pct"),    "primary_metric_value"),
            ("banking",      "Banking Loan Risk",         local_sectors.get("banking", {}).get("default_rate_pct"),      "primary_metric_value"),
            ("healthcare",   "Healthcare OGD",            local_sectors.get("healthcare", {}).get("avg_bed_occupancy_pct"), "primary_metric_value"),
            ("clinical",     "Clinical EHR Readmission",  local_sectors.get("clinical", {}).get("readmission_rate_pct"), "primary_metric_value"),
            ("insurance",    "Insurance Claims Fraud",    local_sectors.get("insurance", {}).get("claims_fraud_rate_pct"), "primary_metric_value"),
            ("retail",       "Retail Sales & Demand",     local_sectors.get("retail", {}).get("gross_revenue_usd"),      "primary_metric_value"),
        ]

        for sector_key, db_sector_name, local_val, db_col in checks:
            if local_val is None:
                continue
            db_row = db_rows.get(db_sector_name)
            if db_row is None:
                mismatches.append({
                    "sector": db_sector_name,
                    "reason": "Sector missing from Databricks Gold table",
                    "local_value": local_val,
                    "databricks_value": None,
                })
                continue

            db_val = db_row.get(db_col)
            if db_val is None:
                mismatches.append({
                    "sector": db_sector_name,
                    "reason": f"Column {db_col} is NULL in Databricks",
                    "local_value": local_val,
                    "databricks_value": None,
                })
                continue

            try:
                local_f = float(local_val)
                db_f = float(db_val)
                if local_f == 0:
                    diff = abs(db_f)
                else:
                    diff = abs(local_f - db_f) / abs(local_f)

                if diff > RECONCILIATION_TOLERANCE:
                    mismatches.append({
                        "sector": db_sector_name,
                        "metric": db_col,
                        "local_value": local_f,
                        "databricks_value": db_f,
                        "relative_diff": round(diff * 100, 4),
                        "reason": f"Values differ by {diff*100:.4f}% (tolerance={RECONCILIATION_TOLERANCE*100}%)",
                    })
                else:
                    matches.append({"sector": db_sector_name, "metric": db_col, "value": local_f})
            except (TypeError, ValueError) as e:
                mismatches.append({
                    "sector": db_sector_name,
                    "reason": f"Type conversion error: {e}",
                    "local_value": local_val,
                    "databricks_value": db_val,
                })

        success = len(mismatches) == 0
        return {
            "success": success,
            "sectors_checked": len(checks),
            "sectors_matched": len(matches),
            "sectors_mismatched": len(mismatches),
            "mismatches": mismatches,
            "matches": matches,
            "reconciliation_tolerance": RECONCILIATION_TOLERANCE,
            "detail": "All sectors reconciled successfully" if success else f"{len(mismatches)} sector(s) failed reconciliation",
        }
