import requests
import re

session = requests.Session()
login_url = 'http://localhost:8088/login/'
resp = session.get(login_url)

csrf_match = re.search(r'id="csrf_token"\s+value="([^"]+)"', resp.text)
csrf_token = csrf_match.group(1) if csrf_match else ''
if not csrf_token:
    csrf_match = re.search(r'value="([^"]+)"', resp.text)
    csrf_token = csrf_match.group(1) if csrf_match else ''

print('EXACT CSRF TOKEN:', csrf_token)

post_resp = session.post(login_url, data={
    'csrf_token': csrf_token,
    'username': 'admin',
    'password': 'admin'
}, allow_redirects=False)

print('POST STATUS:', post_resp.status_code)
print('POST LOCATION:', post_resp.headers.get('Location'))
print('COOKIES:', session.cookies.get_dict())
