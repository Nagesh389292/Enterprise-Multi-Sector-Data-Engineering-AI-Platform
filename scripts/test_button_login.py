import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--window-size=1600,1000')

driver = webdriver.Chrome(options=chrome_options)
driver.get('http://localhost:8088/login/')
time.sleep(3)

print("Filling login fields and clicking button[type='submit']...")
driver.find_element(By.ID, "username").send_keys("admin")
driver.find_element(By.ID, "password").send_keys("admin")
btn = driver.find_element(By.XPATH, "//button[@type='submit']")
btn.click()

time.sleep(5)
print("AFTER BUTTON CLICK URL:", driver.current_url)
print("AFTER BUTTON CLICK TITLE:", driver.title)

driver.get('http://localhost:8088/superset/dashboard/1/')
time.sleep(8)
print("DASHBOARD 1 URL:", driver.current_url)
print("DASHBOARD 1 TITLE:", driver.title)

driver.save_screenshot("test_button_login_dash1.png")
size = len(open("test_button_login_dash1.png", "rb").read())
print("SAVED test_button_login_dash1.png! Size:", size, "bytes")
driver.quit()
