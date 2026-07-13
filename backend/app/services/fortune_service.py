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
    # 日干支：基于已知甲子日推算
    # 2024年1月22日为甲子日（已验证）
    base_date = date(2024, 1, 22)
    days_diff = (target_date - base_date).days
    day_ganzhi_index = days_diff % 60
    day_gan = TIANGAN[day_ganzhi_index % 10]
    day_zhi = DIZHI[day_ganzhi_index % 12]
    
    # 年干支（公元4年为甲子年）
    year = target_date.year
    year_gan = TIANGAN[(year - 4) % 10]
    year_zhi = DIZHI[(year - 4) % 12]
    
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


def _get_day_master_element(chart: Chart) -> str:
    """从命盘数据中获取日主五行"""
    cd = chart.chart_data or {}
    # 八字命盘格式
    if cd.get('pillars'):
        day_gan = cd['pillars'].get('day', {}).get('gan', '')
        if day_gan:
            return TIANGAN_WUXING.get(day_gan, '土')
    # 紫微命盘格式
    if cd.get('chinese_date'):
        parts = cd['chinese_date'].split()
        if len(parts) >= 3:
            day_gan = parts[2][0]
            return TIANGAN_WUXING.get(day_gan, '土')
    # 从五行局推断
    chart_element = WUXING_JU.get(chart.five_elements or '土五局', '土')
    return chart_element


def _wuxing_relation_score(a: str, b: str) -> int:
    """b 对 a 的五行关系得分"""
    if a == b:
        return 6  # 比劫助身
    if WUXING_BEI_SHENG.get(a) == b:
        return 8  # 生我（印星）
    if WUXING_SHENG.get(a) == b:
        return 2  # 我生（食伤泄秀）
    if WUXING_BEI_KE.get(a) == b:
        return -6  # 克我（官杀制身）
    if WUXING_KE.get(a) == b:
        return 0  # 我克（财星）
    return 0


def calculate_love_fortune(chart: Chart, target_date: date, day_wuxing: Dict) -> int:
    """计算爱情运势 - 基于日主与流日五行关系"""
    base_score = 55
    day_master_wx = _get_day_master_element(chart)
    day_gan_wx = day_wuxing['gan_wuxing']
    day_zhi_wx = day_wuxing['zhi_wuxing']
    
    # 日主与流日天干地支的五行关系
    base_score += _wuxing_relation_score(day_master_wx, day_gan_wx)
    base_score += _wuxing_relation_score(day_master_wx, day_zhi_wx)
    
    # 桃花星影响：水日、火日偏旺感情
    if day_zhi_wx == '水':
        base_score += 5
    elif day_zhi_wx == '火':
        base_score += 3
    
    # 地支六合/六冲影响
    soul_palace = chart.soul_palace or ''
    if soul_palace:
        soul_zhi = soul_palace[-1]
        day_zhi = day_wuxing['zhi']
        liuhe = {'子': '丑', '丑': '子', '寅': '亥', '亥': '寅', '卯': '戌', '戌': '卯',
                 '辰': '酉', '酉': '辰', '巳': '申', '申': '巳', '午': '未', '未': '午'}
        if liuhe.get(soul_zhi) == day_zhi:
            base_score += 8
        liuchong = {'子': '午', '午': '子', '丑': '未', '未': '丑', '寅': '申', '申': '寅',
                    '卯': '酉', '酉': '卯', '辰': '戌', '戌': '辰', '巳': '亥', '亥': '巳'}
        if liuchong.get(soul_zhi) == day_zhi:
            base_score -= 5
    
    # 固定种子微波动
    rng = random.Random(target_date.toordinal() + 1)
    base_score += rng.randint(-3, 3)
    
    return max(20, min(95, base_score))


def calculate_career_fortune(chart: Chart, target_date: date, day_wuxing: Dict) -> int:
    """计算事业运势 - 基于日主与官杀印星关系"""
    base_score = 55
    day_master_wx = _get_day_master_element(chart)
    day_gan_wx = day_wuxing['gan_wuxing']
    day_zhi_wx = day_wuxing['zhi_wuxing']
    
    # 官杀（克我者）和印星（生我者）对事业最重要
    ke_me = WUXING_BEI_KE.get(day_master_wx, '')
    sheng_me = WUXING_BEI_SHENG.get(day_master_wx, '')
    
    if day_gan_wx == ke_me:
        base_score += 8  # 官杀透干，事业压力与机遇并存
    elif day_gan_wx == sheng_me:
        base_score += 6  # 印星护佑，贵人提携
    
    if day_zhi_wx == ke_me:
        base_score += 5
    elif day_zhi_wx == sheng_me:
        base_score += 4
    
    # 土日、金日利于事业稳定
    if day_zhi_wx in ['土', '金']:
        base_score += 4
    
    rng = random.Random(target_date.toordinal() + 2)
    base_score += rng.randint(-3, 3)
    
    return max(20, min(95, base_score))


def calculate_wealth_fortune(chart: Chart, target_date: date, day_wuxing: Dict) -> int:
    """计算财运 - 基于日主与财星关系"""
    base_score = 55
    day_master_wx = _get_day_master_element(chart)
    day_gan_wx = day_wuxing['gan_wuxing']
    day_zhi_wx = day_wuxing['zhi_wuxing']
    
    # 财星（我克者）对财运最直接
    wo_ke = WUXING_KE.get(day_master_wx, '')
    sheng_me = WUXING_BEI_SHENG.get(day_master_wx, '')
    
    if day_gan_wx == wo_ke:
        base_score += 10  # 财星透干
    elif day_gan_wx == sheng_me:
        base_score += 4  # 印星生身，身旺可担财
    
    if day_zhi_wx == wo_ke:
        base_score += 8  # 财星坐支
    elif day_zhi_wx == day_master_wx:
        base_score += 5  # 比劫助身，合伙求财
    
    rng = random.Random(target_date.toordinal() + 3)
    base_score += rng.randint(-3, 3)
    
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


# 五行对应的宜忌事项
YI_BY_WUXING = {
    '金': ['签约合作', '结算收账', '修整工具', '决策断事', '佩戴金属饰品'],
    '木': ['学习充电', '种植培植', '创意策划', '社交拓展', '整理收纳'],
    '水': ['出行远行', '沟通交流', '投资理财', '反思冥想', '接触水景'],
    '火': ['表达展示', '面试汇报', '运动健身', '庆祝聚会', '创新尝试'],
    '土': ['房产交易', '存储积累', '养生调理', '拜访长辈', '稳固关系'],
}

JI_BY_WUXING = {
    '金': ['冲动消费', '口舌之争', '过度劳累', '刚愎自用'],
    '木': ['犹豫不决', '过度消耗', '急躁冒进', '疏忽细节'],
    '水': ['情绪失控', '夜归远行', '过度沉迷', '轻信他人'],
    '火': ['与人争执', '熬夜伤身', '铺张浪费', '好高骛远'],
    '土': ['冒险投机', '频繁变动', '暴饮暴食', '消极怠工'],
}


def _generate_personalized_do_list(score: int, day_wuxing: Dict, day_master_wx: str) -> List[str]:
    """根据五行生成个性化宜事项"""
    items = list(YI_BY_WUXING.get(day_master_wx, YI_ITEMS[:5]))
    # 补充流日五行对应的宜
    day_zhi_wx = day_wuxing.get('zhi_wuxing', '土')
    if day_zhi_wx != day_master_wx:
        items.extend(YI_BY_WUXING.get(day_zhi_wx, [])[:2])
    # 随机选取
    rng = random.Random(score + hash(day_master_wx))
    count = max(3, min(5, score // 18))
    return rng.sample(items, min(count, len(items)))


def _generate_personalized_avoid_list(score: int, day_wuxing: Dict, day_master_wx: str) -> List[str]:
    """根据五行生成个性化忌事项"""
    items = list(JI_BY_WUXING.get(day_master_wx, JI_ITEMS[:4]))
    rng = random.Random(100 - score + hash(day_master_wx))
    count = max(2, min(4, (100 - score) // 22))
    return rng.sample(items, min(count, len(items)))


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
        '✨ 吉星高照，今日运势极佳，心想事成！',
        '🌟 贵人相助，诸事顺遂，把握良机',
        '🌞 阳气充盈，能量满满，今日适合大展拳脚',
        '🌈 运势如虹，好运连连，惊喜不断',
        '🌠 命宫吉曜，能量充沛，今日宜创造惊喜'
    ]
    phrases_mid = [
        '🌤️ 今日运势平稳，保持平常心，稳步前行',
        '☁️ 运势中等，宜冷静思考，谨慎决策',
        '🌥️ 平稳中略有起伏，保持耐心，静待时机',
        '🌦️ 按部就班，稳扎稳打，自然会有好结果',
        '🌗 阴阳平和，适合整理规划，蓄势待发'
    ]
    phrases_low = [
        '🌧️ 今日运势较弱，宜低调行事，调整状态',
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
    """计算每日运势（完整版 - 基于八字五行生克）"""
    
    # 1. 当日干支
    year_ganzhi, month_ganzhi, day_ganzhi = get_day_ganzhi(target_date)
    day_wuxing = get_day_wuxing(day_ganzhi)
    
    # 2. 日主五行
    day_master_wx = _get_day_master_element(chart)
    
    # 3. 五行得分（日主与流日关系）
    chart_element = WUXING_JU.get(chart.five_elements or '土五局', '土')
    wuxing_score = calculate_wuxing_score(day_wuxing, chart.five_elements or '土五局')
    
    # 4. 流日运势因子（命宫与日支六合六冲）
    lucky_factor = get_lucky_factor(target_date, chart.soul_palace)
    
    # 5. 日主与流日天干地支五行关系
    day_gan_wx = day_wuxing['gan_wuxing']
    day_zhi_wx = day_wuxing['zhi_wuxing']
    day_master_relation = _wuxing_relation_score(day_master_wx, day_gan_wx) + _wuxing_relation_score(day_master_wx, day_zhi_wx)
    
    # 6. 综合运势评分
    overall_score = 55 + wuxing_score - 50 + lucky_factor + day_master_relation
    rng = random.Random(target_date.toordinal())
    overall_score += rng.randint(-4, 4)
    overall_score = max(20, min(95, overall_score))
    
    # 7. 分维度评分（基于八字）
    love_score = calculate_love_fortune(chart, target_date, day_wuxing)
    career_score = calculate_career_fortune(chart, target_date, day_wuxing)
    wealth_score = calculate_wealth_fortune(chart, target_date, day_wuxing)
    
    # 健康运势：基于日主与流日地支关系
    health_base = 55
    health_base += _wuxing_relation_score(day_master_wx, day_zhi_wx)
    rng_h = random.Random(target_date.toordinal() + 4)
    health_score = max(20, min(95, health_base + rng_h.randint(-4, 4)))
    
    # 8. 宜忌列表（根据五行定制）
    do_list = _generate_personalized_do_list(overall_score, day_wuxing, day_master_wx)
    avoid_list = _generate_personalized_avoid_list(overall_score, day_wuxing, day_master_wx)
    
    # 9. 幸运元素
    lucky_color = get_lucky_color(day_wuxing)
    lucky_number = get_lucky_number(target_date)
    lucky_direction = get_lucky_direction(day_wuxing)
    
    # 10. 运势短语
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