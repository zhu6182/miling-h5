# 添加火山方舟（豆包大模型）AI 接口 - 实施计划

## 一、背景与目标

### 当前状态
- 后端已有 `MockAIProvider`（内置模板解读）和 `OpenAIProvider`（OpenAI 兼容接口）
- 小程序端 AI 设置有三个选项：内置 / OpenAI / 通义千问（通义千问后端未实现）
- AI 服务采用 Provider 模式，通过 `get_ai_provider()` 工厂函数创建实例

### 目标
新增火山方舟（豆包大模型）作为第三种 AI Provider，用户可在小程序中配置自己的火山 API Key 使用。

---

## 二、改动文件清单

### 后端（2 个文件）
1. `backend/app/services/ai_service.py`
   - 新增 `VolcengineProvider` 类（OpenAI 兼容模式）
   - 在 `get_ai_provider()` 工厂函数中注册 `volcengine` 类型

2. `backend/app/api/charts.py`
   - 确保 reading 接口支持 `volcengine` provider

### 前端（2 个文件）
1. `miniprogram/pages/profile/profile.wxml`
   - AI Provider 选项添加"豆包/火山"按钮

2. `miniprogram/pages/profile/profile.js`
   - 默认模型改为豆包默认模型（如 `doubao-1-5-pro-32k-250115`）

---

## 三、实施步骤

### 步骤 1：后端新增 VolcengineProvider
- 使用火山方舟 OpenAI 兼容模式实现（零额外依赖）
- Base URL: `https://ark.cn-beijing.volces.com/api/v3`
- 新增 `VolcengineProvider` 类，调用方式与 OpenAI 完全一致
- 复用现有 prompt 构建和返回解析逻辑

### 步骤 2：注册到工厂函数
- 在 `get_ai_provider()` 中添加 `volcengine` 分支
- 参数：`api_key`、`model`、`base_url`（或 endpoint id）

### 步骤 3：前端 UI 更新
- profile 页面 AI Provider 选项从 3 个改为 4 个（内置 / OpenAI / 通义千问 / 豆包）
- 选择豆包时显示 API Key 和模型输入框
- 默认模型填豆包推荐模型名

### 步骤 4：测试验证
- 使用 mock 模式验证代码结构正确
- 确认接口调用路径通畅
- 确认存储和读取 ai_provider 配置正常

---

## 四、技术方案细节

### 火山方舟 OpenAI 兼容模式
- Base URL: `https://ark.cn-beijing.volces.com/api/v3`
- API Key: 用户在火山方舟控制台生成
- 模型: 使用推理接入点 ID（Endpoint ID），如 `ep-20240101xxxxxx-xxxxx`
- 调用方式与 OpenAI 完全一致：`client.chat.completions.create()`

### 代码复用策略
- 抽取 `BaseAIProvider` 基类，包含 `_build_prompt()` 和 `_parse_response()`
- `OpenAIProvider` 和 `VolcengineProvider` 都继承自 `BaseAIProvider`
- `MockAIProvider` 也继承 `BaseAIProvider` 但完全覆写 `generate_reading()`

---

## 五、风险与应对

| 风险 | 影响 | 应对方案 |
|------|------|----------|
| 火山 SDK 安装失败 | 无法使用豆包 | 优先用 OpenAI 兼容模式，零额外依赖 |
| 模型名称不对 | 调用失败 | 在 UI 提示用户填写推理接入点 ID（Endpoint ID） |
| 解析返回 JSON 失败 | 解读不显示 | fallback 到 Mock 模式（已有逻辑） |

---

## 六、关于后台管理系统

用户确认不需要额外的 Web 管理后台。当前架构（小程序前端 + FastAPI 后端 + SQLite 数据库）已满足需求。
