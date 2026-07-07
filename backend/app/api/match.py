from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
import io
import qrcode
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.models import User, Chart
from app.models.match_models import MatchRecord, Friend
from app.services.match_service import (
    calculate_full_match, generate_qr_code,
    get_match_summary_text
)

router = APIRouter(prefix="/match", tags=["匹配"])


class DirectMatchRequest(BaseModel):
    chart_a_id: int
    chart_b_id: int
    match_type: str = "all"


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

    match_result = calculate_full_match(
        chart_a.chart_data, chart_b.chart_data, req.match_type
    )

    nickname_a = chart_a.remark or current_user.nickname
    nickname_b = chart_b.remark or current_user.nickname

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
    user_charts = db.query(Chart).filter(
        Chart.user_id == current_user.id, Chart.is_default == True
    ).first()
    if not user_charts:
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
    chart_b = db.query(Chart).filter(
        Chart.user_id == current_user.id, Chart.is_default == True
    ).first()
    if not chart_a or not chart_b:
        raise HTTPException(status_code=400, detail="双方都需要有命盘才能配对")

    match_result = calculate_full_match(
        chart_a.chart_data, chart_b.chart_data, record.match_type
    )

    record.user_b_id = current_user.id
    record.user_b_nickname = current_user.nickname
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
        raise HTTPException(status_code=400, detail="双方都需要有命盘才能匹配")

    match_result = calculate_full_match(
        chart_a.chart_data, chart_b.chart_data, match_type
    )

    record = MatchRecord(
        user_a_id=current_user.id,
        user_a_nickname=current_user.nickname,
        user_b_id=target_user_id,
        user_b_nickname=target_user.nickname,
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
