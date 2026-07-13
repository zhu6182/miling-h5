import json
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime


def analyze_love_match(chart_a: Dict, chart_b: Dict) -> Dict[str, Any]:
    """姻缘匹配分析"""
    love_a = None
    love_b = None
    for p in chart_a.get('palaces', []):
        if p.get('name') == '夫妻宫':
            love_a = p
            break
    for p in chart_b.get('palaces', []):
        if p.get('name') == '夫妻宫':
            love_b = p
            break

    score = 65
    stars_a = set(love_a.get('major_stars', []) if love_a else [])
    stars_b = set(love_b.get('major_stars', []) if love_b else [])

    harmony_pairs = [
        ({'紫微', '天府'}, {'紫微', '天府'}),
        ({'天同', '天梁'}, {'天同', '天梁'}),
        ({'太阳', '太阴'}, {'太阳', '太阴'}),
    ]
    conflict_pairs = [
        ({'七杀', '破军'}, {'七杀', '破军'}),
        ({'廉贞', '贪狼'}, {'廉贞', '贪狼'}),
    ]

    for hp in harmony_pairs:
        if stars_a == hp[0] and stars_b == hp[1]:
            score += 15
        if stars_b == hp[0] and stars_a == hp[1]:
            score += 15

    for cp in conflict_pairs:
        if stars_a == cp[0] and stars_b == cp[1]:
            score -= 10
        if stars_b == cp[0] and stars_a == cp[1]:
            score -= 10

    huajia_a = any(m.get('mutagen') == '忌' for m in (love_a.get('mutagens', []) if love_a else []))
    huajia_b = any(m.get('mutagen') == '忌' for m in (love_b.get('mutagens', []) if love_b else []))
    if huajia_a and huajia_b:
        score += 10

    score = min(95, max(30, score))

    tags = []
    if score >= 80:
        tags = ["🌟 天作之合", "❤️ 缘分极深"]
    elif score >= 65:
        tags = ["✨ 较有默契", "🤝 需多沟通"]
    else:
        tags = ["💭 差异较大", "⚡ 互补与冲突并存"]

    return {
        "score": score,
        "tags": tags,
        "summary": _love_summary(score, stars_a, stars_b),
        "advice": _love_advice(score, stars_a, stars_b),
    }


def analyze_career_match(chart_a: Dict, chart_b: Dict, name_a: str = "A", name_b: str = "B") -> Dict[str, Any]:
    """事业合作匹配分析"""
    career_a = None
    career_b = None
    wealth_a = None
    wealth_b = None
    for p in chart_a.get('palaces', []):
        if p.get('name') == '官禄宫':
            career_a = p
        if p.get('name') == '财帛宫':
            wealth_a = p
    for p in chart_b.get('palaces', []):
        if p.get('name') == '官禄宫':
            career_b = p
        if p.get('name') == '财帛宫':
            wealth_b = p

    score = 60
    stars_a = set(career_a.get('major_stars', []) if career_a else [])
    stars_b = set(career_b.get('major_stars', []) if career_b else [])

    opener_a = set(career_a.get('major_stars', []) if career_a else []) & {'贪狼', '破军', '七杀', '廉贞'}
    opener_b = set(career_b.get('major_stars', []) if career_b else []) & {'贪狼', '破军', '七杀', '廉贞'}
    keeper_a = set(career_a.get('major_stars', []) if career_a else []) & {'天府', '天同', '太阴', '天梁'}
    keeper_b = set(career_b.get('major_stars', []) if career_b else []) & {'天府', '天同', '太阴', '天梁'}

    if opener_a and keeper_b or opener_b and keeper_a:
        score += 20
    if opener_a and opener_b:
        score += 5
    if keeper_a and keeper_b:
        score += 5

    wealth_stars_a = set(wealth_a.get('major_stars', []) if wealth_a else [])
    wealth_stars_b = set(wealth_b.get('major_stars', []) if wealth_b else [])
    if wealth_stars_a & wealth_stars_b:
        score += 5

    score = min(95, max(30, score))

    roles = []
    if opener_a and keeper_a:
        roles.append(f"{name_a}是综合型(开拓+稳健)")
    elif opener_a:
        roles.append(f"{name_a}是开拓型")
    elif keeper_a:
        roles.append(f"{name_a}是稳健型")
    
    if opener_b and keeper_b:
        roles.append(f"{name_b}是综合型(开拓+稳健)")
    elif opener_b:
        roles.append(f"{name_b}是开拓型")
    elif keeper_b:
        roles.append(f"{name_b}是稳健型")

    tags = []
    if score >= 80:
        tags = ["💼 黄金搭档", "🚀 互补双赢"]
    elif score >= 65:
        tags = ["🤝 各有优势", "💡 需明确分工"]
    else:
        tags = ["⚡ 风格差异大", "🗣 加强沟通"]

    return {
        "score": score,
        "tags": tags,
        "summary": f"合作指数{score}分。{' '.join(roles) if roles else '特质待进一步分析'}。",
        "advice": _career_advice(score, roles),
        "roles": roles,
    }


def analyze_friendship_match(chart_a: Dict, chart_b: Dict) -> Dict[str, Any]:
    """朋友缘分分析"""
    score = 60
    friends_a = None
    friends_b = None
    for p in chart_a.get('palaces', []):
        if p.get('name') == '交友宫':
            friends_a = p
    for p in chart_b.get('palaces', []):
        if p.get('name') == '交友宫':
            friends_b = p

    stars_a = set(friends_a.get('major_stars', []) if friends_a else [])
    stars_b = set(friends_b.get('major_stars', []) if friends_b else [])

    good_friend_stars = {'天同', '天梁', '太阴', '太阳'}
    if stars_a & good_friend_stars and stars_b & good_friend_stars:
        score += 15
    if stars_a & {'贪狼', '武曲'} or stars_b & {'贪狼', '武曲'}:
        score += 5
    if stars_a & {'巨门', '七杀'} or stars_b & {'巨门', '七杀'}:
        score -= 5

    score = min(95, max(30, score))

    tags = []
    if score >= 75:
        tags = ["👯 知己型友谊", "💫 精神共鸣"]
    elif score >= 55:
        tags = ["🤝 伙伴型友谊", "🌱 共同成长"]
    else:
        tags = ["🌪 关系较复杂", "⏰ 需要磨合"]

    return {
        "score": score,
        "tags": tags,
        "summary": f"友谊指数{score}分。",
        "advice": _friendship_advice(score),
    }


def analyze_mentor_match(chart_a: Dict, chart_b: Dict) -> Dict[str, Any]:
    """贵人缘分分析"""
    score = 50
    for p in chart_a.get('palaces', []):
        if p.get('name') == '命宫':
            main_stars = set(p.get('major_stars', []))
            if main_stars & {'紫微', '天机', '天梁'}:
                score += 15
            if main_stars & {'太阳', '武曲'}:
                score += 10
    for p in chart_b.get('palaces', []):
        if p.get('name') == '命宫':
            main_stars = set(p.get('major_stars', []))
            if main_stars & {'太阴', '天同'}:
                score += 10

    year_hua_a = [m for m in chart_a.get('year_mutagens', []) if m.get('mutagen') == '禄']
    year_hua_b = [m for m in chart_b.get('year_mutagens', []) if m.get('mutagen') == '禄']
    if len(year_hua_a) > 2:
        score += 5
    if len(year_hua_b) > 2:
        score += 5

    score = min(95, max(30, score))

    tags = []
    if score >= 70:
        tags = ["🌟 贵人运强", "✨ 相互助力"]
    elif score >= 50:
        tags = ["💫 有一定缘分", "🤝 需主动经营"]
    else:
        tags = ["🌧 缘分较浅", "💪 需靠自己"]

    return {
        "score": score,
        "tags": tags,
        "summary": f"贵人指数{score}分。",
        "advice": _mentor_advice(score),
    }


def calculate_full_match(chart_a: Dict, chart_b: Dict, match_type: str = "all",
                         name_a: str = "A", name_b: str = "B") -> Dict[str, Any]:
    """完整匹配分析"""
    results = {}

    # 同性别跳过姻缘配对
    gender_a = chart_a.get('gender', '')
    gender_b = chart_b.get('gender', '')
    same_gender = gender_a == gender_b

    if match_type in ("all", "love") and not same_gender:
        results["love"] = analyze_love_match(chart_a, chart_b)
    if match_type in ("all", "career"):
        results["career"] = analyze_career_match(chart_a, chart_b, name_a, name_b)
    if match_type in ("all", "friendship"):
        results["friendship"] = analyze_friendship_match(chart_a, chart_b)
    if match_type in ("all", "mentor"):
        results["mentor"] = analyze_mentor_match(chart_a, chart_b)

    scores = [r["score"] for r in results.values()]
    overall_score = int(sum(scores) / len(scores)) if scores else 50

    return {
        "overall_score": overall_score,
        "dimensions": results,
        "soul_palace_a": _get_soul_stars(chart_a),
        "soul_palace_b": _get_soul_stars(chart_b),
        "five_elements_a": chart_a.get('five_elements', ''),
        "five_elements_b": chart_b.get('five_elements', ''),
        "generated_at": datetime.now().isoformat(),
    }


def _get_soul_stars(chart):
    for p in chart.get('palaces', []):
        if '命宫' in p.get('tags', []):
            return '·'.join(p.get('major_stars', [])[:2]) or '空宫'
    return '未知'


def _love_summary(score, stars_a, stars_b):
    if score >= 80:
        return "你们在感情模式上有天然的默契，相处起来比较舒服。"
    elif score >= 65:
        return "感情上各有特点，需要一些磨合期，但潜力不错。"
    else:
        return "感情上容易有摩擦，但处理好了反而能互相促进。"


def _love_advice(score, stars_a, stars_b):
    if score >= 80:
        return "珍惜这份缘分，多沟通少猜疑，感情会越来越稳。"
    elif score >= 65:
        return "遇到矛盾别冷战，主动说出来，一起找解决办法。"
    else:
        return "感情上容易有误读，说话前先确认对方的意思。"


def _career_advice(score, roles):
    if score >= 80:
        return "你们是非常好的搭档，各展所长，1+1>2。"
    elif score >= 65:
        return "合作时明确分工，发挥各自优势，效率会更高。"
    else:
        return "合作前先聊清楚目标和分工，避免各干各的。"


def _friendship_advice(score):
    if score >= 75:
        return "你们比较投缘，可以发展成长期的朋友关系。"
    elif score >= 55:
        return "友谊需要经营，多联系多分享，关系会更稳固。"
    else:
        return "不是类型的朋友，但也能在特定领域互相支持。"


def _mentor_advice(score):
    if score >= 70:
        return "你们的缘分比较深，在一起往往会互相帮助。"
    elif score >= 50:
        return "遇到困难可以向对方请教，但别完全依赖。"
    else:
        return "各自靠自己更现实，有机会可以互相学习。"


def generate_qr_code() -> str:
    """生成唯一的匹配码"""
    return uuid.uuid4().hex[:12].upper()


def get_match_summary_text(match_result: Dict) -> str:
    """生成匹配结果的文字摘要"""
    dims = match_result.get('dimensions', {})
    lines = []
    lines.append(f"【综合匹配指数】{match_result['overall_score']}分")
    if 'love' in dims:
        lines.append(f"💖 姻缘：{dims['love']['score']}分")
    if 'career' in dims:
        lines.append(f"💼 事业：{dims['career']['score']}分")
    if 'friendship' in dims:
        lines.append(f"🤝 友谊：{dims['friendship']['score']}分")
    if 'mentor' in dims:
        lines.append(f"🌟 贵人：{dims['mentor']['score']}分")
    return '\n'.join(lines)
