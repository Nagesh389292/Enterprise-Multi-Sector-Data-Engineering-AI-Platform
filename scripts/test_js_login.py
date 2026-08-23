import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--window-size=1600,1000')

driver = webdriver.Chrome(options=chrome_options)
driver.get('http://localhost:8088/login/')
time.sleep(3)

print("Submitting login form via Javascript...")
driver.execute_script("""
    document.getElementById('username').value = 'admin';
    document.getElementById('password').value = 'admin';
    document.forms[0].submit();
""")

time.sleep(5)
print("AFTER JS LOGIN URL:", driver.current_url)
print("AFTER JS LOGIN TITLE:", driver.title)

driver.get('http://localhost:8088/superset/dashboard/1/')
time.sleep(8)
print("DASHBOARD 1 URL:", driver.current_url)
print("DASHBOARD 1 TITLE:", driver.title)

driver.save_screenshot("test_js_login_dash1.png")
size = len(open("test_js_login_dash1.png", "rb").read())
print("SAVED test_js_login_dash1.png! Size:", size, "bytes")
driver.quit()
