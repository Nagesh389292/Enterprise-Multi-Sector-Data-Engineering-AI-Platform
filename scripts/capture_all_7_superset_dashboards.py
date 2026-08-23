import os
import time
import requests
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

proj_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
superset_media_dir = os.path.join(proj_root, 'docs', 'media', 'final_demo', 'superset')
os.makedirs(superset_media_dir, exist_ok=True)

# 1. Log in via requests session to obtain session cookie
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

session_cookie = session.cookies.get("session")
print(f"Acquired Superset Session Cookie: {session_cookie[:25]}...")

# 2. Launch Selenium Headless Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1440,900")
chrome_options.add_argument("--no-sandbox")

driver = webdriver.Chrome(options=chrome_options)
driver.get("http://localhost:8088/")

driver.add_cookie({
    "name": "session",
    "value": session_cookie,
    "domain": "localhost",
    "path": "/"
})

dashboard_map = [
    ("01_superset_executive.png", 1, "Executive Command Center"),
    ("02_superset_fraud.png", 2, "Credit Card Fraud Intelligence"),
    ("03_superset_banking.png", 3, "Banking Credit Risk Analytics"),
    ("04_superset_healthcare.png", 4, "Healthcare Capacity & Utilization"),
    ("05_superset_readmission.png", 5, "Clinical EHR Readmission Risk"),
    ("06_superset_insurance.png", 6, "Insurance Claims Fraud Analytics"),
    ("07_superset_retail.png", 7, "Retail Sales & Product Demand")
]

print("=== CAPTURING ALL 7 FRESH SUPERSET DASHBOARD SCREENSHOTS ===")

for filename, dash_id, title in dashboard_map:
    url = f"http://localhost:8088/superset/dashboard/{dash_id}/"
    print(f"[{dash_id}/7] Capturing '{title}' from {url}...")
    driver.get(url)
    time.sleep(5) # Allow charts and KPI metrics to render completely
    out_path = os.path.join(superset_media_dir, filename)
    driver.save_screenshot(out_path)
    size_bytes = os.path.getsize(out_path)
    print(f"  -> Saved {filename} ({size_bytes} bytes)")

driver.quit()
print("All 7 fresh Superset dashboard screenshots captured cleanly!")
