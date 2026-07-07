from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, datetime, timedelta
import json

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.models import User, Chart, DailyFortune, Checkin, UserLog
from app.services.fortune_service import calculate_daily_fortune

router = APIRouter(prefix="/fortune", tags=["每日运势"])


@router.get("/today")
def get_today_fortune(
    chart_id: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取今日运势"""
    today = date.today()
    
    # 获取用户默认命盘或指定命盘
    if chart_id:
        chart = db.query(Chart).filter(
            Chart.id == chart_id,
            Chart.user_id == current_user.id
        ).first()
    else:
        chart = db.query(Chart).filter(
            Chart.user_id == current_user.id,
            Chart.is_default == True
        ).first()
    
    if not chart:
        chart = db.query(Chart).filter(
            Chart.user_id == current_user.id
        ).first()
    
    if not chart:
        raise HTTPException(status_code=400, detail="请先生成星盘")
    
    # 查询今日运势缓存
    fortune = db.query(DailyFortune).filter(
        DailyFortune.user_id == current_user.id,
        DailyFortune.chart_id == chart.id,
        DailyFortune.fortune_date == today
    ).first()
    
    # 如果没有缓存，计算生成
    if not fortune:
        fortune_data = calculate_daily_fortune(chart, today)
        
        fortune = DailyFortune(
            user_id=current_user.id,
            chart_id=chart.id,
            fortune_date=today,
            overall_score=fortune_data['overall_score'],
            love_score=fortune_data['love_score'],
            career_score=fortune_data['career_score'],
            wealth_score=fortune_data['wealth_score'],
            health_score=fortune_data['health_score'],
            lucky_color=fortune_data['lucky_color'],
            lucky_number=fortune_data['lucky_number'],
            lucky_direction=fortune_data['lucky_direction'],
            do_list=fortune_data['do_list'],
            avoid_list=fortune_data['avoid_list'],
            phrase=fortune_data['phrase']
        )
        db.add(fortune)
        db.commit()
        db.refresh(fortune)
    else:
        # 从缓存获取时也需要获取干支信息
        fortune_data = calculate_daily_fortune(chart, today)
    
    # 记录查看日志
    log = UserLog(user_id=current_user.id, action="fortune_view", detail={"chart_id": chart.id})
    db.add(log)
    
    # 更新用户活跃时间
    current_user.last_active_at = datetime.utcnow()
    db.commit()
    
    return {
        "date": str(today),
        "year_ganzhi": fortune_data.get('year_ganzhi', ''),
        "month_ganzhi": fortune_data.get('month_ganzhi', ''),
        "day_ganzhi": fortune_data.get('day_ganzhi', ''),
        "overall_score": fortune.overall_score,
        "love_score": fortune.love_score,
        "career_score": fortune.career_score,
        "wealth_score": fortune.wealth_score,
        "health_score": fortune.health_score,
        "lucky_color": fortune.lucky_color,
        "lucky_number": fortune.lucky_number,
        "lucky_direction": fortune.lucky_direction,
        "do_list": json.loads(fortune.do_list) if fortune.do_list else [],
        "avoid_list": json.loads(fortune.avoid_list) if fortune.avoid_list else [],
        "phrase": fortune.phrase,
        "chart_name": chart.name,
        "chart_remark": chart.remark
    }


@router.post("/checkin")
def do_checkin(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """签到打卡"""
    today = date.today()
    
    # 检查是否已签到
    existing = db.query(Checkin).filter(
        Checkin.user_id == current_user.id,
        Checkin.checkin_date == today
    ).first()
    
    if existing:
        return {
            "success": False,
            "message": "今日已签到",
            "checkin_days": current_user.checkin_days,
            "checkin_total": current_user.checkin_total
        }
    
    # 计算连续签到天数
    yesterday = today - timedelta(days=1)
    if current_user.last_checkin_date == yesterday:
        current_user.checkin_days += 1
    else:
        current_user.checkin_days = 1
    
    current_user.checkin_total += 1
    current_user.last_checkin_date = today
    
    # 创建签到记录
    checkin = Checkin(user_id=current_user.id, checkin_date=today)
    db.add(checkin)
    
    # 记录日志
    log = UserLog(user_id=current_user.id, action="checkin", detail={"days": current_user.checkin_days})
    db.add(log)
    
    db.commit()
    
    return {
        "success": True,
        "message": "签到成功",
        "checkin_days": current_user.checkin_days,
        "checkin_total": current_user.checkin_total,
        "reward": get_checkin_reward(current_user.checkin_days)
    }


def get_checkin_reward(days: int) -> dict:
    """获取签到奖励"""
    rewards = {
        7: {"title": "一周坚持", "bonus": "运势解读小贴士"},
        30: {"title": "月度达人", "bonus": "专属运势报告"},
        100: {"title": "百日成就", "bonus": "VIP体验券"}
    }
    if days in rewards:
        return rewards[days]
    return {"title": f"连续{days}天", "bonus": "感谢坚持"}


@router.get("/checkin/status")
def get_checkin_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取签到状态"""
    today = date.today()
    
    # 检查今日是否已签到
    has_checkin = db.query(Checkin).filter(
        Checkin.user_id == current_user.id,
        Checkin.checkin_date == today
    ).first() is not None
    
    # 获取最近30天签到记录
    recent_checkins = db.query(Checkin).filter(
        Checkin.user_id == current_user.id,
        Checkin.checkin_date >= today - timedelta(days=30)
    ).all()
    
    checkin_dates = [str(c.checkin_date) for c in recent_checkins]
    
    return {
        "has_checkin_today": has_checkin,
        "checkin_days": current_user.checkin_days,
        "checkin_total": current_user.checkin_total,
        "recent_dates": checkin_dates
    }


@router.get("/history")
def get_fortune_history(
    days: int = 7,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取历史运势"""
    today = date.today()
    start_date = today - timedelta(days=days)
    
    fortunes = db.query(DailyFortune).filter(
        DailyFortune.user_id == current_user.id,
        DailyFortune.fortune_date >= start_date
    ).order_by(DailyFortune.fortune_date.desc()).all()
    
    return [{
        "date": str(f.fortune_date),
        "overall_score": f.overall_score,
        "phrase": f.phrase
    } for f in fortunes]