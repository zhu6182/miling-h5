from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def auto_migrate():
    """自动迁移：为已存在的表添加缺失的列（SQLite兼容）"""
    from sqlalchemy import inspect
    from app.models.models import User, DailyFortune, Checkin, UserLog, SystemConfig
    
    inspector = inspect(engine)
    
    # 确保新表被创建
    Base.metadata.create_all(bind=engine)
    
    # User表：添加缺失的列
    if 'users' in inspector.get_table_names():
        existing_cols = {c['name'] for c in inspector.get_columns('users')}
        
        user_new_columns = [
            ('username', 'VARCHAR(50)'),
            ('is_admin', 'BOOLEAN DEFAULT 0'),
            ('email', 'VARCHAR(100)'),
            ('last_active_at', 'TIMESTAMP'),
            ('login_count', 'INTEGER DEFAULT 0'),
            ('checkin_days', 'INTEGER DEFAULT 0'),
            ('checkin_total', 'INTEGER DEFAULT 0'),
            ('last_checkin_date', 'DATE'),
        ]
        
        with engine.connect() as conn:
            for col_name, col_def in user_new_columns:
                if col_name not in existing_cols:
                    try:
                        conn.execute(text(f'ALTER TABLE users ADD COLUMN {col_name} {col_def}'))
                        print(f'  + 添加 users.{col_name}')
                    except Exception as e:
                        print(f'  ! 添加 users.{col_name} 失败: {e}')
            conn.commit()
    
    print('数据库迁移完成')
