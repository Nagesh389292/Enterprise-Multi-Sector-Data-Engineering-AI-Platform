"""
Verifies that all 9 Apache Superset charts execute clean SQL queries without data errors.
"""

import urllib.request
import json
import http.cookiejar

SUPERSET_URL = "http://localhost:8088"

def verify_charts():
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

    login_url = f"{SUPERSET_URL}/api/v1/security/login"
    login_data = json.dumps({"username": "admin", "password": "admin_password_change_me", "provider": "db"}).encode("utf-8")
    req = urllib.request.Request(login_url, data=login_data, headers={"Content-Type": "application/json"})
    
    with opener.open(req) as resp:
        token = json.loads(resp.read().decode("utf-8"))["access_token"]

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # Get charts
    req_charts = urllib.request.Request(f"{SUPERSET_URL}/api/v1/chart/", headers=headers)
    with opener.open(req_charts) as resp:
        charts = json.loads(resp.read().decode("utf-8")).get("result", [])

    print(f"[ChartDataVerifier] Testing query execution for {len(charts)} charts...")
    results = []

    for c in charts:
        cid = c["id"]
        cname = c["slice_name"]
        
        # Test query data endpoint
        data_payload = json.dumps({
            "datasource": {"id": c["datasource_id"], "type": "table"},
            "force": True,
            "queries": [{
                "metrics": json.loads(c["params"]).get("metrics", []),
                "groupby": json.loads(c["params"]).get("groupby", []),
                "row_limit": 100
            }]
        }).encode("utf-8")

        req_data = urllib.request.Request(f"{SUPERSET_URL}/api/v1/chart/data", data=data_payload, headers=headers)
        try:
            with opener.open(req_data) as resp:
                res = json.loads(resp.read().decode("utf-8"))
                query_res = res.get("result", [{}])[0]
                status = query_res.get("status")
                rowcount = query_res.get("rowcount", 0)
                error_msg = query_res.get("error")
                print(f"Chart ID {cid} ('{cname}'): status={status}, rows={rowcount}, err={error_msg}")
                results.append({"id": cid, "name": cname, "status": status, "rows": rowcount, "error": error_msg})
        except Exception as e:
            err = e.read().decode("utf-8") if hasattr(e, "read") else str(e)
            print(f"Chart ID {cid} ('{cname}'): HTTP ERROR -> {err}")
            results.append({"id": cid, "name": cname, "status": "ERROR", "rows": 0, "error": err})

    return results

if __name__ == "__main__":
    verify_charts()
