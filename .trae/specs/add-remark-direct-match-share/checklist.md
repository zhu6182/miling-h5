# Checklist

## 数据库 & 后端基础

- [ ] charts 表加 remark VARCHAR(100) 字段
- [ ] charts 表加 chart_type ENUM('ziwei', 'bazi') 字段
- [ ] models.py Chart 类加 remark 和 chart_type 属性
- [ ] schemas.py ChartCreate/ChartResponse 加 remark 和 chart_type 字段
- [ ] GET /charts 支持 type=my|helped 参数过滤
- [ ] PATCH /charts/{id} 支持更新 remark 和 chart_type

## 备注录入

- [ ] birth-input.wxml 加备注输入框 placeholder="备注：如妈妈、老公、闺蜜"
- [ ] birth-input.wxml 加「为自己查」/「帮别人查」切换
- [ ] birth-input.js 提交时传递 remark 和 is_own 参数

## 首页 Tab 切换

- [ ] index.wxml 加「我的」/「帮查」Tab 切换 UI
- [ ] index.js loadCharts() 支持 type 参数过滤
- [ ] 帮查命盘显示备注标签（如「妈妈」「老公」）

## 直接匹配

- [ ] chart-detail.js 加 goMatch() 方法，弹出命盘选择器
- [ ] bazi-detail.js 加 goMatch() 方法，弹出命盘选择器
- [ ] 命盘选择器展示我的命盘列表，支持切换到 bazi-detail 类型
- [ ] 选择命盘后调用 POST /match，跳转 match-result

## 分享推广

- [ ] POST /share/reading 接口返回不含生辰的分享文案
- [ ] chart-detail 分享按钮生成结论卡片
- [ ] bazi-detail 分享按钮生成结论卡片
- [ ] match-result 分享按钮生成匹配结果卡片（只含缘分指数+双方称呼）
- [ ] 分享卡片不包含任何生辰原始数据

## 验证

- [ ] 数据库 ALTER TABLE 执行成功
- [ ] 帮别人查命盘能填备注并保存
- [ ] 首页能切换「我的」/「帮查」显示不同命盘
- [ ] 从命盘详情页能发起匹配并看到结果
- [ ] 分享的卡片不含生辰原始数据
