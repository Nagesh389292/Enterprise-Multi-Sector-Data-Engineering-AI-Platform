"""
Data.gov.in API Verification Engine.
Systematically tests, audits, and verifies API resources against Data.gov.in gateway parameters.
Generates data/config/ogd_api_verification_report.json without fabricating mock data.
"""

import os
import json
import urllib.request
import urllib.parse
import time
from datetime import datetime, timezone
from typing import Dict, Any, List

def load_env_file():
    env_path = os.path.join(os.getcwd(), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ[key.strip()] = val.strip()

load_env_file()

REPORT_PATH = os.path.join(os.getcwd(), "data", "config", "ogd_api_verification_report.json")
REGISTRY_PATH = os.path.join(os.getcwd(), "data", "config", "ogd_resource_registry.json")

CANDIDATE_RESOURCES = [
    {
        "resource_id": "3b01b880-e841-4194-a072-93e1db11853d",
        "resource_name": "Government Hospital Directory India",
        "catalog_url": "https://data.gov.in/resource/government-hospital-directory-india",
        "api_url": "https://api.data.gov.in/resource/3b01b880-e841-4194-a072-93e1db11853d",
        "required_parameters": ["api-key", "format"],
        "test_parameters": {"format": "json", "limit": "5"}
    },
    {
        "resource_id": "6176573d-42ac-4be3-ad58-1b088b11367e",
        "resource_name": "National Health Portal Hospital Directory",
        "catalog_url": "https://data.gov.in/resource/national-health-portal-hospital-directory",
        "api_url": "https://api.data.gov.in/resource/6176573d-42ac-4be3-ad58-1b088b11367e",
        "required_parameters": ["api-key", "format"],
        "test_parameters": {"format": "json", "limit": "5"}
    },
    {
        "resource_id": "b05e6080-60b7-4a0b-a010-8b17b62900c4",
        "resource_name": "Blood Bank Directory India",
        "catalog_url": "https://data.gov.in/resource/blood-bank-directory-india",
        "api_url": "https://api.data.gov.in/resource/b05e6080-60b7-4a0b-a010-8b17b62900c4",
        "required_parameters": ["api-key", "format"],
        "test_parameters": {"format": "json", "limit": "5"}
    },
    {
        "resource_id": "579b464db66ec23bdd000001b1ae9ffca9af4cd66c1ea806dd234c8f",
        "resource_name": "Item-wise HMIS Report Andhra Pradesh 2017-18",
        "catalog_url": "https://data.gov.in/resource/item-wise-hmis-report-andhra-pradesh-2017-18",
        "api_url": "https://api.data.gov.in/resource/579b464db66ec23bdd000001b1ae9ffca9af4cd66c1ea806dd234c8f",
        "required_parameters": ["api-key", "format"],
        "test_parameters": {"format": "json", "limit": "5"}
    }
]

class OGDAPIVerifier:
    """Audits Data.gov.in resources and generates ogd_api_verification_report.json."""
    def __init__(self):
        self.api_key = os.getenv("DATA_GOV_API_KEY", "")

    def verify_resource(self, candidate: Dict[str, Any]) -> Dict[str, Any]:
        resource_id = candidate["resource_id"]
        report = {
            "resource_id": resource_id,
            "resource_name": candidate["resource_name"],
            "catalog_url": candidate["catalog_url"],
            "api_url": candidate["api_url"],
            "required_parameters": candidate["required_parameters"],
            "test_parameters": candidate["test_parameters"],
            "http_status": None,
            "total_records": 0,
            "records_received": 0,
            "fields": [],
            "api_verified": False,
            "failure_reason": None
        }

        if not self.api_key:
            report["failure_reason"] = "DATA_GOV_API_KEY is not configured in .env"
            return report

        url = f"{candidate['api_url']}?api-key={self.api_key}&format=json&limit=5"
        
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                report["http_status"] = resp.status
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    records = data.get("records", [])
                    total = data.get("total", 0)
                    msg = data.get("message", "")
                    
                    report["total_records"] = total
                    report["records_received"] = len(records)
                    
                    if records and len(records) > 0:
                        report["api_verified"] = True
                        report["fields"] = list(records[0].keys())
                    else:
                        report["api_verified"] = False
                        report["failure_reason"] = f"API returned HTTP 200 OK but 0 records ({msg or 'Empty array'})"
        except urllib.error.HTTPError as e:
            report["http_status"] = e.code
            report["failure_reason"] = f"HTTP Error {e.code}: {e.reason}"
        except Exception as e:
            report["failure_reason"] = f"Connection error: {str(e)}"

        return report

    def generate_verification_report(self) -> Dict[str, Any]:
        os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
        verified_list = []
        unverified_list = []
        download_only_list = []
        all_reports = []

        for candidate in CANDIDATE_RESOURCES:
            r_report = self.verify_resource(candidate)
            all_reports.append(r_report)
            
            if r_report["api_verified"]:
                verified_list.append(r_report)
            else:
                unverified_list.append(r_report)
                # Resources returning 'Meta not found' or HTTP 200 with 0 records require download-only CSV/XLS ingestion
                download_only_list.append(r_report)

        full_payload = {
            "report_generated_at": datetime.now(timezone.utc).isoformat(),
            "total_candidates_audited": len(all_reports),
            "verified_active_apis": len(verified_list),
            "unverified_apis": len(unverified_list),
            "download_only_resources": len(download_only_list),
            "verification_results": all_reports
        }

        with open(REPORT_PATH, "w") as f:
            json.dump(full_payload, f, indent=2)

        # Update OGD Resource Registry file as well
        with open(REGISTRY_PATH, "w") as f:
            json.dump({
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "verified_active_resources": verified_list,
                "resources": all_reports
            }, f, indent=2)

        return full_payload

if __name__ == "__main__":
    verifier = OGDAPIVerifier()
    report = verifier.generate_verification_report()
    
    print("\n========================================================")
    print("DATA.GOV.IN HEALTHCARE API VERIFICATION REPORT")
    print("========================================================\n")
    
    print("VERIFIED API RESOURCES:")
    verified = [r for r in report["verification_results"] if r["api_verified"]]
    if verified:
        for r in verified:
            print(f"  [VERIFIED] {r['resource_id']} - {r['resource_name']} (Records: {r['records_received']})")
    else:
        print("  None (0 active REST endpoints returning non-empty records without catalog filter parameters)")

    print("\nUNVERIFIED RESOURCES:")
    unverified = [r for r in report["verification_results"] if not r["api_verified"]]
    for r in unverified:
        print(f"  [UNVERIFIED] {r['resource_id']} - {r['resource_name']} Reason: {r['failure_reason']}")

    print("\nRESOURCES REQUIRING DOWNLOAD-ONLY INGESTION:")
    for r in unverified:
        print(f"  [DOWNLOAD-ONLY NEEDED] {r['resource_name']} ({r['catalog_url']})")

    print("\nReport saved to:", REPORT_PATH)
