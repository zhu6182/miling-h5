import uuid
import threading
import random
import json as json_module
import re
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from app.api.deps import get_current_user
from app.models.models import User
from app.services.bazi_service import calculate_bazi, WUXING_MAP, ZHI_WUXING_MAP
from app.services.ai_service import get_ai_provider
from app.services.task_manager import create_task, update_task, fail_task, get_task

# 天干地支序列（用于推算流年干支）
_GAN_LIST = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
_ZHI_LIST = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# 五行相生：木生火、火生土、土生金、金生水、水生木
_SHENG = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
# 五行相克：木克土、土克水、水克火、火克金、金克木
_KE = {'木': '土', '土': '水', '水': '火', '火': '金', '金': '木'}


def _get_wuxing_relation(a: str, b: str) -> str:
    """返回 b 对 a 的五行关系：同/生我/我生/克我/我克"""
    if a == b:
        return '同'
    if _SHENG.get(b) == a:
        return '生我'
    if _SHENG.get(a) == b:
        return '我生'
    if _KE.get(b) == a:
        return '克我'
    if _KE.get(a) == b:
        return '我克'
    return ''


def _generate_local_kline(bazi_data: dict, total_years: int = 60) -> list:
    """基于八字大运流年五行生克算法，本地生成K线数据（避免AI输出被截断）"""
    pillars = bazi_data['pillars']
    day_gan = pillars['day']['gan']
    day_wuxing = WUXING_MAP.get(day_gan, '木')

    dayun_list = bazi_data.get('dayun', {}).get('list', [])
    start_year_dy = bazi_data.get('dayun', {}).get('start_year', 1)

    try:
        birth_year = int(bazi_data.get('solar_date', '1990-01-01')[:4])
    except Exception:
        birth_year = 1990

    # 五行统计
    wuxing_count = bazi_data['wuxing']['count']
    sheng_wo = next((k for k, v in _SHENG.items() if v == day_wuxing), '')  # 生我者
    wo_sheng = _SHENG.get(day_wuxing, '')  # 我生者
    ke_wo = next((k for k, v in _KE.items() if v == day_wuxing), '')  # 克我者
    wo_ke = _KE.get(day_wuxing, '')  # 我克者

    # 身强身弱判断（简化）
    support = wuxing_count.get(day_wuxing, 0) + wuxing_count.get(sheng_wo, 0)
    consume = wuxing_count.get(wo_sheng, 0) + wuxing_count.get(wo_ke, 0) + wuxing_count.get(ke_wo, 0)
    is_strong = support >= consume

    if is_strong:
        favorable = [ke_wo, wo_ke, wo_sheng]
        unfavorable = [day_wuxing, sheng_wo]
    else:
        favorable = [day_wuxing, sheng_wo]
        unfavorable = [ke_wo, wo_ke, wo_sheng]

    # 出生年干支索引（用于推算流年干支）
    birth_ganzhi = pillars['year']['ganzhi']
    day_ganzhi = pillars['day']['ganzhi']  # 日柱干支（命主本身）
    try:
        birth_gan_idx = _GAN_LIST.index(birth_ganzhi[0])
        birth_zhi_idx = _ZHI_LIST.index(birth_ganzhi[1])
    except Exception:
        birth_gan_idx = 0
        birth_zhi_idx = 0

    relation_text = {
        '同': '比劫助身',
        '生我': '印星护佑',
        '我生': '食伤泄秀',
        '我克': '财星显达',
        '克我': '官杀制身',
    }

    chart_points = []
    prev_close = 50.0
    # 使用固定的随机种子，保证同一八字生成相同的K线（可复现）
    rng = random.Random(birth_year + (hash(day_ganzhi) % 10000))

    for age in range(1, total_years + 1):
        year = birth_year + age - 1
        gan_idx = (birth_gan_idx + age - 1) % 10
        zhi_idx = (birth_zhi_idx + age - 1) % 12
        year_gan = _GAN_LIST[gan_idx]
        year_zhi = _ZHI_LIST[zhi_idx]
        year_ganzhi = year_gan + year_zhi

        # 当前大运
        current_dayun = "童限"
        current_dy_gan_wx = None
        current_dy_zhi_wx = None
        for dy in dayun_list:
            if dy['start_age'] <= age < dy['start_age'] + 10:
                current_dayun = dy['ganzhi']
                current_dy_gan_wx = WUXING_MAP.get(current_dayun[0])
                current_dy_zhi_wx = ZHI_WUXING_MAP.get(current_dayun[1])
                break

        year_gan_wx = WUXING_MAP.get(year_gan)
        year_zhi_wx = ZHI_WUXING_MAP.get(year_zhi)

        # 基础分
        base_score = 58.0

        # ===== 大运影响（大幅增强，主导10年整体趋势）=====
        # 大运是人生的"气候带"，决定这10年的基本走向
        dy_bonus = 0
        if current_dy_gan_wx:
            if current_dy_gan_wx in favorable:
                dy_bonus += 12
            elif current_dy_gan_wx in unfavorable:
                dy_bonus -= 12
        if current_dy_zhi_wx:
            if current_dy_zhi_wx in favorable:
                dy_bonus += 16
            elif current_dy_zhi_wx in unfavorable:
                dy_bonus -= 16
        base_score += dy_bonus

        # 同一大运内的平滑过渡（让10年走势更连贯）
        if current_dayun != "童限":
            dy_start_age = None
            for dy in dayun_list:
                if dy['ganzhi'] == current_dayun:
                    dy_start_age = dy['start_age']
                    break
            if dy_start_age:
                year_in_dy = age - dy_start_age
                # 大运初期：趋势逐渐显现
                # 大运中期：趋势最强
                # 大运末期：趋势减弱，为下一大运做准备
                if year_in_dy <= 1:
                    base_score *= 0.92
                elif year_in_dy >= 8:
                    base_score *= 0.90
                else:
                    base_score *= 1.0

        # ===== 流年影响（在大运基础上的年度波动）=====
        # 天干影响
        if year_gan_wx in favorable:
            base_score += 8
        elif year_gan_wx in unfavorable:
            base_score -= 8

        # 地支影响（力量更大）
        if year_zhi_wx in favorable:
            base_score += 10
        elif year_zhi_wx in unfavorable:
            base_score -= 10

        # 流年与大运的关系（流年生助/克制大运）
        if current_dy_gan_wx and year_gan_wx:
            dy_gan_rel = _get_wuxing_relation(current_dy_gan_wx, year_gan_wx)
            if dy_gan_rel == '生我':
                base_score += 6
            elif dy_gan_rel == '克我':
                base_score -= 6
        if current_dy_zhi_wx and year_zhi_wx:
            dy_zhi_rel = _get_wuxing_relation(current_dy_zhi_wx, year_zhi_wx)
            if dy_zhi_rel == '生我':
                base_score += 8
            elif dy_zhi_rel == '克我':
                base_score -= 8

        # 大运交接年（转折年，波动最大）
        for dy in dayun_list:
            if dy['start_age'] == age:
                base_score += rng.uniform(-10, 10)
                break

        # 天克地冲年（流年与日柱天克地冲）——大波动
        if _gan_he_or_chong(year_gan, pillars['day']['gan']) == 'chong':
            base_score += rng.uniform(-8, 8)
        if _zhi_he_or_chong(year_zhi, pillars['day']['zhi']) == 'chong':
            base_score += rng.uniform(-10, 10)

        # 小幅随机波动（减少幅度，避免淹没大运趋势）
        base_score += rng.uniform(-3, 3)
        base_score = max(22, min(96, base_score))

        # 生成OHLC
        open_price = prev_close
        trend = (base_score - 50) / 50.0  # -1 ~ 1
        volatility = rng.uniform(2, 9)
        change = trend * volatility + rng.uniform(-3, 3)
        close_price = open_price + change
        # 向base_score靠拢
        close_price = close_price * 0.55 + base_score * 0.45
        close_price = max(20, min(98, close_price))

        high_price = max(open_price, close_price) + rng.uniform(0.5, 4.5)
        low_price = min(open_price, close_price) - rng.uniform(0.5, 4.5)
        high_price = min(100, high_price)
        low_price = max(10, low_price)

        score = int(close_price)

        # 生成reason
        gan_rel = _get_wuxing_relation(day_wuxing, year_gan_wx) if year_gan_wx else ''
        zhi_rel = _get_wuxing_relation(day_wuxing, year_zhi_wx) if year_zhi_wx else ''

        parts = []
        if zhi_rel:
            parts.append(relation_text.get(zhi_rel, ''))
        if gan_rel and gan_rel != zhi_rel:
            parts.append(relation_text.get(gan_rel, ''))
        if not parts:
            parts.append('运势平稳')

        is_favorable = (year_gan_wx in favorable) or (year_zhi_wx in favorable)
        is_unfavorable = (year_gan_wx in unfavorable) or (year_zhi_wx in unfavorable)

        if score >= 75:
            parts.append('吉星高照')
        elif score <= 40:
            parts.append('宜守不宜攻')
        elif is_favorable and score >= 60:
            parts.append('顺势可为')
        elif is_unfavorable and score <= 50:
            parts.append('谨防波折')

        reason = '，'.join(parts[:2])

        chart_points.append({
            'age': age,
            'year': year,
            'daYun': current_dayun,
            'ganZhi': year_ganzhi,
            'open': round(open_price, 1),
            'close': round(close_price, 1),
            'high': round(high_price, 1),
            'low': round(low_price, 1),
            'score': score,
            'reason': reason,
        })

        prev_close = close_price

    return chart_points


def _gan_he_or_chong(a: str, b: str) -> str:
    """天干冲克简化判断（甲庚冲、乙辛冲、丙壬冲、丁癸冲）"""
    chong_pairs = [('甲', '庚'), ('乙', '辛'), ('丙', '壬'), ('丁', '癸')]
    for p in chong_pairs:
        if (a == p[0] and b == p[1]) or (a == p[1] and b == p[0]):
            return 'chong'
    return ''


def _zhi_he_or_chong(a: str, b: str) -> str:
    """地支六冲：子午、丑未、寅申、卯酉、辰戌、巳亥"""
    chong_pairs = [('子', '午'), ('丑', '未'), ('寅', '申'), ('卯', '酉'), ('辰', '戌'), ('巳', '亥')]
    for p in chong_pairs:
        if (a == p[0] and b == p[1]) or (a == p[1] and b == p[0]):
            return 'chong'
    return ''

router = APIRouter(prefix="/bazi", tags=["八字"])


class BaziCalculateRequest(BaseModel):
    date_str: str
    hour_index: int
    gender: str
    is_lunar: Optional[bool] = False
    is_leap: Optional[bool] = False


class BaziReadingRequest(BaseModel):
    date_str: str
    hour_index: int
    gender: str
    is_lunar: Optional[bool] = False
    is_leap: Optional[bool] = False
    question: Optional[str] = ""


def _build_bazi_prompt(bazi_data: dict, question: str = "") -> str:
    pillars = bazi_data['pillars']
    nayin = bazi_data['nayin']
    wuxing = bazi_data['wuxing']['count']
    hidden = bazi_data['hidden_stems']
    ten_gods = bazi_data['ten_gods']

    prompt = f"""
你是一位资深的八字命理师，请根据以下八字排盘数据，为用户进行专业且通俗易懂的解读。

【基本信息】
命主：{bazi_data['gender_cn']}
出生：{bazi_data['solar_date']} {bazi_data['hour_name']}
农历：{bazi_data['lunar_date']}

【八字四柱】
年柱：{pillars['year']['ganzhi']}（{nayin['year']}）
月柱：{pillars['month']['ganzhi']}（{nayin['month']}）
日柱：{pillars['day']['ganzhi']}（{nayin['day']}）—— 日主
时柱：{pillars['hour']['ganzhi']}（{nayin['hour']}）

【五行统计（天干+地支藏干）】
金：{wuxing['金']} 木：{wuxing['木']} 水：{wuxing['水']} 火：{wuxing['火']} 土：{wuxing['土']}

【地支藏干】
年支 {pillars['year']['zhi']}：{'、'.join(hidden['year'])}
月支 {pillars['month']['zhi']}：{'、'.join(hidden['month'])}
日支 {pillars['day']['zhi']}：{'、'.join(hidden['day'])}
时支 {pillars['hour']['zhi']}：{'、'.join(hidden['hour'])}

【十神】
天干十神：年干 {ten_gods['gan']['year']}，月干 {ten_gods['gan']['month']}，时干 {ten_gods['gan']['hour']}
地支十神：年支 {'、'.join(ten_gods['zhi']['year'])}，月支 {'、'.join(ten_gods['zhi']['month'])}，日支 {'、'.join(ten_gods['zhi']['day'])}，时支 {'、'.join(ten_gods['zhi']['hour'])}

用户的问题：{question if question else '请做全面的八字解读'}

==================== 解读结构要求 ====================

请严格按照以下四大模块进行解读，用 HTML 格式输出（rich-text 可直接渲染）：

<h3>一、原局核心格局解读</h3>

<p><strong>1. 日主强弱与喜用神</strong></p>
<p>判断日主身强/身弱/中和，说明判断依据（得令、得地、得势），明确指出喜用神和忌神分别是什么五行。</p>

<p><strong>2. 十神性格与一生底色</strong></p>
<p>逐个分析八字中透出的重要十神，说明每个十神对命主性格和人生的影响。重点分析月柱（性格核心）、日柱（自身特质）、时柱（晚年/子女）、年柱（早年/长辈）。</p>

<p><strong>3. 感情、子女、家庭信息</strong></p>
<p>分析婚姻感情运势、配偶特征、子女缘分、家庭关系等。</p>

<h3>二、原局隐患与注意</h3>
<p>分析八字中的刑冲合害、五行偏枯等隐患，说明对人生哪些方面有影响：</p>
<ul>
<li>健康方面：对应哪些脏腑容易出问题</li>
<li>人事方面：哪些关系容易有矛盾</li>
</ul>

<h3>三、大运走势分析</h3>
<p>按大运顺序分析每步大运的吉凶趋势，重点讲当前大运和未来2-3步大运。每步大运说明：</p>
<ul>
<li>大运干支与原局的作用关系</li>
<li>对事业、财运、感情、健康的影响</li>
<li>整体运势评价</li>
</ul>

<h3>四、综合总结与建议</h3>
<p>整体评价命局层次，给出实用建议：</p>
<ul>
<li>事业发展方向建议</li>
<li>财运理财建议</li>
<li>感情经营建议</li>
<li>健康养生建议</li>
<li>改运/调候建议（根据喜用神）</li>
</ul>

==================== 输出要求 ====================

1. 语言风格：通俗易懂，有温度，像经验丰富的命理师面对面聊天，不要教科书式堆砌术语
2. 要有自己的判断和主见，不要模棱两可
3. 好的坏的都要说，客观真实，不要只说好话
4. 多用比喻和生活化的语言，少用生僻术语，用了要解释
5. 字数 1500-2500 字，内容要充实
6. 直接输出 HTML 内容，不要有其他说明文字
7. 标题用 h3，重点内容用 strong，次级强调用 em，列表用 ul/li，段落用 p

【重要】HTML 样式要求（深色星空主题）：
- 所有文字颜色用浅色系，适配深色背景
- h3 标题：金色 #d4a84b，字号 18px，加粗，上下有间距
- strong：金色 #d4a84b
- em：淡金色 #c9a050，斜体
- p：颜色 #c0c0d8，行高 1.8，字号 14px，段间距 12px
- ul/li：颜色 #b0b0c8，字号 14px，行高 1.8
- 整体不要有背景色，保持透明
- 每个大段之间（h3之间）要有空行

直接输出带 style 内联样式的 HTML，例如：
<h3 style="color:#d4a84b;font-size:18px;font-weight:bold;margin:20px 0 12px;">一、原局核心格局解读</h3>
<p style="color:#c0c0d8;font-size:14px;line-height:1.8;margin:10px 0;"><strong style="color:#d4a84b;">1. 日主强弱与喜用神</strong></p>
<p style="color:#c0c0d8;font-size:14px;line-height:1.8;margin:10px 0;">正文内容...</p>
<ul style="color:#b0b0c8;font-size:14px;line-height:1.8;padding-left:20px;">
<li style="margin:6px 0;">列表项</li>
</ul>
"""
    return prompt


@router.post("/calculate")
def bazi_calculate(
    req: BaziCalculateRequest,
    current_user: User = Depends(get_current_user),
):
    result = calculate_bazi(
        date_str=req.date_str,
        hour_index=req.hour_index,
        gender=req.gender,
        is_lunar=req.is_lunar,
        is_leap=req.is_leap,
    )
    return result


def _build_kline_analysis_prompt(bazi_data: dict) -> str:
    """构建人生K线的文字分析AI提示词（只生成7个维度的文字和评分，K线数据由后端本地生成）"""
    pillars = bazi_data['pillars']
    nayin = bazi_data['nayin']
    wuxing = bazi_data['wuxing']['count']
    hidden = bazi_data['hidden_stems']
    ten_gods = bazi_data['ten_gods']
    dayun = bazi_data.get('dayun', {})
    dayun_list = dayun.get('list', [])
    start_year = dayun.get('start_year', 1)

    dayun_str = ""
    for dy in dayun_list[:8]:
        dayun_str += f"{dy['start_age']}岁起: {dy['ganzhi']}\n"

    prompt = f"""
你是一位八字命理大师，精通命理推演。请根据以下八字信息，给出7个维度的命理文字分析和评分。

【八字四柱】
年柱：{pillars['year']['ganzhi']}（{nayin['year']}）
月柱：{pillars['month']['ganzhi']}（{nayin['month']}）
日柱：{pillars['day']['ganzhi']}（{nayin['day']}）—— 日主
时柱：{pillars['hour']['ganzhi']}（{nayin['hour']}）

【五行统计】
金：{wuxing['金']} 木：{wuxing['木']} 水：{wuxing['水']} 火：{wuxing['火']} 土：{wuxing['土']}

【地支藏干】
年支 {pillars['year']['zhi']}：{'、'.join(hidden['year'])}
月支 {pillars['month']['zhi']}：{'、'.join(hidden['month'])}
日支 {pillars['day']['zhi']}：{'、'.join(hidden['day'])}
时支 {pillars['hour']['zhi']}：{'、'.join(hidden['hour'])}

【十神】
天干十神：年干 {ten_gods['gan']['year']}，月干 {ten_gods['gan']['month']}，时干 {ten_gods['gan']['hour']}
地支十神：年支 {'、'.join(ten_gods['zhi']['year'])}，月支 {'、'.join(ten_gods['zhi']['month'])}，日支 {'、'.join(ten_gods['zhi']['day'])}，时支 {'、'.join(ten_gods['zhi']['hour'])}

【大运】
起运：{start_year}岁
{dayun_str}

只返回以下JSON结构（不要有任何其他文字，不要markdown代码块）:
{{
  "summary": "命理总评（50字以内）",
  "summaryScore": 75,
  "personality": "性格分析（40字以内）",
  "personalityScore": 75,
  "industry": "事业分析（40字以内）",
  "industryScore": 75,
  "wealth": "财富分析（40字以内）",
  "wealthScore": 75,
  "marriage": "婚姻分析（40字以内）",
  "marriageScore": 75,
  "health": "健康分析（30字以内）",
  "healthScore": 75,
  "family": "六亲分析（30字以内）",
  "familyScore": 75
}}

要求：
1. 评分0-100，要有差异，不要都是75
2. 文字要具体有内容，不要空话套话
3. 只返回JSON，不要有其他任何文字
"""
    return prompt


def _parse_json_loose(text: str):
    """容错解析AI返回的JSON"""
    if not text:
        return None
    start = text.find('{')
    end = text.rfind('}') + 1
    if start < 0 or end <= start:
        return None
    json_str = text[start:end]
    try:
        return json_module.loads(json_str)
    except json_module.JSONDecodeError:
        pass
    # 清理
    cleaned = re.sub(r'```json\s*', '', json_str)
    cleaned = re.sub(r'```\s*', '', cleaned)
    cleaned = re.sub(r',\s*}', '}', cleaned)
    cleaned = re.sub(r',\s*]', ']', cleaned)
    cleaned = re.sub(r'[\x00-\x1f]', '', cleaned)
    try:
        return json_module.loads(cleaned)
    except json_module.JSONDecodeError:
        try:
            return json_module.loads(cleaned, strict=False)
        except Exception:
            return None


def _generate_dayun_analysis(bazi_data: dict, chart_points: list) -> list:
    """生成详细的大运解读数据"""
    dayun_list = bazi_data.get('dayun', {}).get('list', [])
    pillars = bazi_data['pillars']
    day_gan = pillars['day']['gan']
    day_wx = WUXING_MAP.get(day_gan, '木')
    wuxing_count = bazi_data['wuxing']['count']

    sheng_wo = next((k for k, v in _SHENG.items() if v == day_wx), '')
    wo_sheng = _SHENG.get(day_wx, '')
    ke_wo = next((k for k, v in _KE.items() if v == day_wx), '')
    wo_ke = _KE.get(day_wx, '')
    support = wuxing_count.get(day_wx, 0) + wuxing_count.get(sheng_wo, 0)
    consume = wuxing_count.get(wo_sheng, 0) + wuxing_count.get(wo_ke, 0) + wuxing_count.get(ke_wo, 0)
    is_strong = support >= consume

    if is_strong:
        favorable = [ke_wo, wo_ke, wo_sheng]
        unfavorable = [day_wx, sheng_wo]
    else:
        favorable = [day_wx, sheng_wo]
        unfavorable = [ke_wo, wo_ke, wo_sheng]

    ten_god_names = {
        '同': '比肩', '生我': '印星', '我生': '食伤', '我克': '财星', '克我': '官杀'
    }

    dayun_analysis = []
    for dy in dayun_list[:10]:
        start_age = dy['start_age']
        ganzhi = dy['ganzhi']
        dy_gan = ganzhi[0]
        dy_zhi = ganzhi[1]
        dy_gan_wx = WUXING_MAP.get(dy_gan)
        dy_zhi_wx = ZHI_WUXING_MAP.get(dy_zhi)

        dy_gan_rel = _get_wuxing_relation(day_wx, dy_gan_wx) if dy_gan_wx else ''
        dy_zhi_rel = _get_wuxing_relation(day_wx, dy_zhi_wx) if dy_zhi_wx else ''

        dy_gan_shen = ten_god_names.get(dy_gan_rel, '')
        dy_zhi_shen = ten_god_names.get(dy_zhi_rel, '')

        score = 50
        if dy_gan_wx in favorable:
            score += 15
        elif dy_gan_wx in unfavorable:
            score -= 15
        if dy_zhi_wx in favorable:
            score += 20
        elif dy_zhi_wx in unfavorable:
            score -= 20
        score = max(25, min(90, score))

        trend_desc = ''
        if score >= 75:
            trend_desc = '大吉之运'
        elif score >= 60:
            trend_desc = '吉运'
        elif score >= 40:
            trend_desc = '平运'
        elif score >= 25:
            trend_desc = '凶运'

        key_points = []
        if dy_gan_shen == '财星':
            key_points.append('财运亨通')
        elif dy_gan_shen == '官杀':
            key_points.append('事业上升')
        elif dy_gan_shen == '印星':
            key_points.append('学业贵人')
        elif dy_gan_shen == '食伤':
            key_points.append('才华展现')
        elif dy_gan_shen == '比肩':
            key_points.append('同辈相助')

        if dy_zhi_shen == '财星' and dy_gan_shen != '财星':
            key_points.append('财源广进')
        elif dy_zhi_shen == '官杀' and dy_gan_shen != '官杀':
            key_points.append('职务变动')

        if dy_gan_rel == '克我' and dy_zhi_rel == '克我':
            key_points.append('压力较大')
        elif dy_gan_rel == '生我' and dy_zhi_rel == '生我':
            key_points.append('贵人相助')

        avg_score = None
        if chart_points:
            dy_points = [p for p in chart_points if start_age <= p['age'] < start_age + 10]
            if dy_points:
                avg_score = sum(p['score'] for p in dy_points) // len(dy_points)

        dayun_analysis.append({
            'start_age': start_age,
            'end_age': start_age + 9,
            'ganzhi': ganzhi,
            'gan': dy_gan,
            'zhi': dy_zhi,
            'gan_wx': dy_gan_wx or '',
            'zhi_wx': dy_zhi_wx or '',
            'gan_shen': dy_gan_shen,
            'zhi_shen': dy_zhi_shen,
            'score': score,
            'trend_desc': trend_desc,
            'key_points': key_points[:3],
            'avg_score': avg_score,
        })

    return dayun_analysis


def _build_fallback_analysis(bazi_data: dict, chart_points: list) -> dict:
    """基于八字和K线数据生成兜底文字分析（AI不可用时使用）"""
    pillars = bazi_data['pillars']
    day_gan = pillars['day']['gan']
    day_wx = WUXING_MAP.get(day_gan, '木')
    wuxing_count = bazi_data['wuxing']['count']

    # 身强身弱
    sheng_wo = next((k for k, v in _SHENG.items() if v == day_wx), '')
    wo_sheng = _SHENG.get(day_wx, '')
    ke_wo = next((k for k, v in _KE.items() if v == day_wx), '')
    wo_ke = _KE.get(day_wx, '')
    support = wuxing_count.get(day_wx, 0) + wuxing_count.get(sheng_wo, 0)
    consume = wuxing_count.get(wo_sheng, 0) + wuxing_count.get(wo_ke, 0) + wuxing_count.get(ke_wo, 0)
    is_strong = support >= consume

    wx_desc = {'木': '仁慈向上', '火': '热情礼仪', '土': '诚信稳重', '金': '刚毅果断', '水': '智慧灵活'}
    personality = f"日主{day_gan}（{day_wx}），天性{wx_desc.get(day_wx, '')}，{'身强主见强' if is_strong else '身弱需扶助'}"

    # 从K线数据提取巅峰/低谷年
    if chart_points:
        peak = max(chart_points, key=lambda x: x['high'])
        low = min(chart_points, key=lambda x: x['low'])
        avg_score = sum(p['score'] for p in chart_points) // len(chart_points)
        peak_age = peak['age']
        low_age = low['age']
    else:
        peak = low = None
        avg_score = 60
        peak_age = low_age = 0

    summary = f"日主{day_gan}{day_wx}，{'身强喜克泄' if is_strong else '身弱喜生扶'}，一生运势起伏见K线"
    industry = f"事业高峰在{peak_age}岁前后" if peak_age else "顺势而为"
    wealth = f"财运见K线高点，{peak_age}岁左右有突破" if peak_age else "财运平稳"
    marriage = "婚姻看大运流年走势，详见K线" if not peak_age else f"感情宜在运势上升期（近{peak_age}岁）推进"
    health = f"注意{low_age}岁前后健康" if low_age else "注意低分年份身体"
    family = "六亲缘分看年月柱，详见命盘"

    return {
        "summary": summary,
        "summaryScore": avg_score,
        "personality": personality,
        "personalityScore": min(100, avg_score + 5),
        "industry": industry,
        "industryScore": peak['score'] if peak else avg_score,
        "wealth": wealth,
        "wealthScore": min(100, (peak['score'] if peak else avg_score) - 5),
        "marriage": marriage,
        "marriageScore": avg_score,
        "health": health,
        "healthScore": low['score'] + 20 if low else avg_score,
        "family": family,
        "familyScore": avg_score,
    }


@router.post("/kline/start")
def bazi_kline_start(
    req: BaziReadingRequest,
    current_user: User = Depends(get_current_user),
):
    """启动人生K线图生成（异步任务）。
    策略：后端本地算法生成K线数据（OHLC），AI只生成7维度文字分析，避免输出被截断。
    """
    task_id = str(uuid.uuid4())
    create_task(task_id)

    ai_provider_name = current_user.ai_provider or "mock"
    ai_api_key = current_user.ai_api_key
    ai_model = current_user.ai_model
    ai_base_url = current_user.ai_base_url

    date_str = req.date_str
    hour_index = req.hour_index
    gender = req.gender
    is_lunar = req.is_lunar
    is_leap = req.is_leap

    def _generate():
        try:
            bazi_data = calculate_bazi(
                date_str=date_str,
                hour_index=hour_index,
                gender=gender,
                is_lunar=is_lunar,
                is_leap=is_leap,
            )

            # 1. 后端本地生成K线数据（60年）—— 立即可用
            chart_points = _generate_local_kline(bazi_data, total_years=60)

            # 2. 生成详细大运解读数据
            dayun_analysis = []
            try:
                dayun_analysis = _generate_dayun_analysis(bazi_data, chart_points)
                import logging
                logging.getLogger("uvicorn.error").info(f"Dayun analysis generated: {len(dayun_analysis)} items")
            except Exception as dy_err:
                import logging
                logging.getLogger("uvicorn.error").error(f"Dayun analysis error: {dy_err}")

            # 3. 先用兜底文案组装结果并立即更新任务（让前端尽快拿到K线图）
            pillars = bazi_data['pillars']
            fallback_analysis = _build_fallback_analysis(bazi_data, chart_points)
            kline_data = {
                "bazi": [
                    pillars['year']['ganzhi'],
                    pillars['month']['ganzhi'],
                    pillars['day']['ganzhi'],
                    pillars['hour']['ganzhi'],
                ],
                **fallback_analysis,
                "chartPoints": chart_points,
                "dayunAnalysis": dayun_analysis,
            }
            update_task(task_id, {"kline_data": kline_data, "bazi": bazi_data})

            # 3. 异步调用AI生成更丰富的文字分析（失败不覆盖已有数据）
            try:
                prompt = _build_kline_analysis_prompt(bazi_data)
                system_prompt = "你是一位八字命理大师，有20年以上实战经验。请严格按照JSON格式输出，不要有任何多余文字。"
                ai_provider = get_ai_provider(ai_provider_name, api_key=ai_api_key, model=ai_model, base_url=ai_base_url)
                result_text = ai_provider.chat(system_prompt, prompt)
                ai_analysis = _parse_json_loose(result_text)
                if ai_analysis and 'summary' in ai_analysis:
                    # AI分析成功，补充到已有结果中
                    kline_data.update(ai_analysis)
                    update_task(task_id, {"kline_data": kline_data, "bazi": bazi_data})
            except Exception as ai_err:
                # AI失败不影响已返回的K线数据，记录错误即可
                import logging
                logging.getLogger("uvicorn.error").warning(f"K线AI分析失败(task={task_id}): {ai_err}")
        except Exception as e:
            fail_task(task_id, str(e))

    thread = threading.Thread(target=_generate)
    thread.daemon = True
    thread.start()

    return {"task_id": task_id, "status": "processing"}


@router.get("/kline/status/{task_id}")
def bazi_kline_status(task_id: str):
    """查询人生K线图生成状态"""
    return get_task(task_id)


@router.post("/reading/start")
def bazi_reading_start(
    req: BaziReadingRequest,
    current_user: User = Depends(get_current_user),
):
    task_id = str(uuid.uuid4())
    create_task(task_id)

    # 在线程启动前提取所有需要的参数，避免线程中使用 SQLAlchemy 对象
    ai_provider_name = current_user.ai_provider or "mock"
    ai_api_key = current_user.ai_api_key
    ai_model = current_user.ai_model
    ai_base_url = current_user.ai_base_url

    date_str = req.date_str
    hour_index = req.hour_index
    gender = req.gender
    is_lunar = req.is_lunar
    is_leap = req.is_leap
    question = req.question

    def _generate():
        try:
            bazi_data = calculate_bazi(
                date_str=date_str,
                hour_index=hour_index,
                gender=gender,
                is_lunar=is_lunar,
                is_leap=is_leap,
            )
            prompt = _build_bazi_prompt(bazi_data, question)
            system_prompt = "你是一位资深的八字命理师，有20年以上实战经验，擅长用通俗易懂的语言解读命盘。解读要有温度、有主见，客观真实，像朋友聊天一样，不要用教科书式的表述。"
            ai_provider = get_ai_provider(ai_provider_name, api_key=ai_api_key, model=ai_model, base_url=ai_base_url)
            reading_text = ai_provider.chat(system_prompt, prompt)
            update_task(task_id, {"bazi": bazi_data, "reading": reading_text})
        except Exception as e:
            fail_task(task_id, str(e))

    thread = threading.Thread(target=_generate)
    thread.daemon = True
    thread.start()

    return {"task_id": task_id, "status": "processing"}


@router.get("/reading/status/{task_id}")
def bazi_reading_status(task_id: str):
    return get_task(task_id)


@router.post("/reading")
def bazi_reading(
    req: BaziReadingRequest,
    current_user: User = Depends(get_current_user),
):
    bazi_data = calculate_bazi(
        date_str=req.date_str,
        hour_index=req.hour_index,
        gender=req.gender,
        is_lunar=req.is_lunar,
        is_leap=req.is_leap,
    )

    prompt = _build_bazi_prompt(bazi_data, req.question)
    ai_provider = get_ai_provider(current_user)
    system_prompt = "你是一位资深的八字命理师，有20年以上实战经验，擅长用通俗易懂的语言解读命盘。解读要有温度、有主见，客观真实，像朋友聊天一样，不要用教科书式的表述。"
    reading_text = ai_provider.chat(system_prompt, prompt)

    return {
        "bazi": bazi_data,
        "reading": reading_text,
    }
