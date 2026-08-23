"""
India Open Government Data (OGD) Resource Discovery Engine.
Programmatically queries Data.gov.in API catalog to discover, audit, rank, and register active API-enabled resources.
"""

import os
import json
import urllib.request
import urllib.parse
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

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

REGISTRY_PATH = os.path.join(os.getcwd(), "data", "config", "ogd_resource_registry.json")

# Known & Verified Data.gov.in Healthcare & Hospital API Resource IDs
KNOWN_HEALTHCARE_RESOURCES = [
    {
        "resource_id": "3b01b880-e841-4194-a072-93e1db11853d",
        "name": "Government Hospital Directory India",
        "sector": "healthcare",
        "priority": 1,
        "api_endpoint": "https://api.data.gov.in/resource/3b01b880-e841-4194-a072-93e1db11853d"
    },
    {
        "resource_id": "6176573d-42ac-4be3-ad58-1b088b11367e",
        "name": "National Health Portal Hospital Directory",
        "sector": "healthcare",
        "priority": 2,
        "api_endpoint": "https://api.data.gov.in/resource/6176573d-42ac-4be3-ad58-1b088b11367e"
    },
    {
        "resource_id": "b05e6080-60b7-4a0b-a010-8b17b62900c4",
        "name": "Blood Bank Directory India",
        "sector": "healthcare",
        "priority": 3,
        "api_endpoint": "https://api.data.gov.in/resource/b05e6080-60b7-4a0b-a010-8b17b62900c4"
    }
]

class OGDResourceDiscoveryEngine:
    """Discovers, audits, and ranks Data.gov.in resources."""
    def __init__(self):
        self.api_key = os.getenv("DATA_GOV_API_KEY", "")

    def audit_resource(self, resource_info: Dict[str, Any]) -> Dict[str, Any]:
        """Tests live API endpoint for availability, record count, and schema quality."""
        resource_id = resource_info["resource_id"]
        audit_result = {
            "resource_id": resource_id,
            "name": resource_info["name"],
            "sector": resource_info["sector"],
            "priority": resource_info["priority"],
            "api_endpoint": resource_info["api_endpoint"],
            "api_available": False,
            "record_count": 0,
            "sample_fields": [],
            "http_status": None,
            "last_audited": datetime.now(timezone.utc).isoformat(),
            "quality_score": 0.0,
            "error": None
        }

        if not self.api_key:
            audit_result["error"] = "DATA_GOV_API_KEY is not configured in environment"
            return audit_result

        url = f"{resource_info['api_endpoint']}?api-key={self.api_key}&format=json&limit=5"
        
        # Retry loop for HTTP rate limit (429) and transient issues
        max_retries = 3
        for attempt in range(max_retries):
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "EnterpriseDataPlatform/1.0"})
                with urllib.request.urlopen(req, timeout=10) as resp:
                    audit_result["http_status"] = resp.status
                    if resp.status == 200:
                        data = json.loads(resp.read().decode("utf-8"))
                        records = data.get("records", [])
                        total = data.get("total", len(records))
                        
                        audit_result["record_count"] = total
                        if records:
                            audit_result["api_available"] = True
                            audit_result["sample_fields"] = list(records[0].keys())
                            audit_result["quality_score"] = min(100.0, round((len(audit_result["sample_fields"]) / 5) * 100, 1))
                        else:
                            audit_result["api_available"] = False
                            audit_result["error"] = "API returned HTTP 200 OK but 0 records (empty array)"
                        break
            except urllib.error.HTTPError as e:
                audit_result["http_status"] = e.code
                if e.code == 429 and attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                audit_result["error"] = f"HTTP Error {e.code}: {e.reason}"
                break
            except Exception as e:
                audit_result["error"] = f"Connection/Parsing Failure: {str(e)}"
                break

        return audit_result

    def discover_and_build_registry(self) -> List[Dict[str, Any]]:
        """Audits all known healthcare resources and builds data/config/ogd_resource_registry.json."""
        os.makedirs(os.path.dirname(REGISTRY_PATH), exist_ok=True)
        results = []
        for r_info in KNOWN_HEALTHCARE_RESOURCES:
            audit = self.audit_resource(r_info)
            results.append(audit)

        # Sort by quality score and record count
        results.sort(key=lambda x: (x["api_available"], x["quality_score"], x["record_count"]), reverse=True)

        registry_payload = {
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "total_resources_audited": len(results),
            "verified_active_resources": [r for r in results if r["api_available"]],
            "resources": results
        }

        with open(REGISTRY_PATH, "w") as f:
            json.dump(registry_payload, f, indent=2)

        return results

if __name__ == "__main__":
    engine = OGDResourceDiscoveryEngine()
    print("Executing Data.gov.in Resource Discovery & Audit:")
    audited = engine.discover_and_build_registry()
    print(json.dumps(audited, indent=2))
