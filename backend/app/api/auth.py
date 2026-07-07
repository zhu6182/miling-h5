from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import requests
from app.core.database import get_db
from app.core.security import create_access_token
from app.core.config import settings
from app.schemas.schemas import UserCreate, UserLogin, UserResponse, Token, WechatLoginRequest
from app.services.user_service import create_user, authenticate_user, get_user_by_phone
from app.models.models import User

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register", response_model=Token)
def register(user_create: UserCreate, db: Session = Depends(get_db)):
    existing = get_user_by_phone(db, user_create.phone)
    if existing:
        raise HTTPException(status_code=400, detail="该手机号已注册")
    user = create_user(db, user_create)
    access_token = create_access_token(data={"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer", "user": user}


@router.post("/login", response_model=Token)
def login(user_login: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, user_login.phone, user_login.password)
    if not user:
        raise HTTPException(status_code=401, detail="手机号或密码错误")
    access_token = create_access_token(data={"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer", "user": user}


def get_wechat_openid(code: str) -> str:
    """调用微信官方 API 获取 openid"""
    if not settings.WECHAT_APPID or not settings.WECHAT_SECRET:
        return None

    url = (
        "https://api.weixin.qq.com/sns/jscode2session"
        f"?appid={settings.WECHAT_APPID}"
        f"&secret={settings.WECHAT_SECRET}"
        f"&js_code={code}"
        "&grant_type=authorization_code"
    )

    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if "openid" in data:
            return data["openid"]
        else:
            print(f"微信登录失败: {data}")
            return None
    except Exception as e:
        print(f"微信 API 调用失败: {e}")
        return None


@router.post("/wechat-login", response_model=Token)
def wechat_login(req: WechatLoginRequest, db: Session = Depends(get_db)):
    """微信一键登录"""
    if not req.code:
        raise HTTPException(status_code=400, detail="缺少 code 参数")

    openid = get_wechat_openid(req.code)

    if not openid:
        if settings.DEBUG:
            if req.code.startswith("test") or len(req.code) < 30:
                openid = "wx_dev_user"
            else:
                openid = "wx_" + req.code[:20]
        else:
            raise HTTPException(status_code=401, detail="微信登录失败")

    user = db.query(User).filter(User.openid == openid).first()
    if not user:
        user = User(
            openid=openid,
            nickname=req.nickname or "微信用户",
            avatar=req.avatar or "",
            ai_provider="mock",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    access_token = create_access_token(data={"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer", "user": user}
