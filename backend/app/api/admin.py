from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta, date
import hashlib
import jwt
from typing import Optional

from app.core.database import get_db
from app.core.config import settings
from app.models.models import User, Chart, Checkin, UserLog, SystemConfig, DailyFortune
from pydantic import BaseModel

router = APIRouter(prefix="/admin", tags=["管理后台"])

# JWT密钥
SECRET_KEY = "mingli_admin_secret_key_2024"
ALGORITHM = "HS256"


class AdminLoginRequest(BaseModel):
    email: str
    password: str


class ConfigUpdateRequest(BaseModel):
    configs: dict


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed


def create_admin_token(user_id: int) -> str:
    payload = {
        "user_id": user_id,
        "is_admin": True,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


async def get_admin_user(authorization: str = Header(None), db: Session = Depends(get_db)) -> User:
    """验证管理员身份"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="缺少认证信息")
    
    token = authorization.replace("Bearer ", "")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="无效的token")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="token已过期")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="无效的token")
    
    user = db.query(User).filter(User.id == user_id, User.is_admin == True).first()
    if not user:
        raise HTTPException(status_code=401, detail="非管理员用户")
    return user


@router.post("/auth/login")
def admin_login(req: AdminLoginRequest, db: Session = Depends(get_db)):
    """管理员登录"""
    # 查找管理员用户
    admin = db.query(User).filter(
        User.is_admin == True,
        or_(User.email == req.email, User.phone == req.email)
    ).first()
    
    if not admin:
        raise HTTPException(status_code=401, detail="管理员账号不存在")
    
    # 验证密码
    if not admin.password_hash:
        raise HTTPException(status_code=401, detail="管理员账号未设置密码")
    
    if not verify_password(req.password, admin.password_hash):
        raise HTTPException(status_code=401, detail="密码错误")
    
    # 更新登录计数
    admin.login_count += 1
    admin.last_active_at = datetime.utcnow()
    db.commit()
    
    # 记录登录日志
    log = UserLog(user_id=admin.id, action="admin_login", detail={"email": req.email})
    db.add(log)
    db.commit()
    
    # 生成token
    token = create_admin_token(admin.id)
    
    return {
        "token": token,
        "user": {
            "id": admin.id,
            "nickname": admin.nickname,
            "email": admin.email,
            "is_admin": admin.is_admin
        }
    }


@router.get("/stats/dashboard")
def get_dashboard_stats(admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    """获取Dashboard统计数据"""
    today = date.today()
    yesterday = today - timedelta(days=1)
    week_start = today - timedelta(days=7)
    month_start = today - timedelta(days=30)
    
    # 用户统计
    total_users = db.query(func.count(User.id)).scalar()
    today_new_users = db.query(func.count(User.id)).filter(
        func.date(User.created_at) == today
    ).scalar()
    
    # 活跃用户统计
    active_today = db.query(func.count(User.id)).filter(
        func.date(User.last_active_at) == today
    ).scalar()
    active_week = db.query(func.count(User.id)).filter(
        User.last_active_at >= week_start
    ).scalar()
    
    # 命盘统计
    total_charts = db.query(func.count(Chart.id)).scalar()
    today_new_charts = db.query(func.count(Chart.id)).filter(
        func.date(Chart.created_at) == today
    ).scalar()
    
    # 签到统计
    today_checkins = db.query(func.count(Checkin.id)).filter(
        Checkin.checkin_date == today
    ).scalar()
    
    # 运势查看统计
    today_fortune_views = db.query(func.count(UserLog.id)).filter(
        UserLog.action == "fortune_view",
        func.date(UserLog.created_at) == today
    ).scalar()
    
    # 用户行为统计（今日）
    action_stats = db.query(
        UserLog.action,
        func.count(UserLog.id)
    ).filter(
        func.date(UserLog.created_at) == today
    ).group_by(UserLog.action).all()
    
    action_counts = {a: c for a, c in action_stats}
    
    # 过去30天用户增长趋势
    user_trend = []
    for i in range(30):
        d = today - timedelta(days=i)
        count = db.query(func.count(User.id)).filter(
            func.date(User.created_at) == d
        ).scalar()
        user_trend.append({"date": str(d), "count": count})
    
    # 过去30天活跃趋势
    active_trend = []
    for i in range(30):
        d = today - timedelta(days=i)
        count = db.query(func.count(User.id)).filter(
            func.date(User.last_active_at) == d
        ).scalar()
        active_trend.append({"date": str(d), "count": count})
    
    return {
        "users": {
            "total": total_users,
            "today_new": today_new_users,
            "active_today": active_today,
            "active_week": active_week
        },
        "charts": {
            "total": total_charts,
            "today_new": today_new_charts
        },
        "checkins": {
            "today": today_checkins
        },
        "fortune": {
            "today_views": today_fortune_views
        },
        "actions": action_counts,
        "trends": {
            "users_30d": user_trend,
            "active_30d": active_trend
        }
    }


@router.get("/users")
def get_user_list(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """获取用户列表"""
    query = db.query(User)
    
    if search:
        query = query.filter(
            or_(
                User.nickname.contains(search),
                User.phone.contains(search),
                User.email.contains(search)
            )
        )
    
    total = query.count()
    users = query.order_by(User.created_at.desc()).offset((page - 1) * limit).limit(limit).all()
    
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "users": [
            {
                "id": u.id,
                "nickname": u.nickname,
                "phone": u.phone,
                "email": u.email,
                "is_admin": u.is_admin,
                "checkin_days": u.checkin_days,
                "checkin_total": u.checkin_total,
                "charts_count": len(u.charts) if u.charts else 0,
                "last_active_at": str(u.last_active_at) if u.last_active_at else None,
                "created_at": str(u.created_at)
            }
            for u in users
        ]
    }


@router.get("/config")
def get_config(admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    """获取系统配置"""
    configs = db.query(SystemConfig).all()
    
    # 配置分组和类型定义
    config_meta = {
        # 广告配置
        "enable_ads": {"group": "广告配置", "type": "switch", "label": "开启广告"},
        "ad_banner_unit_id": {"group": "广告配置", "type": "text", "label": "Banner广告位ID"},
        "ad_reward_unit_id": {"group": "广告配置", "type": "text", "label": "激励视频广告位ID"},
        "ad_interstitial_unit_id": {"group": "广告配置", "type": "text", "label": "插屏广告位ID"},
        "ad_frequency_limit": {"group": "广告配置", "type": "number", "label": "每日广告次数限制"},
        
        # VIP配置
        "enable_vip": {"group": "VIP配置", "type": "switch", "label": "开启VIP功能"},
        "vip_month_price": {"group": "VIP配置", "type": "number", "label": "VIP月卡价格(元)"},
        "vip_year_price": {"group": "VIP配置", "type": "number", "label": "VIP年卡价格(元)"},
        "vip_svip_year_price": {"group": "VIP配置", "type": "number", "label": "SVIP年卡价格(元)"},
        "vip_free_days": {"group": "VIP配置", "type": "number", "label": "新用户免费体验天数"},
        
        # AI配置
        "ai_daily_limit_free": {"group": "AI配置", "type": "number", "label": "免费用户每日AI次数"},
        "ai_daily_limit_vip": {"group": "VIP配置", "type": "number", "label": "VIP用户每日AI次数"},
        "ai_provider": {"group": "AI配置", "type": "select", "label": "AI服务提供商", 
                        "options": [{"label": "模拟(Mock)", "value": "mock"}, 
                                    {"label": "OpenAI", "value": "openai"},
                                    {"label": "火山引擎", "value": "volcengine"}]},
        
        # 运势配置
        "fortune_enable": {"group": "运势配置", "type": "switch", "label": "开启每日运势"},
        "fortune_enable_share": {"group": "运势配置", "type": "switch", "label": "开启运势分享"},
        
        # 运营配置
        "app_name": {"group": "运营配置", "type": "text", "label": "小程序名称"},
        "home_banner_title": {"group": "运营配置", "type": "text", "label": "首页Banner标题"},
        "home_banner_subtitle": {"group": "运营配置", "type": "text", "label": "首页Banner副标题"},
        "customer_service": {"group": "运营配置", "type": "text", "label": "客服联系方式"},
        "user_agreement_url": {"group": "运营配置", "type": "text", "label": "用户协议链接"},
        "privacy_policy_url": {"group": "运营配置", "type": "text", "label": "隐私政策链接"},
        
        # 功能开关
        "enable_match": {"group": "功能开关", "type": "switch", "label": "双人匹配功能"},
        "enable_share": {"group": "功能开关", "type": "switch", "label": "分享功能"},
        "enable_checkin": {"group": "功能开关", "type": "switch", "label": "签到功能"},
    }
    
    # 按分组组织
    groups = {}
    for c in configs:
        meta = config_meta.get(c.key, {"group": "其他", "type": "text", "label": c.key})
        group_name = meta["group"]
        if group_name not in groups:
            groups[group_name] = []
        groups[group_name].append({
            "key": c.key,
            "value": c.value,
            "description": c.description,
            "type": meta.get("type", "text"),
            "label": meta.get("label", c.key),
            "options": meta.get("options")
        })
    
    return {
        "groups": groups,
        "flat": {c.key: {"value": c.value, "description": c.description} for c in configs}
    }


@router.put("/config")
def update_config(
    req: ConfigUpdateRequest,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """更新系统配置"""
    for key, value in req.configs.items():
        config = db.query(SystemConfig).filter(SystemConfig.key == key).first()
        if config:
            config.value = str(value)
        else:
            config = SystemConfig(key=key, value=str(value))
            db.add(config)
    db.commit()
    return {"success": True}


@router.post("/init-admin")
def init_admin_account(db: Session = Depends(get_db)):
    """初始化管理员账号（仅第一次使用）"""
    # 检查是否已存在管理员
    existing = db.query(User).filter(User.is_admin == True).first()
    if existing:
        raise HTTPException(status_code=400, detail="管理员账号已存在")
    
    # 创建管理员账号
    admin = User(
        nickname="管理员",
        email="admin@mingli.com",
        password_hash=hash_password("admin123"),  # 默认密码
        is_admin=True
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    
    # 初始化系统配置
    _init_default_configs(db)
    
    return {
        "success": True,
        "admin": {
            "id": admin.id,
            "email": admin.email,
            "default_password": "admin123"
        },
        "message": "管理员账号已创建，请及时修改密码"
    }


@router.post("/sync-configs")
def sync_default_configs(admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    """同步默认配置（补充缺失的配置项）"""
    added_count = _init_default_configs(db)
    return {"success": True, "added_count": added_count}


def _init_default_configs(db: Session) -> int:
    """初始化默认配置，返回新增的配置数量"""
    default_configs = [
        # 广告配置
        SystemConfig(key="enable_ads", value="false", description="是否开启广告"),
        SystemConfig(key="ad_banner_unit_id", value="", description="Banner广告位ID"),
        SystemConfig(key="ad_reward_unit_id", value="", description="激励视频广告位ID"),
        SystemConfig(key="ad_interstitial_unit_id", value="", description="插屏广告位ID"),
        SystemConfig(key="ad_frequency_limit", value="10", description="广告每日展示次数限制(次)"),
        
        # VIP配置
        SystemConfig(key="enable_vip", value="false", description="是否开启VIP功能"),
        SystemConfig(key="vip_month_price", value="19.9", description="VIP月卡价格(元)"),
        SystemConfig(key="vip_year_price", value="99", description="VIP年卡价格(元)"),
        SystemConfig(key="vip_svip_year_price", value="199", description="SVIP年卡价格(元)"),
        SystemConfig(key="vip_free_days", value="7", description="新用户VIP免费体验天数"),
        
        # AI配置
        SystemConfig(key="ai_daily_limit_free", value="3", description="免费用户每日AI解读次数"),
        SystemConfig(key="ai_daily_limit_vip", value="99", description="VIP用户每日AI解读次数"),
        SystemConfig(key="ai_provider", value="mock", description="AI服务提供商(mock/openai/volcengine)"),
        
        # 运势配置
        SystemConfig(key="fortune_enable", value="true", description="是否开启每日运势功能"),
        SystemConfig(key="fortune_enable_share", value="true", description="是否开启运势分享"),
        
        # 运营配置
        SystemConfig(key="app_name", value="命里", description="小程序名称"),
        SystemConfig(key="home_banner_title", value="探索你的命理奥秘", description="首页Banner标题"),
        SystemConfig(key="home_banner_subtitle", value="紫微斗数 · 八字排盘 · AI解读", description="首页Banner副标题"),
        SystemConfig(key="customer_service", value="", description="客服联系方式"),
        SystemConfig(key="user_agreement_url", value="", description="用户协议链接"),
        SystemConfig(key="privacy_policy_url", value="", description="隐私政策链接"),
        
        # 功能开关
        SystemConfig(key="enable_match", value="true", description="是否开启双人匹配"),
        SystemConfig(key="enable_share", value="true", description="是否开启分享功能"),
        SystemConfig(key="enable_checkin", value="true", description="是否开启签到功能"),
    ]
    
    added = 0
    for config in default_configs:
        existing = db.query(SystemConfig).filter(SystemConfig.key == config.key).first()
        if not existing:
            db.add(config)
            added += 1
    db.commit()
    return added