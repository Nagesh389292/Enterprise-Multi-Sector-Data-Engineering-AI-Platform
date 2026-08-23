"""
Databricks Jobs API Integration.

Triggers, monitors, and retrieves results for Databricks Jobs (Workflows).
Designed for triggering the PySpark Medallion pipeline as a cloud job.

Usage:
    jobs = DatabricksJobsClient()
    run_id = jobs.trigger_run(job_id="123456")
    result = jobs.wait_for_run(run_id, timeout=300)
    print(result)
"""

import time
import logging
from typing import Dict, Any, Optional

from data_engineering.databricks.client import DatabricksClient, DatabricksConfig

logger = logging.getLogger(__name__)

TERMINAL_RUN_STATES = {"SUCCESS", "FAILED", "CANCELED", "TIMEDOUT", "SKIPPED"}
DEFAULT_JOB_TIMEOUT_SECS = 600  # 10 minutes


class DatabricksJobsClient:
    """
    Databricks Jobs API client for triggering and monitoring Workflow runs.

    Supports:
    - trigger_run(job_id): Start a job run now
    - get_run_state(run_id): Get current run state
    - wait_for_run(run_id): Block until run completes or times out
    - get_run_output(run_id): Retrieve run output/result
    """

    def __init__(self, config: Optional[DatabricksConfig] = None):
        self.config = config or DatabricksConfig()
        self.client = DatabricksClient(self.config)

    def trigger_run(self, job_id: str) -> Dict[str, Any]:
        """
        Triggers a Databricks job run.

        Args:
            job_id: Databricks job ID (string or int)

        Returns:
            Dict with run_id and status
        """
        try:
            ws = self.client.workspace_client()
            run = ws.jobs.run_now(job_id=int(job_id))
            run_id = run.run_id
            logger.info("[DatabricksJobs] Triggered job %s → run_id=%s", job_id, run_id)
            return {
                "success": True,
                "job_id": str(job_id),
                "run_id": str(run_id),
                "detail": f"Job run triggered successfully (run_id={run_id})",
            }
        except Exception as e:
            safe_err = str(e)
            if self.config.token_present:
                safe_err = safe_err.replace(self.config.token, "<REDACTED>")
            return {
                "success": False,
                "job_id": str(job_id),
                "run_id": None,
                "detail": f"Failed to trigger job: {safe_err[:300]}",
            }

    def get_run_state(self, run_id: str) -> Dict[str, Any]:
        """
        Gets the current state of a job run.

        Returns:
            Dict with run_id, state, life_cycle_state, and result_state
        """
        try:
            ws = self.client.workspace_client()
            run = ws.jobs.get_run(run_id=int(run_id))
            state = run.state
            life_cycle = str(getattr(state, "life_cycle_state", "UNKNOWN")).upper()
            result_state = str(getattr(state, "result_state", "")).upper()
            state_message = getattr(state, "state_message", "")
            return {
                "success": True,
                "run_id": str(run_id),
                "life_cycle_state": life_cycle,
                "result_state": result_state or "IN_PROGRESS",
                "state_message": state_message,
                "terminal": life_cycle in ("TERMINATED", "SKIPPED", "INTERNAL_ERROR"),
            }
        except Exception as e:
            safe_err = str(e)
            if self.config.token_present:
                safe_err = safe_err.replace(self.config.token, "<REDACTED>")
            return {
                "success": False,
                "run_id": str(run_id),
                "life_cycle_state": "UNKNOWN",
                "result_state": "UNKNOWN",
                "state_message": safe_err[:300],
                "terminal": False,
            }

    def wait_for_run(
        self,
        run_id: str,
        timeout_secs: int = DEFAULT_JOB_TIMEOUT_SECS,
        poll_interval: float = 10.0,
    ) -> Dict[str, Any]:
        """
        Polls a job run until it reaches a terminal state or timeout.

        Returns:
            Dict with final run state, result, and elapsed time
        """
        start = time.time()
        logger.info("[DatabricksJobs] Waiting for run %s (timeout=%ds)...", run_id, timeout_secs)

        while True:
            elapsed = time.time() - start
            if elapsed > timeout_secs:
                return {
                    "success": False,
                    "run_id": str(run_id),
                    "result": "TIMEOUT",
                    "elapsed_secs": round(elapsed, 1),
                    "detail": f"Run timed out after {timeout_secs}s",
                }

            state = self.get_run_state(run_id)
            if state["terminal"]:
                result_state = state["result_state"]
                success = result_state == "SUCCESS"
                logger.info(
                    "[DatabricksJobs] Run %s finished: %s (%.1fs)",
                    run_id, result_state, elapsed,
                )
                return {
                    "success": success,
                    "run_id": str(run_id),
                    "result": result_state,
                    "life_cycle_state": state["life_cycle_state"],
                    "state_message": state.get("state_message", ""),
                    "elapsed_secs": round(elapsed, 1),
                    "detail": f"Run completed with state: {result_state}",
                }

            logger.debug("[DatabricksJobs] Run %s state=%s (%.1fs)", run_id, state["life_cycle_state"], elapsed)
            time.sleep(poll_interval)

    def list_jobs(self, limit: int = 20) -> Dict[str, Any]:
        """Lists available Databricks jobs in the workspace."""
        try:
            ws = self.client.workspace_client()
            jobs_list = list(ws.jobs.list(limit=limit))
            job_summaries = []
            for job in jobs_list:
                job_summaries.append({
                    "job_id": str(job.job_id),
                    "name": getattr(getattr(job, "settings", None), "name", "unnamed"),
                })
            return {"success": True, "jobs": job_summaries, "count": len(job_summaries)}
        except Exception as e:
            safe_err = str(e)
            if self.config.token_present:
                safe_err = safe_err.replace(self.config.token, "<REDACTED>")
            return {"success": False, "jobs": [], "count": 0, "detail": safe_err[:300]}


# Medallion pipeline job definition (create via Databricks UI or Terraform)
MEDALLION_JOB_DEFINITION = {
    "name": "Enterprise-Medallion-Pipeline",
    "description": (
        "PySpark Bronze → Silver → Gold Medallion pipeline "
        "for all 6 enterprise sectors."
    ),
    "timeout_seconds": 1800,
    "tasks": [
        {
            "task_key": "run_medallion_pipeline",
            "description": "Run multi-sector Medallion pipeline",
            "python_wheel_task": {
                "package_name": "enterprise_platform",
                "entry_point": "run_medallion",
            },
            "libraries": [{"pypi": {"package": "pyarrow"}}, {"pypi": {"package": "pandas"}}],
        }
    ],
    "job_clusters": [],  # Use existing SQL Warehouse compute — no new cluster
    "tags": {
        "project": "enterprise-data-platform",
        "pipeline": "medallion",
        "environment": "cloud",
    },
}


if __name__ == "__main__":
    jobs = DatabricksJobsClient()
    print("[DatabricksJobs] Listing available jobs...")
    result = jobs.list_jobs()
    print(f"  Found {result['count']} jobs")
    for j in result.get("jobs", []):
        print(f"  - job_id={j['job_id']}  name={j['name']}")
