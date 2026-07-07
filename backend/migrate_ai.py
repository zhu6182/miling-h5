import sqlite3
conn = sqlite3.connect('mingli.db')
cursor = conn.cursor()
# 把用户3的火山方舟配置复制到固定开发用户
cursor.execute("UPDATE users SET ai_provider='openai', ai_api_key=(SELECT ai_api_key FROM users WHERE id=3), ai_model=(SELECT ai_model FROM users WHERE id=3), ai_base_url=(SELECT ai_base_url FROM users WHERE id=3) WHERE openid='wx_dev_user'")
conn.commit()
# 验证
cursor.execute("SELECT id, openid, nickname, ai_provider, ai_model, ai_base_url, CASE WHEN ai_api_key IS NULL OR ai_api_key='' THEN 0 ELSE 1 END as has_key FROM users WHERE openid='wx_dev_user'")
for row in cursor.fetchall():
    print(row)
conn.close()
