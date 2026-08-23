import time
import requests
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

session = requests.Session()
login_url = 'http://localhost:8088/login/'
resp = session.get(login_url)

csrf_match = re.search(r'id="csrf_token"\s+value="([^"]+)"', resp.text)
csrf_token = csrf_match.group(1) if csrf_match else ''

post_resp = session.post(login_url, data={
    'csrf_token': csrf_token,
    'username': 'admin',
    'password': 'admin'
}, allow_redirects=False)

session_cookie = session.cookies.get('session')
print('AUTHENTICATED SESSION COOKIE:', session_cookie[:30] + '...')

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--window-size=1600,1000')

driver = webdriver.Chrome(options=chrome_options)
driver.get('http://localhost:8088/404')
driver.add_cookie({'name': 'session', 'value': session_cookie, 'domain': 'localhost', 'path': '/'})

driver.get('http://localhost:8088/superset/dashboard/1/')
time.sleep(8)
driver.save_screenshot('test_authenticated_dash_1.png')
size = len(open('test_authenticated_dash_1.png', 'rb').read())
print('SAVED test_authenticated_dash_1.png! Size:', size, 'bytes')
driver.quit()
