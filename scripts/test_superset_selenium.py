import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1600,1000")
chrome_options.add_argument("--no-sandbox")

driver = webdriver.Chrome(options=chrome_options)

try:
    print("Opening Superset Login Page (http://localhost:8088/login/)...")
    driver.get("http://localhost:8088/login/")
    time.sleep(2)
    
    print("Filling Login Form...")
    user_elem = driver.find_element(By.NAME, "username")
    user_elem.clear()
    user_elem.send_keys("admin")
    
    pass_elem = driver.find_element(By.NAME, "password")
    pass_elem.clear()
    pass_elem.send_keys("admin")
    
    submit_elem = driver.find_element(By.XPATH, "//input[@type='submit']")
    submit_elem.click()
    
    time.sleep(3)
    print("Logged in! Current URL:", driver.current_url)
    
    # Try navigating to Dashboard 1
    driver.get("http://localhost:8088/superset/dashboard/1/")
    time.sleep(6) # Wait for charts to render
    driver.save_screenshot("test_dash_1.png")
    print("Saved test_dash_1.png! Size:", len(open("test_dash_1.png", "rb").read()))
finally:
    driver.quit()
