# 命里 - 命理匹配平台

基于紫微斗数的 AI 命盘解读 + 双人匹配小程序。

## 项目结构

```
miling/
├── backend/                    # 后端服务 (Python + FastAPI)
│   ├── app/
│   │   ├── api/                # API 路由
│   │   │   ├── auth.py         # 认证接口（注册/登录）
│   │   │   ├── users.py        # 用户接口（排盘/命盘列表）
│   │   │   ├── charts.py       # 命盘接口（CRUD/AI解读）
│   │   │   └── deps.py         # 认证依赖
│   │   ├── core/               # 核心模块
│   │   │   ├── config.py       # 配置管理
│   │   │   ├── database.py     # 数据库连接
│   │   │   └── security.py     # 安全工具（JWT/密码哈希）
│   │   ├── models/             # 数据库模型
│   │   ├── schemas/            # Pydantic 数据模型
│   │   ├── services/           # 业务服务
│   │   │   ├── chart_service.py    # 排盘计算（iztro-py）
│   │   │   ├── ai_service.py       # AI 解读（可插拔）
│   │   │   └── user_service.py     # 用户服务
│   │   └── main.py             # 应用入口
│   ├── run.py                  # 启动脚本
│   ├── requirements.txt        # Python 依赖
│   └── mingli.db               # SQLite 数据库（自动生成）
│
├── miniprogram/                # 微信小程序
│   ├── app.js / app.json / app.wxss
│   ├── pages/
│   │   ├── index/              # 首页（命盘概览）
│   │   ├── chart/              # 匹配页
│   │   ├── chart-detail/       # 命盘详情页
│   │   ├── birth-input/        # 生辰录入页
│   │   └── profile/            # 个人中心
│   ├── components/
│   └── utils/
│
└── mingli-master/              # 原始项目（参考）
```

## 快速开始

### 1. 启动后端

```bash
cd backend
pip install -r requirements.txt
python run.py
```

服务启动在 http://localhost:8000

API 文档：http://localhost:8000/docs

### 2. 小程序

用微信开发者工具打开 `miniprogram` 目录。

修改 `miniprogram/app.js` 中的 `BASE_URL` 为你的后端地址。

## API 接口

### 认证
- `POST /api/v1/auth/register` - 注册
- `POST /api/v1/auth/login` - 登录

### 用户 & 命盘
- `GET /api/v1/users/me` - 获取当前用户
- `PUT /api/v1/users/me` - 更新用户信息
- `GET /api/v1/users/me/charts` - 我的命盘列表
- `POST /api/v1/users/calculate-chart` - 计算排盘（不保存）
- `POST /api/v1/users/save-chart` - 计算并保存命盘

### 命盘详情
- `GET /api/v1/charts/{id}` - 获取命盘详情
- `PUT /api/v1/charts/{id}` - 更新命盘
- `DELETE /api/v1/charts/{id}` - 删除命盘
- `POST /api/v1/charts/{id}/reading` - 生成 AI 解读

## AI 解读配置

支持多种 AI 提供商，在用户设置中配置：

- **mock** - 内置模拟数据（默认，无需 API Key）
- **openai** - OpenAI GPT 系列
- （更多待添加）

## 开发路线图

- [x] **第一阶段**：后端核心 + 单人命盘小程序
- [ ] **第二阶段**：双人匹配功能（扫码/NFC/分享）
- [ ] **第三阶段**：手相识别 + 好友系统
- [ ] **第四阶段**：分享图片 + 性能优化

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python 3.11 + FastAPI + SQLAlchemy |
| 数据库 | SQLite |
| 排盘计算 | iztro-py |
| AI 解读 | 可插拔（Mock / OpenAI / 通义千问） |
| 前端 | 微信小程序原生 |
