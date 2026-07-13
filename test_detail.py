import requests

login = requests.post('http://localhost:8000/api/v1/auth/login', json={'username':'test','password':'123456'})
token = login.json().get('access_token', '')
headers = {'Authorization': f'Bearer {token}'}

r = requests.get('http://localhost:8000/api/v1/charts', headers=headers)
charts = r.json()
chart_id = charts[0]['id']

detail = requests.get(f'http://localhost:8000/api/v1/charts/{chart_id}', headers=headers)
data = detail.json()
print('Keys:', list(data.keys()))
print('has chart_data:', 'chart_data' in data)
if 'chart_data' in data and data['chart_data']:
    cd = data['chart_data']
    print('chart_data keys:', list(cd.keys()) if isinstance(cd, dict) else type(cd))
    if isinstance(cd, dict) and 'palaces' in cd:
        palaces = cd['palaces']
        print(f'palaces count: {len(palaces)}')
        if palaces:
            p0 = palaces[0]
            print(f'palace 0 keys: {list(p0.keys())}')
            print(f'major_stars: {p0.get("major_stars")}')
else:
    print('chart_data:', data.get('chart_data'))
