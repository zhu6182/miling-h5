import json
from typing import Optional, Dict, Any

BRANCH_CN = {
    'ziEarthly': '子', 'chouEarthly': '丑', 'yinEarthly': '寅',
    'maoEarthly': '卯', 'chenEarthly': '辰', 'siEarthly': '巳',
    'wuEarthly': '午', 'weiEarthly': '未', 'shenEarthly': '申',
    'youEarthly': '酉', 'xuEarthly': '戌', 'haiEarthly': '亥',
}

STEM_CN = {
    'jiaHeavenly': '甲', 'yiHeavenly': '乙', 'bingHeavenly': '丙',
    'dingHeavenly': '丁', 'wuHeavenly': '戊', 'jiHeavenly': '己',
    'gengHeavenly': '庚', 'xinHeavenly': '辛', 'renHeavenly': '壬',
    'guiHeavenly': '癸',
}

FIVE_ELEMENTS_CN = {
    'water2': '水二局', 'wood3': '木三局', 'metal4': '金四局',
    'earth5': '土五局', 'fire6': '火六局',
}

MUTAGEN_CN = {'禄': '化禄', '权': '化权', '科': '化科', '忌': '化忌'}

HOUR_NAMES = {
    0: '早子时 (23:00-00:00)', 1: '丑时 (01:00-03:00)',
    2: '寅时 (03:00-05:00)', 3: '卯时 (05:00-07:00)',
    4: '辰时 (07:00-09:00)', 5: '巳时 (09:00-11:00)',
    6: '午时 (11:00-13:00)', 7: '未时 (13:00-15:00)',
    8: '申时 (15:00-17:00)', 9: '酉时 (17:00-19:00)',
    10: '戌时 (19:00-21:00)', 11: '亥时 (21:00-23:00)',
    12: '晚子时 (23:00-00:00)',
}


def translate_name(obj):
    if hasattr(obj, 'translate_name'):
        return obj.translate_name()
    return str(obj)


def calculate_chart(
    date_str: str,
    hour_index: int,
    gender: str,
    is_lunar: bool = False,
    is_leap: bool = False,
    language: str = 'zh-CN'
) -> Dict[str, Any]:
    from iztro_py import astro

    if is_lunar:
        chart = astro.by_lunar(date_str, hour_index, gender, is_leap, True, language)
    else:
        chart = astro.by_solar(date_str, hour_index, gender, language)

    soul_idx = chart.get_soul_palace().index
    body_idx = chart.get_body_palace().index

    fec = chart.five_elements_class
    five_elements = FIVE_ELEMENTS_CN.get(fec, fec)

    year_mutagens = []
    for p in chart.palaces:
        for s in list(p.major_stars) + list(p.minor_stars):
            if hasattr(s, 'mutagen') and s.mutagen:
                year_mutagens.append({
                    'star': translate_name(s),
                    'mutagen': MUTAGEN_CN.get(s.mutagen, s.mutagen),
                    'palace': translate_name(p),
                    'branch': BRANCH_CN.get(p.earthly_branch, p.earthly_branch),
                })

    palaces = []
    for p in chart.palaces:
        major = [translate_name(s) for s in p.major_stars]
        minor = [translate_name(s) for s in p.minor_stars]
        adj = [translate_name(s) for s in p.adjective_stars] if hasattr(p, 'adjective_stars') else []

        star_mutagens = []
        for s in list(p.major_stars) + list(p.minor_stars):
            if hasattr(s, 'mutagen') and s.mutagen:
                star_mutagens.append({
                    'star': translate_name(s),
                    'mutagen': s.mutagen,
                })

        dec = p.decadal
        decadal_range = f"{dec.range[0]}-{dec.range[1]}" if dec else ""
        decadal_stem = STEM_CN.get(dec.heavenly_stem, dec.heavenly_stem) if dec else ""
        decadal_branch = BRANCH_CN.get(dec.earthly_branch, dec.earthly_branch) if dec else ""

        is_empty = not major
        tags = []
        if p.index == soul_idx:
            tags.append('命宫')
        if p.index == body_idx:
            tags.append('身宫')

        palace_data = {
            'name': translate_name(p),
            'heavenly_stem': STEM_CN.get(p.heavenly_stem, p.heavenly_stem),
            'earthly_branch': BRANCH_CN.get(p.earthly_branch, p.earthly_branch),
            'dizhi': STEM_CN.get(p.heavenly_stem, '') + BRANCH_CN.get(p.earthly_branch, ''),
            'major_stars': major,
            'minor_stars': minor,
            'adjective_stars': adj[:5],
            'mutagens': star_mutagens,
            'is_empty': is_empty,
            'decadal_range': decadal_range,
            'decadal_dizhi': decadal_stem + decadal_branch,
            'tags': tags,
            'index': p.index,
        }
        palaces.append(palace_data)

    empty_palaces_result = chart.empty_palaces() if callable(getattr(chart, 'empty_palaces', None)) else []
    empty_palaces = [BRANCH_CN.get(ep.earthly_branch, str(ep)) for ep in empty_palaces_result]

    soul_palace_branch = BRANCH_CN.get(chart.earthly_branch_of_soul_palace, chart.earthly_branch_of_soul_palace)
    body_palace_branch = BRANCH_CN.get(chart.earthly_branch_of_body_palace, chart.earthly_branch_of_body_palace)

    result = {
        'solar_date': date_str if not is_lunar else None,
        'lunar_date': date_str if is_lunar else (chart.lunar_date if hasattr(chart, 'lunar_date') else None),
        'chinese_date': chart.chinese_date if hasattr(chart, 'chinese_date') else '',
        'gender': gender,
        'hour_index': hour_index,
        'hour_name': HOUR_NAMES.get(hour_index, ''),
        'five_elements': five_elements,
        'soul_palace_branch': soul_palace_branch,
        'body_palace_branch': body_palace_branch,
        'year_mutagens': year_mutagens,
        'empty_palaces': empty_palaces,
        'palaces': palaces,
    }
    return result
