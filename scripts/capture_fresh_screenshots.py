import os
import sys
import time
from playwright.sync_api import sync_playwright

proj_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
out_dir = os.path.join(proj_root, 'docs', 'media', 'final_demo')
os.makedirs(out_dir, exist_ok=True)

print("=== CAPTURING FRESH PRODUCT DEMO SCREENSHOTS ===")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})

    # 1. React Command Center Web UI
    try:
        print("[Capture 1/11] React Command Center Web UI...")
        page.goto("http://localhost:3000", wait_until="networkidle", timeout=15000)
        time.sleep(2)
        page.screenshot(path=os.path.join(out_dir, "09_react_command_center.png"))
        print("  -> Saved 09_react_command_center.png")

        # 2. AI Copilot Interaction
        print("[Capture 2/11] AI Copilot Question Interaction...")
        # Type realistic business question
        textarea = page.query_selector("textarea, input[type='text']")
        if textarea:
            textarea.fill("Which sector currently shows the highest risk according to available analytics?")
            time.sleep(1)
            page.keyboard.press("Enter")
            time.sleep(3)
        page.screenshot(path=os.path.join(out_dir, "05_ai_copilot.png"))
        print("  -> Saved 05_ai_copilot.png")
    except Exception as e:
        print(f"React UI capture error: {e}")

    # 3. Superset Login & Dashboards
    try:
        print("[Capture 3/11] Superset Login & Dashboards...")
        page.goto("http://localhost:8088/login/", wait_until="networkidle", timeout=15000)
        time.sleep(1)
        if "login" in page.url:
            page.fill("input[name='username']", "admin")
            page.fill("input[name='password']", "admin")
            page.click("input[type='submit']")
            time.sleep(3)

        # Executive Dashboard
        page.goto("http://localhost:8088/superset/dashboard/1/", wait_until="networkidle", timeout=20000)
        time.sleep(4)
        page.screenshot(path=os.path.join(out_dir, "06_superset_executive.png"))
        print("  -> Saved 06_superset_executive.png")

        # Fraud Dashboard
        page.goto("http://localhost:8088/superset/dashboard/2/", wait_until="networkidle", timeout=20000)
        time.sleep(4)
        page.screenshot(path=os.path.join(out_dir, "07_superset_fraud.png"))
        print("  -> Saved 07_superset_fraud.png")

        # Retail Dashboard
        page.goto("http://localhost:8088/superset/dashboard/6/", wait_until="networkidle", timeout=20000)
        time.sleep(4)
        page.screenshot(path=os.path.join(out_dir, "08_superset_retail.png"))
        print("  -> Saved 08_superset_retail.png")

    except Exception as e:
        print(f"Superset capture error: {e}")

    browser.close()

print("Fresh UI captures complete!")
