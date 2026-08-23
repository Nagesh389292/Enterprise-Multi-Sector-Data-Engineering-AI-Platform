import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

proj_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
out_dir = os.path.join(proj_root, 'docs', 'media', 'final_demo')
os.makedirs(out_dir, exist_ok=True)

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1440,900")
chrome_options.add_argument("--no-sandbox")

driver = webdriver.Chrome(options=chrome_options)
print("=== CAPTURING LIVE FRESH APPLICATION SCREENSHOTS VIA SELENIUM ===")

try:
    # 1. React Command Center UI
    print("[1/5] Capturing React Command Center (http://localhost:3000)...")
    driver.get("http://localhost:3000")
    time.sleep(3)
    driver.save_screenshot(os.path.join(out_dir, "09_react_command_center.png"))
    print("  -> Saved 09_react_command_center.png")

    # 2. AI Copilot Query Interaction
    print("[2/5] Interacting with AI Copilot...")
    try:
        textarea = driver.find_element(By.TAG_NAME, "textarea")
        textarea.send_keys("Which sector currently shows the highest risk according to available analytics?")
        time.sleep(1)
        button = driver.find_element(By.XPATH, "//button[contains(text(), 'Ask') or contains(text(), 'Send') or contains(text(), 'Query')]")
        button.click()
        time.sleep(4)
    except Exception as e:
        print(f"  AI Copilot interaction warning: {e}")
    driver.save_screenshot(os.path.join(out_dir, "05_ai_copilot.png"))
    print("  -> Saved 05_ai_copilot.png")

    # 3. Superset Login & Dashboards
    print("[3/5] Logging into Apache Superset (http://localhost:8088)...")
    driver.get("http://localhost:8088/login/")
    time.sleep(2)
    try:
        username_input = driver.find_element(By.NAME, "username")
        password_input = driver.find_element(By.NAME, "password")
        username_input.send_keys("admin")
        password_input.send_keys("admin")
        submit_btn = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
        submit_btn.click()
        time.sleep(4)
    except Exception as e:
        print(f"  Superset login warning: {e}")

    # Executive Dashboard
    print("[4/5] Capturing Superset Executive Dashboard...")
    driver.get("http://localhost:8088/superset/dashboard/1/")
    time.sleep(5)
    driver.save_screenshot(os.path.join(out_dir, "06_superset_executive.png"))
    print("  -> Saved 06_superset_executive.png")

    # Fraud Dashboard
    print("[5/5] Capturing Superset Fraud Dashboard...")
    driver.get("http://localhost:8088/superset/dashboard/2/")
    time.sleep(5)
    driver.save_screenshot(os.path.join(out_dir, "07_superset_fraud.png"))
    print("  -> Saved 07_superset_fraud.png")

    # Retail Dashboard
    print("[6/6] Capturing Superset Retail Dashboard...")
    driver.get("http://localhost:8088/superset/dashboard/6/")
    time.sleep(5)
    driver.save_screenshot(os.path.join(out_dir, "08_superset_retail.png"))
    print("  -> Saved 08_superset_retail.png")

finally:
    driver.quit()

print("All live fresh screenshots captured cleanly!")
