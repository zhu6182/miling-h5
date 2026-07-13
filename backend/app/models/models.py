from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Boolean, ForeignKey, Date
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=True)
    phone = Column(String(20), unique=True, index=True, nullable=True)
    password_hash = Column(String(255), nullable=True)
    openid = Column(String(100), unique=True, index=True, nullable=True)
    nickname = Column(String(50), default="匿名用户")
    avatar = Column(String(500), nullable=True)
    gender = Column(String(10), nullable=True)
    birth_date = Column(String(20), nullable=True)
    birth_hour = Column(Integer, nullable=True)
    birth_place = Column(String(100), nullable=True)
    solar_lunar = Column(String(10), default="solar")
    ai_provider = Column(String(50), default="mock")
    ai_api_key = Column(String(500), nullable=True)
    ai_model = Column(String(100), nullable=True)
    ai_base_url = Column(String(500), nullable=True)
    # 管理员和统计字段
    is_admin = Column(Boolean, default=False)
    email = Column(String(100), nullable=True)  # 管理员邮箱
    last_active_at = Column(DateTime(timezone=True), nullable=True)
    login_count = Column(Integer, default=0)
    # 签到相关字段
    checkin_days = Column(Integer, default=0)  # 连续签到天数
    checkin_total = Column(Integer, default=0)  # 累计签到天数
    last_checkin_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    charts = relationship("Chart", back_populates="user", cascade="all, delete-orphan")
    checkins = relationship("Checkin", back_populates="user", cascade="all, delete-orphan")
    daily_fortunes = relationship("DailyFortune", back_populates="user", cascade="all, delete-orphan")
    user_logs = relationship("UserLog", back_populates="user", cascade="all, delete-orphan")


class Chart(Base):
    __tablename__ = "charts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(100), default="我的命盘")
    solar_date = Column(String(20))
    lunar_date = Column(String(20), nullable=True)
    gender = Column(String(10))
    hour_index = Column(Integer)
    hour_name = Column(String(50))
    five_elements = Column(String(20))
    soul_palace = Column(String(20))
    body_palace = Column(String(20))
    chart_data = Column(JSON)
    reading_data = Column(JSON, nullable=True)
    reading_unlocked = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    remark = Column(String(100), nullable=True)
    chart_type = Column(String(20), default='ziwei')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="charts")


class DailyFortune(Base):
    __tablename__ = "daily_fortunes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    chart_id = Column(Integer, ForeignKey("charts.id"))
    fortune_date = Column(Date, index=True)
    overall_score = Column(Integer)
    love_score = Column(Integer)
    career_score = Column(Integer)
    wealth_score = Column(Integer)
    health_score = Column(Integer)
    lucky_color = Column(String(50))
    lucky_number = Column(String(50))
    lucky_direction = Column(String(50))
    do_list = Column(Text)  # JSON数组
    avoid_list = Column(Text)  # JSON数组
    phrase = Column(String(200))  # 今日运势短语
    analysis = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="daily_fortunes")


class Checkin(Base):
    __tablename__ = "checkins"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    checkin_date = Column(Date, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="checkins")


class UserLog(Base):
    __tablename__ = "user_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(50), index=True)  # login, chart_create, ai_reading, match, checkin等
    detail = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="user_logs")


class SystemConfig(Base):
    __tablename__ = "system_config"

    key = Column(String(50), primary_key=True)
    value = Column(Text)
    description = Column(String(200), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Friendship(Base):
    __tablename__ = "friendships"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    friend_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    remark = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("user_id", "friend_id", name="uq_user_friend"),
    )
