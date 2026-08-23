import os
import time
import requests
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

proj_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
out_dir = os.path.join(proj_root, 'docs', 'media', 'final_demo')
os.makedirs(out_dir, exist_ok=True)

# 1. Log in via requests to fetch session cookie
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
print(f"Acquired Superset Session Cookie: {session_cookie[:20]}...")

# 2. Launch Selenium Chrome Headless
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1440,900")

driver = webdriver.Chrome(options=chrome_options)
driver.get("http://localhost:8088/")

# Add session cookie
driver.add_cookie({
    "name": "session",
    "value": session_cookie,
    "domain": "localhost",
    "path": "/"
})

print("=== CAPTURING FRESH LIVE SUPERSET DASHBOARDS ===")

# Executive Dashboard
print("[1/3] Executive Command Center (Dashboard #1)...")
driver.get("http://localhost:8088/superset/dashboard/1/")
time.sleep(5)
driver.save_screenshot(os.path.join(out_dir, "06_superset_executive.png"))

# Fraud Dashboard
print("[2/3] Credit Card Fraud Intelligence (Dashboard #2)...")
driver.get("http://localhost:8088/superset/dashboard/2/")
time.sleep(5)
driver.save_screenshot(os.path.join(out_dir, "07_superset_fraud.png"))

# Retail Dashboard
print("[3/3] Retail Demand & Revenue (Dashboard #6)...")
driver.get("http://localhost:8088/superset/dashboard/6/")
time.sleep(5)
driver.save_screenshot(os.path.join(out_dir, "08_superset_retail.png"))

driver.quit()
print("All Superset screenshots captured cleanly!")
