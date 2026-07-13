from sqlalchemy.orm import Session
from app.models.models import User, Chart
from app.schemas.schemas import UserCreate, UserUpdate
from app.core.security import hash_password, verify_password


def get_user_by_phone(db: Session, phone: str) -> User:
    return db.query(User).filter(User.phone == phone).first()


def get_user_by_username(db: Session, username: str) -> User:
    return db.query(User).filter(User.username == username).first()


def get_user_by_id(db: Session, user_id: int) -> User:
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, user_create: UserCreate) -> User:
    db_user = User(
        username=user_create.username,
        password_hash=hash_password(user_create.password),
        nickname=user_create.nickname or user_create.username,
        gender=user_create.gender,
        birth_date=user_create.birth_date,
        birth_hour=user_create.birth_hour,
        birth_place=user_create.birth_place,
        solar_lunar=user_create.solar_lunar,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.password_hash or ""):
        return None
    return user


def update_user(db: Session, user_id: int, user_update: UserUpdate) -> User:
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    update_data = user_update.model_dump(exclude_unset=True)
    if 'password' in update_data and update_data['password']:
        update_data['password_hash'] = hash_password(update_data.pop('password'))
    for key, value in update_data.items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user
