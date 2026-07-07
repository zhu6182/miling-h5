import json
import random
from datetime import date, datetime
from typing import Dict, List, Optional, Any
from app.models.models import Chart


# 天干
TIANGAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']

# 地支
DIZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# 五行
WUXING = ['金', '木', '水', '火', '土']

# 天干五行
TIANGAN_WUXING = {
    '甲': '木', '乙': '木', '丙': '火', '丁': '火', '戊': '土',
    '己': '土', '庚': '金', '辛': '金', '壬': '水', '癸': '水'
}

# 地支五行
DIZHI_WUXING = {
    '子': '水', '丑': '土', '寅': '木', '卯': '木', '辰': '土',
    '巳': '火', '午': '火', '未': '土', '申': '金', '酉': '金', '戌': '土', '亥': '水'
}

# 五行相生相克关系
WUXING_SHENG = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
WUXING_KE = {'木': '土', '土': '水', '水': '火', '火': '金', '金': '木'}
WUXING_BEI_SHENG = {'火': '木', '土': '火', '金': '土', '水': '金', '木': '水'}
WUXING_BEI_KE = {'土': '木', '水': '土', '火': '水', '金': '火', '木': '金'}

# 五行局对应
WUXING_JU = {
    '水二局': '水', '木三局': '木', '金四局': '金', '土五局': '土', '火六局': '火'
}

# 幸运颜色映射
LUCKY_COLORS = {
    '金': ['白色', '银色', '金色'],
    '木': ['绿色', '青色', '翠色'],
    '水': ['蓝色', '黑色', '灰色'],
    '火': ['红色', '橙色', '粉色'],
    '土': ['黄色', '棕色', '咖啡色']
}

YI_ITEMS = ['外出游玩', '约会社交', '学习提升', '健身运动', '阅读思考', '整理规划', '聚会聚餐', '投资理财', '求职面试', '表达沟通', '放松冥想', '尝试新事物']
JI_ITEMS = ['冲动消费', '熬夜追剧', '过度社交', '与人争执', '盲目投资', '消极怠工', '暴饮暴食', '拖延偷懒', '情绪失控', '过度焦虑', '忽视健康', '轻言放弃']


def get_day_ganzhi(target_date: date) -> tuple:
    """获取指定日期的干支（年月日）"""
    # 使用八字计算库中的方法获取当日干支
    # 这里使用简化算法：基于基准日期计算
    
    # 基准日期 1900年1月1日 为 甲子日
    base_date = date(1900, 1, 1)
    
    days_diff = (target_date - base_date).days
    
    # 日干支（60日一个周期）
    day_ganzhi_index = days_diff % 60
    day_gan = TIANGAN[day_ganzhi_index % 10]
    day_zhi = DIZHI[day_ganzhi_index % 12]
    
    # 年干支
    year = target_date.year
    year_gan_index = (year - 1900) % 10
    year_zhi_index = (year - 1900) % 12
    year_gan = TIANGAN[year_gan_index]
    year_zhi = DIZHI[year_zhi_index]
    
    # 月干支（简化计算）
    month = target_date.month
    # 月支固定对应
    month_zhi_map = {1: '寅', 2: '卯', 3: '辰', 4: '巳', 5: '午', 6: '未',
                      7: '申', 8: '酉', 9: '戌', 10: '亥', 11: '子', 12: '丑'}
    month_zhi = month_zhi_map[month]
    
    # 月干根据年干推算（五虎遁）
    year_gan_wuxing = TIANGAN_WUXING[year_gan]
    if year_gan in ['甲', '己']:
        month_gan_base = '丙'
    elif year_gan in ['乙', '庚']:
        month_gan_base = '戊'
    elif year_gan in ['丙', '辛']:
        month_gan_base = '庚'
    elif year_gan in ['丁', '壬']:
        month_gan_base = '壬'
    else:
        month_gan_base = '甲'
    
    month_gan_index = TIANGAN.index(month_gan_base) + (month - 1)
    month_gan = TIANGAN[month_gan_index % 10]
    
    return (year_gan + year_zhi), (month_gan + month_zhi), (day_gan + day_zhi)


def get_day_wuxing(day_ganzhi: str) -> Dict:
    """获取日干支的五行分布"""
    day_gan = day_ganzhi[0]
    day_zhi = day_ganzhi[1]
    
    return {
        'gan': day_gan,
        'zhi': day_zhi,
        'gan_wuxing': TIANGAN_WUXING[day_gan],
        'zhi_wuxing': DIZHI_WUXING[day_zhi]
    }


def calculate_wuxing_score(day_wuxing: Dict, chart_wuxing: str) -> int:
    """计算五行相生相克得分"""
    # 获取命盘五行局对应的五行
    chart_element = WUXING_JU.get(chart_wuxing, '土')
    
    day_gan_element = day_wuxing['gan_wuxing']
    day_zhi_element = day_wuxing['zhi_wuxing']
    
    score = 50  # 基础分
    
    # 日干与命盘五行关系
    if WUXING_SHENG.get(day_gan_element) == chart_element:
        score += 10  # 日干生命盘五行
    elif WUXING_KE.get(day_gan_element) == chart_element:
        score -= 5  # 日干克命盘五行
    elif WUXING_BEI_SHENG.get(day_gan_element) == chart_element:
        score += 5  # 命盘五行生日干
    elif WUXING_BEI_KE.get(day_gan_element) == chart_element:
        score -= 10  # 命盘五行克日干
    
    # 日支与命盘五行关系
    if WUXING_SHENG.get(day_zhi_element) == chart_element:
        score += 8
    elif WUXING_KE.get(day_zhi_element) == chart_element:
        score -= 4
    elif WUXING_BEI_SHENG.get(day_zhi_element) == chart_element:
        score += 4
    elif WUXING_BEI_KE.get(day_zhi_element) == chart_element:
        score -= 8
    
    return score


def get_lucky_factor(target_date: date, soul_palace: str) -> int:
    """计算流日运势因子"""
    # 基于命宫地支和当日地支的关系
    _, _, day_ganzhi = get_day_ganzhi(target_date)
    day_zhi = day_ganzhi[1]
    
    if not soul_palace:
        return 0
    
    soul_zhi = soul_palace[-1] if len(soul_palace) > 1 else soul_palace
    
    # 地支相合（六合）
    liuhe = {'子': '丑', '丑': '子', '寅': '亥', '亥': '寅', '卯': '戌', '戌': '卯',
             '辰': '酉', '酉': '辰', '巳': '申', '申': '巳', '午': '未', '未': '午'}
    if liuhe.get(soul_zhi) == day_zhi:
        return 15
    
    # 地支相冲（六冲）
    liuchong = {'子': '午', '午': '子', '丑': '未', '未': '丑', '寅': '申', '申': '寅',
                '卯': '酉', '酉': '卯', '辰': '戌', '戌': '辰', '巳': '亥', '亥': '巳'}
    if liuchong.get(soul_zhi) == day_zhi:
        return -15
    
    return 0


def calculate_love_fortune(chart: Chart, target_date: date) -> int:
    """计算爱情运势"""
    base_score = 50
    day_ganzhi = get_day_ganzhi(target_date)[2]
    day_wuxing = get_day_wuxing(day_ganzhi)
    
    # 简化计算：基于日支五行
    day_element = day_wuxing['zhi_wuxing']
    
    # 水日利于感情（桃花）
    if day_element == '水':
        base_score += 15
    elif day_element == '火':
        base_score += 10  # 热情
    
    # 添加随机波动
    base_score += random.randint(-5, 10)
    
    return max(20, min(95, base_score))


def calculate_career_fortune(chart: Chart, target_date: date) -> int:
    """计算事业运势"""
    base_score = 50
    day_ganzhi = get_day_ganzhi(target_date)[2]
    day_wuxing = get_day_wuxing(day_ganzhi)
    
    day_element = day_wuxing['zhi_wuxing']
    
    # 土日利于稳定事业
    if day_element == '土':
        base_score += 15
    elif day_element == '金':
        base_score += 10  # 执行力
    
    base_score += random.randint(-5, 10)
    
    return max(20, min(95, base_score))


def calculate_wealth_fortune(chart: Chart, target_date: date) -> int:
    """计算财运"""
    base_score = 50
    day_ganzhi = get_day_ganzhi(target_date)[2]
    day_wuxing = get_day_wuxing(day_ganzhi)
    
    day_element = day_wuxing['zhi_wuxing']
    
    # 金日利于求财
    if day_element == '金':
        base_score += 15
    elif day_element == '木':
        base_score += 10  # 生长
    
    base_score += random.randint(-5, 10)
    
    return max(20, min(95, base_score))


def generate_do_list(score: int, day_wuxing: Dict) -> List[str]:
    """生成今日宜事项"""
    count = max(3, min(5, score // 20))
    items = random.sample(YI_ITEMS, count)
    return items


def generate_avoid_list(score: int, day_wuxing: Dict) -> List[str]:
    """生成今日忌事项"""
    count = max(2, min(4, (100 - score) // 25))
    items = random.sample(JI_ITEMS, count)
    return items


def get_lucky_color(day_wuxing: Dict) -> str:
    """获取幸运颜色"""
    element = day_wuxing['zhi_wuxing']
    colors = LUCKY_COLORS.get(element, LUCKY_COLORS['土'])
    return random.choice(colors)


def get_lucky_number(target_date: date) -> str:
    """获取幸运数字"""
    day_sum = sum(int(d) for d in str(target_date.day))
    lucky_nums = [str((day_sum + i) % 10) for i in range(3)]
    return ', '.join(lucky_nums)


def get_lucky_direction(day_wuxing: Dict) -> str:
    """获取幸运方位"""
    direction_map = {
        '金': '西方',
        '木': '东方',
        '水': '北方',
        '火': '南方',
        '土': '中央'
    }
    element = day_wuxing['zhi_wuxing']
    return direction_map.get(element, '中央')


def generate_fortune_phrase(score: int) -> str:
    """生成运势短语"""
    phrases_high = [
        '🌟 今日星辰照耀，好运加持，把握机会，心想事成',
        '✨ 星运亨通，贵人相助，宜积极进取，必有美好收获',
        '🌙 运势如虹，诸事顺遂，相信直觉，大胆前行',
        '💫 吉星高照，心情愉悦，适合开启新计划',
        '🌠 星光璀璨，能量充沛，今日宜创造惊喜'
    ]
    phrases_mid = [
        '🌤️ 今日星运平稳，保持平常心，稳步前行',
        '☁️ 运势中等，宜冷静思考，谨慎决策',
        '🌥️ 平稳中略有起伏，保持耐心，静待时机',
        '🌦️ 按部就班，稳扎稳打，自然会有好结果',
        '🌗 星象平和，适合整理规划，蓄势待发'
    ]
    phrases_low = [
        '🌧️ 今日星运较弱，宜低调行事，调整状态',
        '🌫️ 运势欠佳，宜静不宜动，给自己充电',
        '🌙 谨慎为主，多思少行，做好基础工作',
        '🌑 保持低调，修身养性，静待好运降临',
        '🌚 适合反思总结，调整心态，明天会更好'
    ]
    
    if score >= 75:
        return random.choice(phrases_high)
    elif score >= 50:
        return random.choice(phrases_mid)
    else:
        return random.choice(phrases_low)


def calculate_daily_fortune(chart: Chart, target_date: date) -> Dict:
    """计算每日运势（完整版）"""
    
    # 1. 当日干支
    year_ganzhi, month_ganzhi, day_ganzhi = get_day_ganzhi(target_date)
    day_wuxing = get_day_wuxing(day_ganzhi)
    
    # 2. 五行得分
    chart_element = chart.five_elements or '土五局'
    wuxing_score = calculate_wuxing_score(day_wuxing, chart_element)
    
    # 3. 流日运势因子
    lucky_factor = get_lucky_factor(target_date, chart.soul_palace)
    
    # 4. 综合运势评分
    overall_score = 50 + wuxing_score - 50 + lucky_factor
    overall_score += random.randint(-5, 5)
    overall_score = max(20, min(95, overall_score))
    
    # 5. 分维度评分
    love_score = calculate_love_fortune(chart, target_date)
    career_score = calculate_career_fortune(chart, target_date)
    wealth_score = calculate_wealth_fortune(chart, target_date)
    health_score = 60 + random.randint(-10, 15)
    
    # 6. 宜忌列表
    do_list = generate_do_list(overall_score, day_wuxing)
    avoid_list = generate_avoid_list(overall_score, day_wuxing)
    
    # 7. 幸运元素
    lucky_color = get_lucky_color(day_wuxing)
    lucky_number = get_lucky_number(target_date)
    lucky_direction = get_lucky_direction(day_wuxing)
    
    # 8. 运势短语
    phrase = generate_fortune_phrase(overall_score)
    
    return {
        'fortune_date': str(target_date),
        'year_ganzhi': year_ganzhi,
        'month_ganzhi': month_ganzhi,
        'day_ganzhi': day_ganzhi,
        'overall_score': overall_score,
        'love_score': love_score,
        'career_score': career_score,
        'wealth_score': wealth_score,
        'health_score': health_score,
        'lucky_color': lucky_color,
        'lucky_number': lucky_number,
        'lucky_direction': lucky_direction,
        'do_list': json.dumps(do_list),
        'avoid_list': json.dumps(avoid_list),
        'phrase': phrase
    }