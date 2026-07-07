import sqlite3

db_path = "mingli.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("PRAGMA table_info(charts)")
    columns = [col[1] for col in cursor.fetchall()]
    print(f"现有字段: {columns}")

    if "remark" not in columns:
        cursor.execute("ALTER TABLE charts ADD COLUMN remark VARCHAR(100)")
        print("已添加 remark 字段")
    else:
        print("remark 字段已存在")

    if "chart_type" not in columns:
        cursor.execute("ALTER TABLE charts ADD COLUMN chart_type VARCHAR(20) DEFAULT 'ziwei'")
        print("已添加 chart_type 字段")
    else:
        print("chart_type 字段已存在")

    cursor.execute("PRAGMA table_info(charts)")
    columns = cursor.fetchall()
    print("\n迁移后字段列表:")
    for col in columns:
        print(f"  {col[1]} - {col[2]}")

    conn.commit()
    print("\n数据库迁移完成!")

except Exception as e:
    print(f"迁移失败: {e}")
    conn.rollback()
finally:
    conn.close()
