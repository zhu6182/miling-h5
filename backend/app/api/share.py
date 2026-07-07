from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
import io
from PIL import Image, ImageDraw, ImageFont
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.models import User, Chart
from app.models.match_models import MatchRecord
from app.services.match_service import get_match_summary_text

router = APIRouter(prefix="/share", tags=["分享"])


class ShareReadingRequest(BaseModel):
    chart_id: int


class ShareMatchRequest(BaseModel):
    match_id: int


def _strip_html(text: str) -> str:
    import re
    clean = re.compile(r'<[^>]+>')
    return clean.sub('', text)


def _generate_simple_reading(chart: Chart) -> dict:
    chart_data = chart.chart_data or {}
    palaces = chart_data.get('palaces', [])

    soul_palace_data = None
    career_palace_data = None
    wealth_palace_data = None
    love_palace_data = None

    for p in palaces:
        if '命宫' in p.get('tags', []):
            soul_palace_data = p
        if p.get('name') == '官禄宫':
            career_palace_data = p
        if p.get('name') == '财帛宫':
            wealth_palace_data = p
        if p.get('name') == '夫妻宫':
            love_palace_data = p

    soul_stars = '·'.join(soul_palace_data.get('major_stars', [])) if soul_palace_data and soul_palace_data.get('major_stars') else '空宫'
    career_stars = '·'.join(career_palace_data.get('major_stars', [])) if career_palace_data and career_palace_data.get('major_stars') else '空宫'
    wealth_stars = '·'.join(wealth_palace_data.get('major_stars', [])) if wealth_palace_data and wealth_palace_data.get('major_stars') else '空宫'
    love_stars = '·'.join(love_palace_data.get('major_stars', [])) if love_palace_data and love_palace_data.get('major_stars') else '空宫'

    personality_content = f"你的命宫主星是{soul_stars}，自带独特的气场与天赋。在人群中往往有自己的辨识度，遇事有主见，不容易随波逐流。"
    career_content = f"事业宫主星为{career_stars}，工作中有自己的节奏和风格。找准方向后能稳步前行，适合发挥自己的特长。"
    love_content = f"夫妻宫主星为{love_stars}，感情里有自己的期待和坚持。遇到对的人，会认真投入地经营这段关系。"
    wealth_content = f"财帛宫主星为{wealth_stars}，财运有自己的节奏。赚钱能力不错，注意合理规划收支，积少成多。"

    summary = f"{soul_stars}坐命，{chart.five_elements or '五行局'}，天赋独特，未来可期。"

    return {
        "personality_content": personality_content,
        "career_content": career_content,
        "love_content": love_content,
        "wealth_content": wealth_content,
        "summary": summary
    }


@router.post("/reading")
def get_reading_share(
    req: ShareReadingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    chart = db.query(Chart).filter(
        Chart.id == req.chart_id,
        Chart.user_id == current_user.id
    ).first()

    if not chart:
        raise HTTPException(status_code=404, detail="命盘不存在")

    title_name = chart.remark or "我"
    title = f"{title_name} 的命盘解读"

    soul_palace = chart.soul_palace or "未知"
    five_elements = chart.five_elements or "未知"

    sections = []
    summary = ""

    if chart.reading_data and chart.reading_data.get('cards'):
        cards = chart.reading_data['cards']
        title_map = {
            "命盘底色 · 先天禀赋": "性格特点",
            "事业格局": "事业运势",
            "感情模式": "姻缘走势",
            "财运模式": "财运分析"
        }
        expected_titles = ["命盘底色 · 先天禀赋", "事业格局", "感情模式", "财运模式"]
        section_titles = ["性格特点", "事业运势", "姻缘走势", "财运分析"]

        for i, expected in enumerate(expected_titles):
            card = next((c for c in cards if c.get('title') == expected), None)
            if card:
                content = _strip_html(card.get('body', ''))
                sections.append({
                    "title": section_titles[i],
                    "content": content
                })
            else:
                simple = _generate_simple_reading(chart)
                key_map = {
                    0: "personality_content",
                    1: "career_content",
                    2: "love_content",
                    3: "wealth_content"
                }
                sections.append({
                    "title": section_titles[i],
                    "content": simple[key_map[i]]
                })

        if sections:
            first_content = sections[0].get('content', '')
            if len(first_content) > 50:
                summary = first_content[:50] + "..."
            else:
                summary = first_content
    else:
        simple = _generate_simple_reading(chart)
        sections = [
            {"title": "性格特点", "content": simple["personality_content"]},
            {"title": "事业运势", "content": simple["career_content"]},
            {"title": "姻缘走势", "content": simple["love_content"]},
            {"title": "财运分析", "content": simple["wealth_content"]}
        ]
        summary = simple["summary"]

    return {
        "title": title,
        "subtitle": "命里 · 紫微斗数",
        "sections": sections,
        "summary": summary,
        "soul_palace": soul_palace,
        "five_elements": five_elements
    }


@router.post("/match")
def get_match_share(
    req: ShareMatchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    record = db.query(MatchRecord).filter(
        MatchRecord.id == req.match_id,
        (MatchRecord.user_a_id == current_user.id) | (MatchRecord.user_b_id == current_user.id)
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="配对不存在")

    if not record.match_data:
        raise HTTPException(status_code=400, detail="匹配结果未生成")

    is_user_a = record.user_a_id == current_user.id
    other_nickname = record.user_b_nickname if is_user_a else record.user_a_nickname
    title = f"我和 {other_nickname} 的缘分指数"

    match_data = record.match_data
    overall_score = match_data.get('overall_score', 0)
    dims = match_data.get('dimensions', {})

    dim_map = {
        'love': {'title': '姻缘匹配', 'fallback': '缘分天定，珍惜彼此'},
        'career': {'title': '事业合拍', 'fallback': '各有所长，互补共赢'},
        'friendship': {'title': '性格互补', 'fallback': '相互理解，友谊长存'}
    }

    sections = []
    for key, info in dim_map.items():
        dim = dims.get(key, {})
        score = dim.get('score', 0)
        content = dim.get('summary') or dim.get('advice') or info['fallback']
        sections.append({
            "title": info['title'],
            "score": score,
            "content": content
        })

    if overall_score >= 85:
        summary = "天作之合，相互成就"
    elif overall_score >= 70:
        summary = "缘分深厚，携手同行"
    elif overall_score >= 55:
        summary = "各有特点，需要磨合"
    else:
        summary = "互补共存，共同成长"

    return {
        "title": title,
        "overall_score": overall_score,
        "sections": sections,
        "summary": summary
    }


def draw_share_image(match_record: MatchRecord) -> bytes:
    """生成匹配结果分享图"""
    match_data = match_record.match_data or {}
    overall_score = match_data.get('overall_score', 0)
    dims = match_data.get('dimensions', {})

    img = Image.new('RGB', (600, 800), '#0a0a1a')
    draw = ImageDraw.Draw(img)

    try:
        title_font = ImageFont.truetype('msyh.ttc', 36)
        name_font = ImageFont.truetype('msyh.ttc', 24)
        score_font = ImageFont.truetype('msyh.ttc', 64)
        desc_font = ImageFont.truetype('msyh.ttc', 18)
        small_font = ImageFont.truetype('msyh.ttc', 16)
    except:
        title_font = name_font = score_font = desc_font = small_font = None

    draw.text((300, 60), '命里', fill='#c9a050', font=title_font, anchor='mm')

    y = 140
    draw.text((300, y), f'{match_record.user_a_nickname or ""} ✦ {match_record.user_b_nickname or "?"}',
              fill='#e0e0f0', font=name_font, anchor='mm')

    y = 220
    draw.text((300, y), f'{overall_score}', fill='#c9a050', font=score_font, anchor='mm')
    draw.text((300, y + 80), '综合匹配指数', fill='#8888a0', font=desc_font, anchor='mm')

    colors = {'love': '#e06060', 'career': '#6090c8', 'friendship': '#50c878', 'mentor': '#c9a050'}
    icons = {'love': '💖', 'career': '💼', 'friendship': '🤝', 'mentor': '🌟'}
    names = {'love': '姻缘', 'career': '事业', 'friendship': '友谊', 'mentor': '贵人'}

    y = 350
    dim_labels = ['love', 'career', 'friendship', 'mentor']
    for i, key in enumerate(dim_labels):
        if key in dims:
            d = dims[key]
            score = d.get('score', 0)
            x = 80 + i * 130

            bar_y = y + 60
            bar_w = 100
            bar_h = 10
            draw.rectangle([x - bar_w//2, bar_y, x + bar_w//2, bar_y + bar_h], fill='#333355')
            fill_w = int(bar_w * score / 100)
            color = colors.get(key, '#c9a050')
            draw.rectangle([x - bar_w//2, bar_y, x - bar_w//2 + fill_w, bar_y + bar_h], fill=color)

            draw.text((x, y + 20), f'{score}', fill=color, font=name_font, anchor='mm')
            draw.text((x, y + 40), names.get(key, key), fill='#c0c0d8', font=small_font, anchor='mm')
            draw.text((x, y + 100), icons.get(key, '✦'), fill=color, font=name_font, anchor='mm')

    y = 540
    draw.text((300, y), '长按识别小程序查看详情', fill='#666680', font=small_font, anchor='mm')
    draw.text((300, y + 30), '命里 · 命理匹配平台', fill='#8888a0', font=small_font, anchor='mm')

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf.getvalue()


@router.get("/match/{match_id}/image")
def get_match_share_image(
    match_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """生成分享图片"""
    record = db.query(MatchRecord).filter(
        MatchRecord.id == match_id,
        (MatchRecord.user_a_id == current_user.id) | (MatchRecord.user_b_id == current_user.id)
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="配对不存在")

    if not record.match_data:
        raise HTTPException(status_code=400, detail="匹配结果未生成")

    image_bytes = draw_share_image(record)

    return StreamingResponse(
        io.BytesIO(image_bytes),
        media_type='image/png',
        headers={'Content-Disposition': f'attachment; filename=match_{match_id}.png'}
    )
