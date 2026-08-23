import requests
import re

session = requests.Session()
login_url = "http://localhost:8088/login/"
resp = session.get(login_url)

csrf_match = re.search(r'name="csrf_token" type="hidden" value="([^"]+)"', resp.text)
csrf_token = csrf_match.group(1) if csrf_match else ""

session.post(login_url, data={
    "csrf_token": csrf_token,
    "username": "admin",
    "password": "admin"
})

resp_dash = session.get("http://localhost:8088/api/v1/dashboard/?q=(page_size:100)")
data = resp_dash.json()

print(f"=== ALL SUPERSET DASHBOARDS IN RUNNING INSTANCE ===")
for d in data.get("result", []):
    print(f"ID: {d.get('id')} | Title: {d.get('dashboard_title')} | URL: http://localhost:8088/superset/dashboard/{d.get('id')}/")
