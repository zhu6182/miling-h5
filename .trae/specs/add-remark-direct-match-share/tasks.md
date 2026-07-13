# Tasks

## Phase 1: 数据模型 & 后端基础

- [ ] Task 1.1: 数据库迁移 - charts 表加 remark 和 chart_type 字段
  - 对 mingli.db 执行 ALTER TABLE
  - 更新 models.py Chart 模型加字段
  - 更新 schemas.py ChartCreate/ChartResponse 加 remark/chart_type

- [ ] Task 1.2: 后端 charts API 改造 - 支持按类型查询和更新备注
  - GET /charts 新增 type 参数 (my|helped|all)
  - PATCH /charts/{id} 支持更新 remark

---

## Phase 2: 前端 - 备注录入

- [ ] Task 2.1: birth-input 页面加备注输入框
  - birth-input.wxml 加备注 input
  - birth-input.js 绑定 onRemarkInput 和 onOwnerTypeChange（我/帮别人查）
  - 提交时传递 remark 和 is_own 参数

---

## Phase 3: 前端 - 首页 Tab 切换

- [ ] Task 3.1: index 页面加「我的」/「帮查」Tab 切换
  - index.wxml 加 tab 切换组件
  - index.js 加 loadCharts(type) 方法，type=my 时过滤 remark 为空的，type=helped 时过滤 remark 非空的
  - 显示帮查命盘时显示备注标签

---

## Phase 4: 直接匹配功能

- [ ] Task 4.1: 命盘详情页加「找人匹配」按钮
  - chart-detail.js 加 goMatch() 方法 - 弹出命盘选择器
  - bazi-detail.js 加 goMatch() 方法 - 同上
  - 共用命盘选择组件（modal 展示我的命盘列表，支持搜索）

- [ ] Task 4.2: 命盘选择器组件
  - 创建命盘选择 modal 页面或组件
  - 调用 GET /charts?type=my 获取我的命盘列表
  - 选择后调用 POST /match 发起匹配，跳转 match-result

- [ ] Task 4.3: match-result 页面支持从详情页传入的 chart_id
  - 接收 source_chart_id 和 target_chart_id
  - 调用 POST /match 计算匹配

---

## Phase 5: 分享推广功能

- [ ] Task 5.1: 分享卡片生成（后端）
  - POST /share/reading 接口 - 接收 chart_id 和 reading_data
  - 返回分享文案（不含生辰，只含解读结论）
  - 未来扩展：生成小程序码 URL

- [ ] Task 5.2: chart-detail 分享按钮
  - 加「分享」按钮
  - 点击调用 POST /share/reading 获取文案
  - 调用 wx.showShareImage 或生成分享图

- [ ] Task 5.3: bazi-detail 分享按钮
  - 同上

- [ ] Task 5.4: match-result 分享按钮
  - 分享匹配结果卡片，只含缘分指数和结论

---

## Task Dependencies

- Task 1.2 依赖 Task 1.1（数据库字段存在才能更新）
- Task 2.1 依赖 Task 1.1（后端字段就绪）
- Task 3.1 依赖 Task 1.2（后端支持按类型查询）
- Task 4.1、4.2 依赖 Task 3.1（命盘列表可用）
- Task 5.1 可独立开发
- Task 5.2、5.3、5.4 依赖 Task 5.1
