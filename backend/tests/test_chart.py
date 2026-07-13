import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.services.chart_service import calculate_chart

try:
    result = calculate_chart(
        date_str="1991-8-15",
        hour_index=1,
        gender="男",
        is_lunar=False
    )
    print("排盘成功!")
    print("五行局:", result['five_elements'])
    print("命宫:", result['soul_palace_branch'])
    print("身宫:", result['body_palace_branch'])
    print("宫位数:", len(result['palaces']))
    print("第一宫:", result['palaces'][0]['name'], result['palaces'][0]['major_stars'])
except Exception as e:
    import traceback
    traceback.print_exc()
