from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.models import User, Friendship
from app.schemas.schemas import UserResponse
from pydantic import BaseModel

router = APIRouter(prefix="/friends", tags=["好友"])


class AddFriendRequest(BaseModel):
    friend_id: int


class UpdateFriendRemarkRequest(BaseModel):
    remark: str


@router.post("")
def add_friend(req: AddFriendRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """添加好友"""
    if req.friend_id == user.id:
        raise HTTPException(status_code=400, detail="不能添加自己为好友")

    friend = db.query(User).filter(User.id == req.friend_id).first()
    if not friend:
        raise HTTPException(status_code=404, detail="用户不存在")

    existing = db.query(Friendship).filter(
        Friendship.user_id == user.id,
        Friendship.friend_id == req.friend_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="已添加该用户为好友")

    friendship = Friendship(
        user_id=user.id,
        friend_id=req.friend_id
    )
    db.add(friendship)
    db.commit()
    db.refresh(friendship)

    return {"status": "success", "message": "添加好友成功"}


@router.get("")
def get_friends(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """获取好友列表"""
    friendships = db.query(Friendship).filter(Friendship.user_id == user.id).order_by(Friendship.created_at.desc()).all()

    result = []
    for f in friendships:
        friend = db.query(User).filter(User.id == f.friend_id).first()
        if friend:
            result.append({
                "friend_id": friend.id,
                "username": friend.username,
                "nickname": f.remark or friend.nickname,
                "avatar": friend.avatar,
                "gender": friend.gender,
                "remark": f.remark,
                "created_at": str(f.created_at)
            })

    return {"friends": result}


@router.put("/{friend_id}")
def update_friend_remark(
    friend_id: int,
    req: UpdateFriendRemarkRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """修改好友备注"""
    friendship = db.query(Friendship).filter(
        Friendship.user_id == user.id,
        Friendship.friend_id == friend_id
    ).first()

    if not friendship:
        raise HTTPException(status_code=404, detail="好友关系不存在")

    friendship.remark = req.remark
    friendship.updated_at = datetime.now()
    db.commit()

    return {"status": "success", "message": "备注修改成功"}


@router.delete("/{friend_id}")
def remove_friend(
    friend_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """删除好友"""
    friendship = db.query(Friendship).filter(
        Friendship.user_id == user.id,
        Friendship.friend_id == friend_id
    ).first()

    if not friendship:
        raise HTTPException(status_code=404, detail="好友关系不存在")

    db.delete(friendship)
    db.commit()

    return {"status": "success", "message": "删除好友成功"}