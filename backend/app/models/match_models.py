from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class MatchStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"


class MatchType(str, enum.Enum):
    LOVE = "love"
    CAREER = "career"
    FRIENDSHIP = "friendship"
    MENTOR = "mentor"
    ALL = "all"


class MatchRecord(Base):
    __tablename__ = "match_records"

    id = Column(Integer, primary_key=True, index=True)
    user_a_id = Column(Integer, ForeignKey("users.id"))
    user_b_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user_a_nickname = Column(String(100))
    user_b_nickname = Column(String(100), nullable=True)
    match_type = Column(String(20), default="all")
    status = Column(String(20), default="pending")
    qr_code = Column(String(100), unique=True, nullable=True)
    match_data = Column(JSON, nullable=True)
    result_unlocked = Column(Boolean, default=True)  # 匹配结果是否已解锁（默认免费）
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Friend(Base):
    __tablename__ = "friends"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    friend_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String(20), default="active")
    note = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
