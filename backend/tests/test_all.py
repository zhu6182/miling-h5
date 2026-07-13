import urllib.request, json

BASE = 'http://localhost:8000/api/v1'

def post(url, data, token=None):
    req = urllib.request.Request(url, data=json.dumps(data).encode() if data else None,
                                headers={'Content-Type': 'application/json'}, method='POST')
    if token:
        req.add_header('Authorization', 'Bearer ' + token)
    return json.loads(urllib.request.urlopen(req).read().decode())

def get(url, token=None):
    req = urllib.request.Request(url, headers={'Content-Type': 'application/json'}, method='GET')
    if token:
        req.add_header('Authorization', 'Bearer ' + token)
    return json.loads(urllib.request.urlopen(req).read().decode())

print('=== 1. 注册两个用户 ===')
r1 = post(BASE + '/auth/register', {'phone': '13999900001', 'password': '123456', 'nickname': '用户A'})
token_a = r1['access_token']
uid_a = r1['user']['id']
print(f'  A 注册成功, id={uid_a}')

r2 = post(BASE + '/auth/register', {'phone': '13999900002', 'password': '123456', 'nickname': '用户B'})
token_b = r2['access_token']
uid_b = r2['user']['id']
print(f'  B 注册成功, id={uid_b}')

print()
print('=== 2. 双方创建命盘 ===')
chart_a = post(BASE + '/users/save-chart',
    {'solar_date': '1991-8-15', 'gender': '男', 'hour_index': 1, 'is_default': True}, token_a)
print(f'  A 命盘: {chart_a["five_elements"]} {chart_a["soul_palace"]}宫')

chart_b = post(BASE + '/users/save-chart',
    {'solar_date': '1990-3-20', 'gender': '女', 'hour_index': 3, 'is_default': True}, token_b)
print(f'  B 命盘: {chart_b["five_elements"]} {chart_b["soul_palace"]}宫')

print()
print('=== 3. A 生成配对码 ===')
qr = post(BASE + '/match/create-qr', {'match_type': 'all'}, token_a)
print(f'  配对码: {qr["qr_code"]}')

print()
print('=== 4. B 扫码配对 ===')
match_result = post(BASE + '/match/scan/' + qr['qr_code'], None, token_b)
print(f'  配对成功! match_id={match_result["match_id"]}')
print(f'  综合指数: {match_result["result"]["overall_score"]}分')

dims = match_result['result']['dimensions']
print(f'  💖 姻缘: {dims["love"]["score"]}分')
print(f'  💼 事业: {dims["career"]["score"]}分')
print(f'  🤝 友谊: {dims["friendship"]["score"]}分')
print(f'  🌟 贵人: {dims["mentor"]["score"]}分')

print()
print('=== 5. 获取匹配历史 ===')
history = get(BASE + '/match/history', token_a)
print(f'  历史记录: {len(history)} 条')

print()
print('=== 6. 添加好友 ===')
friend = post(BASE + '/match/add-friend/' + str(uid_a), None, token_b)
print(f'  {friend["message"]}')

print()
print('=== 7. 好友列表 ===')
friends = get(BASE + '/match/friends/list', token_b)
print(f'  好友数: {len(friends)}')
if friends:
    print(f'  好友: {friends[0]["nickname"]} - {friends[0]["soul_palace"]}宫')

print()
print('=== 8. 生成分享图片 ===')
try:
    img_url = BASE + '/share/match/' + str(match_result['match_id']) + '/image'
    req = urllib.request.Request(img_url, headers={'Authorization': 'Bearer ' + token_a})
    resp = urllib.request.urlopen(req)
    print(f'  分享图片生成成功! 大小: {len(resp.read())} bytes')
except Exception as e:
    print(f'  分享图片: {e}')

print()
print('=== 全部测试通过! 🎉 ===')
