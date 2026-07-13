from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
import io
import qrcode
import json
from app.core.database import get_db, SessionLocal
from app.api.deps import get_current_user
from app.models.models import User, Chart
from app.models.match_models import MatchRecord, Friend
from app.services.match_service import (
    calculate_full_match, generate_qr_code,
    get_match_summary_text
)
from app.services.ai_service import get_ai_provider

router = APIRouter(prefix="/match", tags=["匹配"])


class DirectMatchRequest(BaseModel):
    chart_a_id: int
    chart_b_id: int
    match_type: str = "all"


class AIAnalysisRequest(BaseModel):
    dimension: str  # career / friendship / mentor


# === 固定路由必须放在通配路由前面 ===

@router.post("/direct")
def direct_match(
    req: DirectMatchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """通过两个 chart_id 直接匹配"""
    chart_a = db.query(Chart).filter(
        Chart.id == req.chart_a_id, Chart.user_id == current_user.id
    ).first()
    chart_b = db.query(Chart).filter(
        Chart.id == req.chart_b_id, Chart.user_id == current_user.id
    ).first()

    if not chart_a:
        raise HTTPException(status_code=404, detail="命盘 A 不存在")
    if not chart_b:
        raise HTTPException(status_code=404, detail="命盘 B 不存在")
    if not chart_a.chart_data:
        raise HTTPException(status_code=400, detail="命盘 A 数据不完整")
    if not chart_b.chart_data:
        raise HTTPException(status_code=400, detail="命盘 B 数据不完整")

    nickname_a = chart_a.remark or current_user.nickname
    nickname_b = chart_b.remark or current_user.nickname

    match_result = calculate_full_match(
        chart_a.chart_data, chart_b.chart_data, req.match_type,
        name_a=nickname_a, name_b=nickname_b
    )

    record = MatchRecord(
        user_a_id=current_user.id,
        user_a_nickname=nickname_a,
        user_b_id=current_user.id,
        user_b_nickname=nickname_b,
        match_type=req.match_type,
        status="accepted",
        match_data=match_result,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "match_id": record.id,
        "status": "accepted",
        "summary": get_match_summary_text(match_result),
        "result": match_result,
    }


@router.post("/create-qr")
def create_match_qr(
    match_type: str = "all",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """生成匹配二维码"""
    user_chart = db.query(Chart).filter(
        Chart.user_id == current_user.id, Chart.is_default == True
    ).first()
    if not user_chart:
        user_chart = db.query(Chart).filter(
            Chart.user_id == current_user.id
        ).first()
    if not user_chart:
        raise HTTPException(status_code=400, detail="请先创建命盘")

    qr_code = generate_qr_code()
    record = MatchRecord(
        user_a_id=current_user.id,
        user_a_nickname=current_user.nickname,
        match_type=match_type,
        status="pending",
        qr_code=qr_code,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "qr_code": qr_code,
        "match_id": record.id,
        "match_type": match_type,
        "user_nickname": current_user.nickname,
    }


@router.post("/scan/{qr_code}")
def scan_match_qr(
    qr_code: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """扫码配对"""
    record = db.query(MatchRecord).filter(MatchRecord.qr_code == qr_code).first()
    if not record:
        raise HTTPException(status_code=404, detail="无效的配对码")
    if record.user_a_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能和自己配对")
    if record.status != "pending":
        raise HTTPException(status_code=400, detail="该配对已失效或已完成")

    chart_a = db.query(Chart).filter(
        Chart.user_id == record.user_a_id, Chart.is_default == True
    ).first()
    if not chart_a:
        chart_a = db.query(Chart).filter(
            Chart.user_id == record.user_a_id
        ).first()
    chart_b = db.query(Chart).filter(
        Chart.user_id == current_user.id, Chart.is_default == True
    ).first()
    if not chart_b:
        chart_b = db.query(Chart).filter(
            Chart.user_id == current_user.id
        ).first()
    if not chart_a or not chart_b:
        raise HTTPException(status_code=400, detail="双方都需要有命盘才能配对")

    nickname_a = record.user_a_nickname
    nickname_b = current_user.nickname

    match_result = calculate_full_match(
        chart_a.chart_data, chart_b.chart_data, record.match_type,
        name_a=nickname_a, name_b=nickname_b
    )

    record.user_b_id = current_user.id
    record.user_b_nickname = nickname_b
    record.status = "accepted"
    record.match_data = match_result
    db.commit()
    db.refresh(record)

    return {
        "match_id": record.id,
        "status": "accepted",
        "summary": get_match_summary_text(match_result),
        "result": match_result,
        "user_a": {"nickname": record.user_a_nickname, "soul_palace": match_result.get("soul_palace_a")},
        "user_b": {"nickname": record.user_b_nickname, "soul_palace": match_result.get("soul_palace_b")},
    }


@router.get("/history")
def get_match_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """匹配历史列表（只显示已配对的）"""
    records = db.query(MatchRecord).filter(
        (MatchRecord.user_a_id == current_user.id) | (MatchRecord.user_b_id == current_user.id),
        MatchRecord.status == "accepted"
    ).order_by(MatchRecord.created_at.desc()).limit(20).all()

    return [
        {
            "id": r.id,
            "user_a_nickname": r.user_a_nickname,
            "user_b_nickname": r.user_b_nickname,
            "match_type": r.match_type,
            "status": r.status,
            "overall_score": r.match_data.get("overall_score") if r.match_data else None,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in records
    ]


@router.get("/friends/list")
def get_friends(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """好友列表"""
    friends = db.query(Friend).filter(
        Friend.user_id == current_user.id, Friend.status == "active"
    ).all()

    result = []
    for f in friends:
        user = db.query(User).filter(User.id == f.friend_id).first()
        if user:
            default_chart = db.query(Chart).filter(
                Chart.user_id == user.id, Chart.is_default == True
            ).first()
            result.append({
                "user_id": user.id,
                "nickname": user.nickname,
                "soul_palace": default_chart.soul_palace if default_chart else None,
                "five_elements": default_chart.five_elements if default_chart else None,
            })
    return result


@router.get("/{match_id}")
def get_match_result(
    match_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取匹配结果"""
    record = db.query(MatchRecord).filter(
        MatchRecord.id == match_id,
        (MatchRecord.user_a_id == current_user.id) | (MatchRecord.user_b_id == current_user.id)
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="配对不存在")

    # 如果结果锁定，不返回详细数据
    if not record.result_unlocked:
        return {
            "id": record.id,
            "user_a_id": record.user_a_id,
            "user_a_nickname": record.user_a_nickname,
            "user_b_id": record.user_b_id,
            "user_b_nickname": record.user_b_nickname,
            "match_type": record.match_type,
            "status": record.status,
            "qr_code": record.qr_code,
            "locked": True,
            "message": "请看完广告解锁完整匹配结果",
            "created_at": record.created_at.isoformat() if record.created_at else None,
        }

    return {
        "id": record.id,
        "user_a_id": record.user_a_id,
        "user_a_nickname": record.user_a_nickname,
        "user_b_id": record.user_b_id,
        "user_b_nickname": record.user_b_nickname,
        "match_type": record.match_type,
        "status": record.status,
        "qr_code": record.qr_code,
        "match_data": record.match_data,
        "locked": False,
        "created_at": record.created_at.isoformat() if record.created_at else None,
    }


@router.post("/{match_id}/unlock")
def unlock_match_result(
    match_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """解锁匹配结果（看完广告后调用）"""
    record = db.query(MatchRecord).filter(
        MatchRecord.id == match_id,
        (MatchRecord.user_a_id == current_user.id) | (MatchRecord.user_b_id == current_user.id)
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="配对不存在")

    record.result_unlocked = True
    db.commit()

    return {
        "id": record.id,
        "match_data": record.match_data,
        "locked": False,
    }


DIMENSION_LABELS = {
    "love": "姻缘配对",
    "career": "事业合作",
    "friendship": "友谊缘分",
    "mentor": "贵人运",
}

DIMENSION_PROMPTS = {
    "love": """请对以下两人的姻缘配对进行深度分析，包括：
1. 双方各自的感情特质和爱情观
2. 相处的默契点和潜在摩擦
3. 感情发展的趋势和关键节点
4. 维系感情的要点和方法
5. 给出具体的相处建议""",
    "career": """请对以下两人的事业合作潜力进行深度分析，包括：
1. 双方各自的事业特质和行事风格
2. 合作中的互补点和潜在冲突
3. 适合的合作模式和分工建议
4. 需要注意的风险和规避方法
5. 给出具体的合作建议""",
    "friendship": """请对以下两人的友谊缘分进行深度分析，包括：
1. 双方性格特点和相处模式
2. 友谊中的默契点和差异
3. 深层精神共鸣的可能性
4. 友谊长久的关键因素
5. 给出具体的相处建议""",
    "mentor": """请对以下两人的贵人缘分进行深度分析，包括：
1. 双方各自的命格特点
2. 谁更可能是谁的贵人，在什么方面
3. 贵人运的强弱和表现形式
4. 如何主动经营这段缘分
5. 给出具体的建议""",
}


@router.post("/{match_id}/ai-analysis")
def ai_analysis(
    match_id: int,
    req: AIAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """AI详解某个维度的配对分析"""
    dimension = req.dimension
    if dimension not in DIMENSION_LABELS:
        raise HTTPException(status_code=400, detail="无效的分析维度")

    record = db.query(MatchRecord).filter(
        MatchRecord.id == match_id,
        (MatchRecord.user_a_id == current_user.id) | (MatchRecord.user_b_id == current_user.id)
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="配对不存在")
    if not record.match_data:
        raise HTTPException(status_code=400, detail="配对数据不完整")

    # 检查是否已有缓存的AI分析
    cache_key = f"ai_{dimension}"
    if record.match_data.get(cache_key):
        return {
            "dimension": dimension,
            "label": DIMENSION_LABELS[dimension],
            "analysis": record.match_data[cache_key],
        }

    # 获取双方命盘数据
    chart_a = db.query(Chart).filter(
        Chart.user_id == record.user_a_id, Chart.is_default == True
    ).first()
    if not chart_a:
        chart_a = db.query(Chart).filter(Chart.user_id == record.user_a_id).first()
    chart_b = db.query(Chart).filter(
        Chart.user_id == record.user_b_id, Chart.is_default == True
    ).first()
    if not chart_b:
        chart_b = db.query(Chart).filter(Chart.user_id == record.user_b_id).first()
    if not chart_a or not chart_b:
        raise HTTPException(status_code=400, detail="命盘数据不完整")

    name_a = record.user_a_nickname or "A"
    name_b = record.user_b_nickname or "B"
    dim_data = record.match_data.get("dimensions", {}).get(dimension, {})

    # 构建AI提示
    system_prompt = "你是一位资深的紫微斗数命理咨询师，擅长用通俗温暖的语言分析人际关系。分析要有深度、有温度、有实用建议，用朋友聊天的语气。使用HTML格式输出，支持<strong>白色强调</strong>、<em>金色强调</em>、<span class='warn'>橙色提醒</span>、<span class='good'>绿色利好</span>、<br>换行。"

    user_prompt = f"""请对【{name_a}】和【{name_b}】的{DIMENSION_LABELS[dimension]}进行深度分析。

{name_a}的命盘数据：
{json.dumps(chart_a.chart_data, ensure_ascii=False)[:2000]}

{name_b}的命盘数据：
{json.dumps(chart_b.chart_data, ensure_ascii=False)[:2000]}

基础配对结果：
{json.dumps(dim_data, ensure_ascii=False)}

{DIMENSION_PROMPTS[dimension]}

请用800-1200字进行分析，直接输出HTML内容，不要加代码块标记。"""

    # 调用AI（使用系统默认的火山方舟AI，不依赖用户的ai_provider配置）
    try:
        ai = get_ai_provider()
        result = ai.chat(system_prompt, user_prompt)

        # 缓存到match_data
        if not record.match_data:
            record.match_data = {}
        record.match_data[cache_key] = result
        db.commit()

        return {
            "dimension": dimension,
            "label": DIMENSION_LABELS[dimension],
            "analysis": result,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI分析失败: {str(e)}")


@router.post("/nfc/{target_user_id}")
def nfc_match(
    target_user_id: int,
    match_type: str = "all",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """NFC 碰一碰匹配"""
    if target_user_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能和自己匹配")

    target_user = db.query(User).filter(User.id == target_user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="目标用户不存在")

    chart_a = db.query(Chart).filter(
        Chart.user_id == current_user.id, Chart.is_default == True
    ).first()
    chart_b = db.query(Chart).filter(
        Chart.user_id == target_user_id, Chart.is_default == True
    ).first()
    if not chart_a or not chart_b:
        raise HTTPException(status_code=400, detail="双方都需要有命盘才能配对")

    nickname_a = current_user.nickname
    nickname_b = target_user.nickname

    match_result = calculate_full_match(
        chart_a.chart_data, chart_b.chart_data, match_type,
        name_a=nickname_a, name_b=nickname_b
    )

    record = MatchRecord(
        user_a_id=current_user.id,
        user_a_nickname=nickname_a,
        user_b_id=target_user_id,
        user_b_nickname=nickname_b,
        match_type=match_type,
        status="accepted",
        match_data=match_result,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "match_id": record.id,
        "status": "accepted",
        "summary": get_match_summary_text(match_result),
        "result": match_result,
    }


@router.post("/add-friend/{user_id}")
def add_friend(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """添加好友"""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能添加自己为好友")

    existing = db.query(Friend).filter(
        Friend.user_id == current_user.id, Friend.friend_id == user_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="已经是好友了")

    friend = Friend(user_id=current_user.id, friend_id=user_id)
    db.add(friend)
    reverse = Friend(user_id=user_id, friend_id=current_user.id)
    db.add(reverse)
    db.commit()
    return {"message": "添加成功"}


@router.delete("/friends/{friend_id}")
def remove_friend(
    friend_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除好友"""
    db.query(Friend).filter(
        Friend.user_id == current_user.id, Friend.friend_id == friend_id
    ).delete()
    db.query(Friend).filter(
        Friend.user_id == friend_id, Friend.friend_id == current_user.id
    ).delete()
    db.commit()
    return {"message": "删除成功"}


@router.get("/qr/{qr_code}/image")
def get_qr_image(
    qr_code: str,
    db: Session = Depends(get_db)
):
    """获取配对二维码图片"""
    record = db.query(MatchRecord).filter(MatchRecord.qr_code == qr_code).first()
    if not record:
        raise HTTPException(status_code=404, detail="配对码无效")

    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(qr_code)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#1a1a2e", back_color="white")

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")


@router.get("/qr/{qr_code}/share")
def get_qr_share_info(
    qr_code: str,
    db: Session = Depends(get_db)
):
    """获取分享信息"""
    record = db.query(MatchRecord).filter(MatchRecord.qr_code == qr_code).first()
    if not record:
        raise HTTPException(status_code=404, detail="配对码无效")

    return {
        "qr_code": qr_code,
        "user_nickname": record.user_a_nickname,
        "match_type": record.match_type,
        "status": record.status,
    }
