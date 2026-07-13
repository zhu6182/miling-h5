import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.services.chart_service import calculate_chart
from app.core.database import SessionLocal, Base, engine
from app.models.models import User, Chart
from app.core.security import hash_password

Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    result = calculate_chart("1991-8-15", 1, "男", False)
    print("排盘成功, 宫位数:", len(result['palaces']))

    user = User(
        phone="13900139000",
        password_hash=hash_password("123456"),
        nickname="测试2"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print("用户创建成功:", user.id)

    chart = Chart(
        user_id=user.id,
        name="测试命盘",
        solar_date=result.get('solar_date'),
        lunar_date=result.get('lunar_date'),
        gender=result['gender'],
        hour_index=result['hour_index'],
        hour_name=result.get('hour_name', ''),
        five_elements=result.get('five_elements', ''),
        soul_palace=result.get('soul_palace_branch', ''),
        body_palace=result.get('body_palace_branch', ''),
        chart_data=result,
        is_default=True,
    )
    db.add(chart)
    db.commit()
    db.refresh(chart)
    print("命盘保存成功:", chart.id, chart.five_elements, chart.soul_palace)

except Exception as e:
    import traceback
    traceback.print_exc()
finally:
    db.close()
