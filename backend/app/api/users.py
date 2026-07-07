from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.models import User, Chart
from app.schemas.schemas import UserUpdate, UserResponse, ChartResponse, ChartCalculateRequest
from app.services.user_service import update_user
from app.services.chart_service import calculate_chart

router = APIRouter(prefix="/users", tags=["用户"])


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserResponse)
def update_me(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = update_user(db, current_user.id, user_update)
    return user


@router.get("/me/charts", response_model=List[ChartResponse])
def get_my_charts(
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
    return charts


@router.post("/calculate-chart")
def calculate_new_chart(
    req: ChartCalculateRequest,
    current_user: User = Depends(get_current_user),
):
    try:
        if req.solar_date:
            chart_data = calculate_chart(
                date_str=req.solar_date,
                hour_index=req.hour_index,
                gender=req.gender,
                is_lunar=False
            )
        elif req.lunar_date:
            chart_data = calculate_chart(
                date_str=req.lunar_date,
                hour_index=req.hour_index,
                gender=req.gender,
                is_lunar=True,
                is_leap=req.is_leap
            )
        else:
            raise HTTPException(status_code=400, detail="请提供公历或农历日期")
        return chart_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"排盘失败: {str(e)}")


@router.post("/save-chart", response_model=ChartResponse)
def save_chart(
    req: ChartCalculateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        if req.solar_date:
            chart_data = calculate_chart(
                date_str=req.solar_date,
                hour_index=req.hour_index,
                gender=req.gender,
                is_lunar=False
            )
        elif req.lunar_date:
            chart_data = calculate_chart(
                date_str=req.lunar_date,
                hour_index=req.hour_index,
                gender=req.gender,
                is_lunar=True,
                is_leap=req.is_leap
            )
        else:
            raise HTTPException(status_code=400, detail="请提供公历或农历日期")

        if req.is_default or not db.query(Chart).filter(Chart.user_id == current_user.id, Chart.is_default == True).first():
            db.query(Chart).filter(Chart.user_id == current_user.id).update({Chart.is_default: False})
            is_default = True
        else:
            is_default = False

        chart = Chart(
            user_id=current_user.id,
            name=req.name or "我的命盘",
            solar_date=chart_data.get('solar_date'),
            lunar_date=chart_data.get('lunar_date'),
            gender=chart_data['gender'],
            hour_index=chart_data['hour_index'],
            hour_name=chart_data.get('hour_name', ''),
            five_elements=chart_data.get('five_elements', ''),
            soul_palace=chart_data.get('soul_palace_branch', ''),
            body_palace=chart_data.get('body_palace_branch', ''),
            chart_data=chart_data,
            is_default=is_default,
            remark=req.remark,
            chart_type=req.chart_type or 'ziwei',
        )
        db.add(chart)
        db.commit()
        db.refresh(chart)
        return chart
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存失败: {str(e)}")
