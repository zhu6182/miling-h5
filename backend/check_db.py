import sqlite3
conn = sqlite3.connect('mingli.db')
cursor = conn.cursor()
cursor.execute("SELECT id, openid, nickname, ai_provider, ai_model, ai_base_url, CASE WHEN ai_api_key IS NULL OR ai_api_key='' THEN 0 ELSE 1 END as has_key FROM users")
for row in cursor.fetchall():
    print(row)
conn.close()
