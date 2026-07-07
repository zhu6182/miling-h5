from typing import Dict, Any, List
from lunar_python import Solar, Lunar, EightChar


def calculate_bazi(
    date_str: str,
    hour_index: int,
    gender: str,
    is_lunar: bool = False,
    is_leap: bool = False,
) -> Dict[str, Any]:
    """
    计算八字排盘

    Args:
        date_str: 日期字符串，格式 YYYY-MM-DD（公历或农历）
        hour_index: 时辰索引 0=子, 1=丑, ..., 11=亥
        gender: 'male' 或 'female'
        is_lunar: 是否农历
        is_leap: 是否闰月
    """
    hour_map = {
        0: (23, 30), 1: (1, 30), 2: (3, 30), 3: (5, 30),
        4: (7, 30), 5: (9, 30), 6: (11, 30), 7: (13, 30),
        8: (15, 30), 9: (17, 30), 10: (19, 30), 11: (21, 30),
    }
    hour, minute = hour_map.get(hour_index, (12, 0))

    if is_lunar:
        parts = date_str.split('-')
        year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
        if is_leap:
            month = -month
        lunar = Lunar.fromYmdHms(year, month, day, hour, minute, 0)
    else:
        parts = date_str.split('-')
        year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
        solar = Solar.fromYmdHms(year, month, day, hour, minute, 0)
        lunar = solar.getLunar()

    ec = lunar.getEightChar()

    gender_cn = '男' if gender == 'male' else '女'

    # 藏干
    hidden_stems = {
        'year': ec.getYearHideGan(),
        'month': ec.getMonthHideGan(),
        'day': ec.getDayHideGan(),
        'hour': ec.getTimeHideGan(),
    }

    # 十神
    ten_gods_gan = {
        'year': ec.getYearShiShenGan(),
        'month': ec.getMonthShiShenGan(),
        'day': '日主',
        'hour': ec.getTimeShiShenGan(),
    }
    ten_gods_zhi = {
        'year': ec.getYearShiShenZhi(),
        'month': ec.getMonthShiShenZhi(),
        'day': ec.getDayShiShenZhi(),
        'hour': ec.getTimeShiShenZhi(),
    }

    # 纳音
    nayin = {
        'year': ec.getYearNaYin(),
        'month': ec.getMonthNaYin(),
        'day': ec.getDayNaYin(),
        'hour': ec.getTimeNaYin(),
    }

    # 五行
    wuxing_gan = {
        'year': _get_wuxing(ec.getYearGan()),
        'month': _get_wuxing(ec.getMonthGan()),
        'day': _get_wuxing(ec.getDayGan()),
        'hour': _get_wuxing(ec.getTimeGan()),
    }
    wuxing_zhi = {
        'year': _get_zhi_wuxing(ec.getYearZhi()),
        'month': _get_zhi_wuxing(ec.getMonthZhi()),
        'day': _get_zhi_wuxing(ec.getDayZhi()),
        'hour': _get_zhi_wuxing(ec.getTimeZhi()),
    }

    # 五行统计
    wuxing_count = _count_wuxing(ec)

    # 大运
    dayun_list = []
    try:
        yun = ec.getYun(gender_cn)
        start_year = yun.getStartYear()
        start_month = yun.getStartMonth()
        start_day = yun.getStartDay()
        da_yun = yun.getDaYun()
        for i, dy in enumerate(da_yun):
            if i == 0:
                continue
            ganzhi = dy.getGanZhi()
            if ganzhi:
                dayun_list.append({
                    'index': i,
                    'ganzhi': ganzhi,
                    'start_age': start_year + (i - 1) * 10,
                    'xun': dy.getXun(),
                    'xunkong': dy.getXunKong(),
                })
    except Exception:
        start_year = 0
        start_month = 0
        start_day = 0

    # 十二长生
    di_shi = {
        'year': ec.getYearDiShi(),
        'month': ec.getMonthDiShi(),
        'day': ec.getDayDiShi(),
        'hour': ec.getTimeDiShi(),
    }

    # 旬空
    xun_kong = {
        'year': f"{ec.getYearXun()}旬空{ec.getYearXunKong()}",
        'month': f"{ec.getMonthXun()}旬空{ec.getMonthXunKong()}",
        'day': f"{ec.getDayXun()}旬空{ec.getDayXunKong()}",
        'hour': f"{ec.getTimeXun()}旬空{ec.getTimeXunKong()}",
    }

    # 神煞（基础）
    shensha_list = _get_shensha(ec, gender_cn)

    # 农历信息
    lunar_str = lunar.toString()
    lunar_year_cn = lunar.getYearInGanZhi() + '年'
    lunar_month_cn = lunar.getMonthInChinese() + '月'
    lunar_day_cn = lunar.getDayInChinese()
    ganzhi_year = ec.getYear()
    ganzhi_month = ec.getMonth()
    ganzhi_day = ec.getDay()
    ganzhi_hour = ec.getTime()

    result = {
        'solar_date': date_str if not is_lunar else (lunar.getSolar().toString() if lunar else ''),
        'lunar_date': f"{lunar_year_cn}{lunar_month_cn}{lunar_day_cn}",
        'lunar_year': lunar.getYear(),
        'lunar_month': lunar.getMonth(),
        'lunar_day': lunar.getDay(),
        'gender': gender,
        'gender_cn': gender_cn,
        'hour_index': hour_index,
        'hour_name': _get_hour_name(hour_index),

        # 四柱
        'pillars': {
            'year': {
                'gan': ec.getYearGan(),
                'zhi': ec.getYearZhi(),
                'ganzhi': ganzhi_year,
            },
            'month': {
                'gan': ec.getMonthGan(),
                'zhi': ec.getMonthZhi(),
                'ganzhi': ganzhi_month,
            },
            'day': {
                'gan': ec.getDayGan(),
                'zhi': ec.getDayZhi(),
                'ganzhi': ganzhi_day,
            },
            'hour': {
                'gan': ec.getTimeGan(),
                'zhi': ec.getTimeZhi(),
                'ganzhi': ganzhi_hour,
            },
        },

        # 藏干
        'hidden_stems': hidden_stems,

        # 十神
        'ten_gods': {
            'gan': ten_gods_gan,
            'zhi': ten_gods_zhi,
        },

        # 纳音
        'nayin': nayin,

        # 五行
        'wuxing': {
            'gan': wuxing_gan,
            'zhi': wuxing_zhi,
            'count': wuxing_count,
        },

        # 十二长生
        'di_shi': di_shi,

        # 旬空
        'xun_kong': xun_kong,

        # 神煞
        'shensha': shensha_list,

        # 大运
        'dayun': {
            'start_year': start_year,
            'start_month': start_month,
            'start_day': start_day,
            'list': dayun_list,
        },
    }

    return result


WUXING_MAP = {
    '甲': '木', '乙': '木',
    '丙': '火', '丁': '火',
    '戊': '土', '己': '土',
    '庚': '金', '辛': '金',
    '壬': '水', '癸': '水',
}

ZHI_WUXING_MAP = {
    '子': '水', '丑': '土', '寅': '木', '卯': '木',
    '辰': '土', '巳': '火', '午': '火', '未': '土',
    '申': '金', '酉': '金', '戌': '土', '亥': '水',
}

HOUR_NAMES = {
    0: '子时 (23:00-01:00)',
    1: '丑时 (01:00-03:00)',
    2: '寅时 (03:00-05:00)',
    3: '卯时 (05:00-07:00)',
    4: '辰时 (07:00-09:00)',
    5: '巳时 (09:00-11:00)',
    6: '午时 (11:00-13:00)',
    7: '未时 (13:00-15:00)',
    8: '申时 (15:00-17:00)',
    9: '酉时 (17:00-19:00)',
    10: '戌时 (19:00-21:00)',
    11: '亥时 (21:00-23:00)',
}


def _get_wuxing(gan: str) -> str:
    return WUXING_MAP.get(gan, '')


def _get_zhi_wuxing(zhi: str) -> str:
    return ZHI_WUXING_MAP.get(zhi, '')


def _get_hour_name(index: int) -> str:
    return HOUR_NAMES.get(index, '')


def _count_wuxing(ec: EightChar) -> Dict[str, int]:
    """统计五行数量（天干 + 地支本气）"""
    count = {'金': 0, '木': 0, '水': 0, '火': 0, '土': 0}

    for gan in [ec.getYearGan(), ec.getMonthGan(), ec.getDayGan(), ec.getTimeGan()]:
        wx = WUXING_MAP.get(gan)
        if wx:
            count[wx] += 1

    for zhi in [ec.getYearZhi(), ec.getMonthZhi(), ec.getDayZhi(), ec.getTimeZhi()]:
        wx = ZHI_WUXING_MAP.get(zhi)
        if wx:
            count[wx] += 1

    return count


def _get_shensha(ec: EightChar, gender: str) -> List[str]:
    """基础神煞列表"""
    result = []
    day_zhi = ec.getDayZhi()
    year_zhi = ec.getYearZhi()

    # 桃花（咸池）
    taohua_map = {
        '申子辰': '酉', '亥卯未': '子',
        '寅午戌': '卯', '巳酉丑': '午',
    }
    for key, val in taohua_map.items():
        if year_zhi in key:
            if day_zhi == val:
                result.append('桃花')
            break

    # 驿马
    yima_map = {
        '申子辰': '寅', '亥卯未': '巳',
        '寅午戌': '申', '巳酉丑': '亥',
    }
    for key, val in yima_map.items():
        if year_zhi in key:
            if day_zhi == val:
                result.append('驿马')
            break

    # 天乙贵人（日干起）
    day_gan = ec.getDayGan()
    tianyi_map = {
        '甲': ['丑', '未'], '戊': ['丑', '未'], '庚': ['丑', '未'],
        '乙': ['子', '申'], '己': ['子', '申'],
        '丙': ['亥', '酉'], '丁': ['亥', '酉'],
        '壬': ['卯', '巳'], '癸': ['卯', '巳'],
    }
    if day_gan in tianyi_map:
        for zhi in [year_zhi, ec.getMonthZhi(), ec.getTimeZhi()]:
            if zhi in tianyi_map[day_gan]:
                result.append('天乙贵人')
                break

    # 太极贵人
    taiji_map = {
        '甲': ['子', '午'], '乙': ['卯', '酉'],
        '丙': ['卯', '酉'], '丁': ['申', '亥'],
        '戊': ['辰', '戌', '丑', '未'],
        '己': ['辰', '戌', '丑', '未'],
        '庚': ['寅', '亥'], '辛': ['寅', '亥'],
        '壬': ['卯', '巳'], '癸': ['巳', '丑'],
    }
    if day_gan in taiji_map:
        for zhi in [year_zhi, ec.getMonthZhi(), ec.getDayZhi(), ec.getTimeZhi()]:
            if zhi in taiji_map[day_gan]:
                result.append('太极贵人')
                break

    # 福星贵人
    fuxing_map = {
        '甲': ['寅', '丙'], '乙': ['子', '申'],
        '丙': ['寅', '辰'], '丁': ['酉', '亥'],
        '戊': ['申', '子'], '己': ['丑', '亥'],
        '庚': ['午', '寅'], '辛': ['子', '巳'],
        '壬': ['申', '辰'], '癸': ['卯', '巳'],
    }

    # 文昌贵人
    wenchang_map = {
        '甲': '巳', '乙': '午',
        '丙': '申', '丁': '酉',
        '戊': '申', '己': '酉',
        '庚': '亥', '辛': '子',
        '壬': '寅', '癸': '卯',
    }
    if day_gan in wenchang_map:
        for zhi in [year_zhi, ec.getMonthZhi(), ec.getDayZhi(), ec.getTimeZhi()]:
            if zhi == wenchang_map[day_gan]:
                result.append('文昌贵人')
                break

    return result
