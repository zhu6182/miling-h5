import uuid
import threading
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db, SessionLocal
from app.api.deps import get_current_user
from app.models.models import User, Chart
from app.schemas.schemas import ChartUpdate, ChartResponse, ReadingRequest
from app.services.ai_service import get_ai_provider
from app.services.task_manager import create_task, update_task, fail_task, get_task

router = APIRouter(prefix="/charts", tags=["命盘"])


def _extract_bazi_info(chart: Chart) -> dict:
    """从命盘中提取八字四柱信息用于展示"""
    result = {"bazi_pillars": None, "bazi_display": None}
    
    if chart.chart_data:
        cd = chart.chart_data
        
        # 八字命盘格式 (bazi)
        if cd.get('pillars'):
            p = cd['pillars']
            year_gz = p.get('year', {}).get('ganzhi', '')
            month_gz = p.get('month', {}).get('ganzhi', '')
            day_gz = p.get('day', {}).get('ganzhi', '')
            hour_gz = p.get('hour', {}).get('ganzhi', '')
            if all([year_gz, month_gz, day_gz, hour_gz]):
                result['bazi_pillars'] = f"{year_gz} {month_gz} {day_gz} {hour_gz}"
                result['bazi_display'] = f"{year_gz} · {month_gz} · {day_gz} · {hour_gz}"
        
        # 紫微斗数格式 (ziwei)
        elif cd.get('chinese_date'):
            chinese_date = cd['chinese_date']
            parts = chinese_date.split()
            if len(parts) >= 4:
                year_gz, month_gz, day_gz, hour_gz = parts[:4]
                result['bazi_pillars'] = f"{year_gz} {month_gz} {day_gz} {hour_gz}"
                result['bazi_display'] = f"{year_gz} · {month_gz} · {day_gz} · {hour_gz}"
    
    return result


@router.get("", response_model=List[ChartResponse])
def get_charts(
    type: Optional[str] = Query(None, description="过滤类型: my=我的命盘(remark为空), helped=已帮助过的命盘(remark不为空)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Chart).filter(Chart.user_id == current_user.id)
    if type == "my":
        query = query.filter((Chart.remark == None) | (Chart.remark == ""))
    elif type == "helped":
        query = query.filter(Chart.remark != None, Chart.remark != "")
    charts = query.order_by(Chart.created_at.desc()).all()
    
    result = []
    for chart in charts:
        response = ChartResponse.from_orm(chart)
        bazi_info = _extract_bazi_info(chart)
        response.bazi_pillars = bazi_info['bazi_pillars']
        response.bazi_display = bazi_info['bazi_display']
        result.append(response)
    
    return result


@router.get("/{chart_id}", response_model=ChartResponse)
def get_chart(
    chart_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    chart = db.query(Chart).filter(Chart.id == chart_id, Chart.user_id == current_user.id).first()
    if not chart:
        raise HTTPException(status_code=404, detail="命盘不存在")
    return chart


@router.put("/{chart_id}", response_model=ChartResponse)
def update_chart(
    chart_id: int,
    chart_update: ChartUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    chart = db.query(Chart).filter(Chart.id == chart_id, Chart.user_id == current_user.id).first()
    if not chart:
        raise HTTPException(status_code=404, detail="命盘不存在")
    update_data = chart_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(chart, key, value)
    db.commit()
    db.refresh(chart)
    return chart


@router.patch("/{chart_id}", response_model=ChartResponse)
def patch_chart(
    chart_id: int,
    chart_update: ChartUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    chart = db.query(Chart).filter(Chart.id == chart_id, Chart.user_id == current_user.id).first()
    if not chart:
        raise HTTPException(status_code=404, detail="命盘不存在")
    update_data = chart_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(chart, key, value)
    db.commit()
    db.refresh(chart)
    return chart


@router.delete("/{chart_id}")
def delete_chart(
    chart_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    chart = db.query(Chart).filter(Chart.id == chart_id, Chart.user_id == current_user.id).first()
    if not chart:
        raise HTTPException(status_code=404, detail="命盘不存在")
    db.delete(chart)
    db.commit()
    return {"message": "删除成功"}


@router.post("/{chart_id}/reading/start")
def generate_reading_start(
    chart_id: int,
    reading_request: ReadingRequest = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    chart = db.query(Chart).filter(Chart.id == chart_id, Chart.user_id == current_user.id).first()
    if not chart:
        raise HTTPException(status_code=404, detail="命盘不存在")
    if not chart.chart_data:
        raise HTTPException(status_code=400, detail="命盘数据不完整")

    # 检查是否需要解锁
    if not chart.reading_unlocked:
        if not reading_request or not reading_request.ad_watched:
            return {
                "locked": True,
                "message": "请看完广告解锁AI解读",
                "chart_id": chart_id
            }
        # 用户已看完广告，解锁
        chart.reading_unlocked = True
        db.commit()

    task_id = str(uuid.uuid4())
    create_task(task_id)

    # 在线程启动前提取所有需要的参数
    ai_provider_name = current_user.ai_provider or "mock"
    ai_api_key = current_user.ai_api_key
    ai_model = current_user.ai_model
    ai_base_url = current_user.ai_base_url
    chart_data = chart.chart_data  # 提取 chart_data，避免线程中使用 SQLAlchemy 对象

    def _generate():
        db_session = None
        try:
            ai = get_ai_provider(ai_provider_name, api_key=ai_api_key, model=ai_model, base_url=ai_base_url)
            reading = ai.generate_reading(chart_data)

            # 用独立 session 保存结果到数据库
            db_session = SessionLocal()
            chart_obj = db_session.query(Chart).filter(Chart.id == chart_id).first()
            if chart_obj:
                chart_obj.reading_data = reading
                db_session.commit()

            update_task(task_id, {"chart_id": chart_id, "reading": reading, "locked": False})
        except Exception as e:
            fail_task(task_id, str(e))
        finally:
            if db_session:
                db_session.close()

    thread = threading.Thread(target=_generate)
    thread.daemon = True
    thread.start()

    return {"task_id": task_id, "status": "processing"}


@router.get("/{chart_id}/reading/status")
def generate_reading_status(
    chart_id: int,
    task_id: str = Query(..., description="任务ID"),
    current_user: User = Depends(get_current_user),
):
    return get_task(task_id)


@router.post("/{chart_id}/reading")
def generate_reading(
    chart_id: int,
    reading_request: ReadingRequest = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    chart = db.query(Chart).filter(Chart.id == chart_id, Chart.user_id == current_user.id).first()
    if not chart:
        raise HTTPException(status_code=404, detail="命盘不存在")
    if not chart.chart_data:
        raise HTTPException(status_code=400, detail="命盘数据不完整")

    # 检查是否需要解锁
    if not chart.reading_unlocked:
        if not reading_request or not reading_request.ad_watched:
            return {
                "locked": True,
                "message": "请看完广告解锁AI解读",
                "chart_id": chart_id
            }
        # 用户已看完广告，解锁
        chart.reading_unlocked = True
        db.commit()

    provider = current_user.ai_provider or "mock"
    api_key = current_user.ai_api_key
    model = current_user.ai_model
    base_url = current_user.ai_base_url

    try:
        ai = get_ai_provider(provider, api_key=api_key, model=model, base_url=base_url)
        reading = ai.generate_reading(chart.chart_data)
        chart.reading_data = reading
        # 生成后重新锁定，下次需再看广告（可选：也可永久解锁）
        # chart.reading_unlocked = False
        db.commit()
        return {"chart_id": chart_id, "reading": reading, "locked": False}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 解读失败: {str(e)}")
