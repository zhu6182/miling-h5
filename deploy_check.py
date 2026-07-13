import requests
import time

API_KEY = 'rnd_zKofIzqhuPcWM3AGfraqsjdASpnD'
headers = {'Authorization': f'Bearer {API_KEY}', 'Accept': 'application/json'}

print('=== 检查服务状态 ===')
r = requests.get('https://api.render.com/v1/services/srv-d96jgdnavr4c739k5rjg', headers=headers)
service = r.json()
print(f'service status: {service.get("status")}')
print(f'last deploy: {service.get("lastDeployedAt")}')

print('\n=== 检查最近部署 ===')
r2 = requests.get('https://api.render.com/v1/services/srv-d96jgdnavr4c739k5rjg/deploys', headers=headers)
deploys = r2.json()
if deploys:
    for d in deploys[:3]:
        deploy_id = d.get('id')
        status = d.get('status')
        commit = d.get('commit', {}).get('id', '')[:7]
        print(f'deploy id: {deploy_id}, status: {status}, commit: {commit}')

print('\n=== 等待部署完成 ===')
for i in range(15):
    time.sleep(30)
    r3 = requests.get('https://api.render.com/v1/services/srv-d96jgdnavr4c739k5rjg', headers=headers)
    service = r3.json()
    status = service.get('status')
    print(f'第{i+1}次检查: {status}')
    if status == 'live':
        print('\n部署成功!')
        break
else:
    print('\n部署超时')

print('\n=== 测试 save-chart ===')
base = 'https://miling-backend.onrender.com/api/v1'
r4 = requests.post(f'{base}/auth/register', json={'username': 'testuser_new', 'password': 'test123'})
if r4.status_code == 200:
    token = r4.json().get('access_token')
    headers2 = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    data = {
        'solar_date': '2000-01-01',
        'lunar_date': '',
        'hour_index': 6,
        'gender': 'male',
        'is_default': True,
        'name': '测试命盘',
        'remark': '',
        'chart_type': 'ziwei',
        'is_leap': False
    }
    r5 = requests.post(f'{base}/users/save-chart', json=data, headers=headers2)
    print(f'save-chart status: {r5.status_code}')
    if r5.status_code == 200:
        print('save-chart 成功!')
    else:
        print(f'error: {r5.text}')
else:
    print(f'register error: {r4.text}')
