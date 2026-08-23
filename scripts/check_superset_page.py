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

# POST to login
post_resp = session.post(login_url, data={
    'csrf_token': csrf_token,
    'username': 'admin',
    'password': 'admin'
})

print('REPOST DASHBOARD 1 HTML LENGTH:', len(session.get('http://localhost:8088/superset/dashboard/1/').text))

cookies = session.cookies.get_dict()
print('COOKIES OBTAINED:', cookies)

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--window-size=1600,1000')

driver = webdriver.Chrome(options=chrome_options)
driver.get('http://localhost:8088/login/')

for name, val in cookies.items():
    driver.add_cookie({'name': name, 'value': val, 'path': '/'})

driver.get('http://localhost:8088/superset/dashboard/1/')
time.sleep(6)
print('AFTER COOKIES SET TITLE:', driver.title)
print('AFTER COOKIES SET URL:', driver.current_url)
print('BODY TEXT HEAD:', repr(driver.find_element('tag name', 'body').text[:300]))
driver.save_screenshot('test_dash_1_authenticated_ui.png')
print('SCREENSHOT SIZE:', len(open('test_dash_1_authenticated_ui.png', 'rb').read()))
driver.quit()
