# 恢复原始小程序布局方案

## 目标

将 H5 版本完全恢复为原始小程序的布局和功能，保持视觉和交互一致。

## 核心改动

### 1. 全局样式 - 金色主题

**文件：** `web/src/style.css`

恢复原始配色：
- 背景：`#0a0a1a`
- 主色调：`#c9a050`（金色）
- 文字：`#e0e0f0`、`#8888a0`、`#666680`
- 边框：`rgba(201, 160, 80, 0.2)`

### 2. 首页 - 完整恢复

**文件：** `web/src/pages/Index.vue`

按小程序 `pages/index/index.wxml` 恢复：
- 标题区："星运日记 · 每日星座运势" + slogan
- Tab切换：我的 / 帮查
- 星盘概览卡片（有星盘时）
- 星盘列表（多星盘时）
- 快捷操作区：今日运势、星盘解析、性格测试、运势曲线
- 核心功能介绍（2列网格）

### 3. 运势页 - 完整恢复

**文件：** `web/src/pages/Fortune.vue`

按小程序 `pages/fortune/fortune.wxml` 恢复：
- 日期 + 干支显示
- 圆形分数展示（金色渐变）
- 分维度进度条（爱情/事业/财运/健康）
- 宜忌建议（并排卡片）
- 幸运元素
- 签到区域
- 分享按钮

### 4. 出生输入页 - 完整恢复

**文件：** `web/src/pages/BirthInput.vue`

按小程序 `pages/birth-input/birth-input.wxml` 恢复：
- 排盘方式：紫微斗数 / 八字四柱
- 历法：公历 / 农历
- 日期选择器
- 时辰选择（3列网格，带时间段）
- 性别选择
- 查询对象：为自己查 / 帮别人查
- 备注输入
- 提交按钮

### 5. 星盘详情页 - 完整恢复

**文件：** `web/src/pages/ChartDetail.vue`

按小程序 `pages/chart-detail/chart-detail.wxml` 恢复：
- 星盘标题 + 五行标签
- 操作按钮：查看八字、分享、找人匹配
- 生年四化标签
- 4x4星盘宫格
- AI解读区域

### 6. 配对页 & 个人中心 - 恢复配色

**文件：** `web/src/pages/Match.vue`, `web/src/pages/Profile.vue`

更新配色为金色主题，保持现有功能结构。

### 7. 导航组件 - 金色主题

**文件：** `web/src/components/NavBar.vue`, `web/src/components/TabBar.vue`

更新配色为金色主题。

## 实施步骤

1. 更新 `style.css` 全局样式
2. 重构 `Index.vue`
3. 重构 `Fortune.vue`
4. 重构 `BirthInput.vue`
5. 重构 `ChartDetail.vue`
6. 更新 `Match.vue`、`Profile.vue` 配色
7. 更新导航组件
8. 构建验证

## 验证标准

- `npm run build` 无错误
- 各页面布局与小程序一致
- 功能正常可用
