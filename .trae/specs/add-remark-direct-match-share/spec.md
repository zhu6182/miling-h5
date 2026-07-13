# 帮查备注 + 直接匹配 + 分享推广 Spec

## Why
用户只用输入一次生辰八字，就可以查八字和紫微，还会帮人去查（需备注区分），还可以直接匹配命盘，以及分享结论给好友进行互动。八字是隐私，分享时只放结论不暴露生辰原始数据。

## What Changes

### 新增功能
1. **帮谁查备注** - birth-input 加备注字段，Chart 模型支持 remark，首页/历史记录区分"我的"和"帮查"的命盘
2. **直接匹配** - 命盘详情页（chart-detail/bazi-detail）直接发起匹配，选择自己保存的另一个命盘
3. **分享推广** - 生成只含结论文字的分享卡片（无生辰数据），带小程序码/链接，好友扫码进入小程序首页

### 数据模型变更
- `charts` 表加 `remark` 字段（VARCHAR(100)，可空）
- `charts` 表加 `chart_type` 字段（ENUM: 'ziwei'/'bazi'），区分命盘类型

### 页面变更
- birth-input：加备注输入框
- index：我的命盘 / 帮查命盘  Tab 切换
- chart-detail/bazi-detail：加「找人匹配」按钮、加「分享」按钮
- match-result：展示双人匹配结论（可分享）

## Impact
- Affected: 紫微/八字命盘系统
- 后端: models.py, schemas.py, charts.py, match.py
- 前端: birth-input, index, chart-detail, bazi-detail, match-result, profile

---

## ADDED Requirements

### Requirement: 帮谁查备注
系统 SHALL 支持在录入生辰时填写备注（如"妈妈"、"老公"、"闺蜜"），并区分"我的命盘"和"帮查的命盘"。

#### Scenario: 帮妈妈查八字
- **WHEN** 用户在 birth-input 输入生辰，并在备注栏填"妈妈"，选择"帮别人查"
- **THEN** 命盘保存时 remark="妈妈"，在首页显示为「帮查」标签
- **AND** 命盘详情页显示"帮妈妈查的命盘"

#### Scenario: 查看我的命盘
- **WHEN** 用户在首页切换到「我的命盘」Tab
- **THEN** 只显示 remark 为空或自己的命盘
- **AND** 帮查的命盘不显示

---

### Requirement: 直接匹配
系统 SHALL 支持在任意命盘详情页直接选择另一个命盘发起双人匹配。

#### Scenario: 从八字详情发起匹配
- **WHEN** 用户在 bazi-detail 页点击「找人匹配」
- **THEN** 弹出自己保存的命盘列表（支持搜索）
- **AND** 用户选择一个命盘后，跳转到 match-result 页展示匹配结果

#### Scenario: 从紫微详情发起匹配
- **WHEN** 用户在 chart-detail 页点击「找人匹配」
- **THEN** 同上，弹出命盘列表，选择后跳转 match-result

---

### Requirement: 分享推广（隐私优先）
系统 SHALL 支持生成只含结论文字的分享图片，不包含任何生辰原始数据。

#### Scenario: 分享八字结论
- **WHEN** 用户在 bazi-detail 页点击「分享」
- **THEN** 生成一张图片，包含：命主称呼（备注或"我的"）、性格解读摘要、事业/姻缘/财运结论
- **AND** 图片底部带小程序码/「扫码查看你的命盘」
- **AND** 不包含：出生日期、时辰、四柱原始数据

#### Scenario: 分享匹配结果
- **WHEN** 用户在 match-result 页点击「分享」
- **THEN** 生成一张图片，包含：缘分指数、双方称呼（备注或"我"）、匹配结论摘要
- **AND** 不包含：双方生辰原始数据

#### Scenario: 好友扫码进入
- **WHEN** 好友扫描分享图的小程序码
- **THEN** 打开小程序首页，需自己输入生辰才能查看解读
- **AND** 好友看到的解读是自己的，不是分享者的

---

## MODIFIED Requirements

### Requirement: 命盘录入流程
**原来的**: birth-input 只保存紫微命盘
**修改为**: birth-input 支持选择「帮别人查」并填写备注字段，提交时根据 chartType 保存对应类型的命盘（紫微/八字），remark 字段存入数据库

### Requirement: 命盘列表查询
**原来的**: index 页查询自己所有命盘
**修改为**: index 页加「我的」/「帮查」Tab 切换，帮我查的命盘显示备注标签

---

## Technical Design

### 数据库变更
```sql
ALTER TABLE charts ADD COLUMN remark VARCHAR(100);
ALTER TABLE charts ADD COLUMN chart_type ENUM('ziwei', 'bazi') DEFAULT 'ziwei';
```

### 后端接口
- `PATCH /charts/{id}` - 更新 remark 和 chart_type
- `GET /charts?type=my|helped` - 按类型查询命盘
- `POST /match` - 发起匹配（支持 chart_id 指定命盘）
- `POST /share/reading` - 生成分享图片文字（不含生辰）

### 前端页面
- birth-input.wxml: 加 `<input placeholder="备注：如妈妈、老公、闺蜜" bindinput="onRemarkInput">`
- index.wxml: 加 tab 切换「我的」/「帮查」
- chart-detail.wxml: 加「匹配」和「分享」按钮
- bazi-detail.wxml: 加「匹配」和「分享」按钮
- match-result.wxml: 加「分享」按钮

### 分享卡片内容规范
```
┌─────────────────────────┐
│  [命主称呼] 的命盘解读     │
│                         │
│  性格特点：xxx           │
│  事业运势：xxx           │
│  姻缘走势：xxx           │
│                         │
│  ─────────────────────  │
│  扫码查看你的命盘         │
│  [小程序码]              │
└─────────────────────────┘
```

---

## REMOVED Requirements
无
