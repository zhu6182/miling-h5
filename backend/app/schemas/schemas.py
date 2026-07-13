from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class UserBase(BaseModel):
    username: Optional[str] = None
    phone: Optional[str] = None
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[str] = None
    birth_hour: Optional[int] = None
    birth_place: Optional[str] = None
    solar_lunar: Optional[str] = "solar"


class UserCreate(UserBase):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class WechatLoginRequest(BaseModel):
    code: str
    nickname: Optional[str] = "微信用户"
    avatar: Optional[str] = ""


class UserUpdate(UserBase):
    password: Optional[str] = None
    ai_provider: Optional[str] = None
    ai_api_key: Optional[str] = None
    ai_model: Optional[str] = None
    ai_base_url: Optional[str] = None


class UserResponse(UserBase):
    id: int
    ai_provider: Optional[str] = None
    ai_model: Optional[str] = None
    ai_base_url: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class ChartCreate(BaseModel):
    name: Optional[str] = "我的命盘"
    solar_date: Optional[str] = None
    lunar_date: Optional[str] = None
    gender: str
    hour_index: int
    is_default: Optional[bool] = False
    remark: Optional[str] = None
    chart_type: Optional[str] = "ziwei"


class ChartUpdate(BaseModel):
    name: Optional[str] = None
    reading_data: Optional[Dict[str, Any]] = None
    remark: Optional[str] = None
    chart_type: Optional[str] = None


class ChartResponse(BaseModel):
    id: int
    user_id: int
    name: str
    solar_date: Optional[str] = None
    lunar_date: Optional[str] = None
    gender: str
    hour_index: int
    hour_name: Optional[str] = None
    five_elements: Optional[str] = None
    soul_palace: Optional[str] = None
    body_palace: Optional[str] = None
    chart_data: Optional[Dict[str, Any]] = None
    reading_data: Optional[Dict[str, Any]] = None
    is_default: bool
    remark: Optional[str] = None
    chart_type: Optional[str] = None
    created_at: Optional[datetime] = None
    bazi_pillars: Optional[str] = None
    bazi_display: Optional[str] = None

    class Config:
        from_attributes = True


class ChartCalculateRequest(BaseModel):
    solar_date: Optional[str] = None
    lunar_date: Optional[str] = None
    gender: str
    hour_index: int
    is_leap: Optional[bool] = False
    is_default: Optional[bool] = False
    name: Optional[str] = "我的命盘"
    remark: Optional[str] = None
    chart_type: Optional[str] = "ziwei"


class ReadingRequest(BaseModel):
    chart_id: Optional[int] = None
    style: Optional[str] = "friendly"
    sections: Optional[List[str]] = None
    ad_watched: Optional[bool] = False  # 是否已看完广告


class MatchRequest(BaseModel):
    target_user_id: Optional[int] = None
    match_type: Optional[str] = "all"
    chart_a_id: Optional[int] = None
    chart_b_id: Optional[int] = None


class AdminLoginRequest(BaseModel):
    email: str
    password: str


class AdminStatsResponse(BaseModel):
    users: Dict[str, Any]
    charts: Dict[str, Any]
    checkins: Dict[str, Any]
    fortune: Dict[str, Any]
    actions: Dict[str, int]
    trends: Dict[str, List[Dict[str, Any]]]


class UserListResponse(BaseModel):
    total: int
    page: int
    limit: int
    users: List[Dict[str, Any]]


class ConfigResponse(BaseModel):
    configs: Dict[str, Dict[str, str]]


class ConfigUpdateRequest(BaseModel):
    configs: Dict[str, Any]
