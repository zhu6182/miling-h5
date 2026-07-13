# 付费功能开发计划

## 场景一：AI深度解读付费

### 方案选择
- **激励视频广告**：用户看完广告可解锁一次AI解读
- **直接付费**：微信支付（可选后续扩展）

### 后端改动
1. `Chart` 模型增加字段：`reading_unlocked`（默认True，即首次免费）
2. `/charts/{id}/reading` 接口：
   - 检查 `reading_unlocked` 状态
   - 锁定时返回 `{ locked: true, message: "请看完广告解锁AI解读" }`
   - 解锁后生成解读，可选重新锁定

### 前端改动
1. `chart-detail.js`：
   - `loadChart()` 检查 `reading_unlocked` 字段
   - `generateReading()` 检查 `readingLocked` 状态
   - 新增 `watchAdToUnlockReading()` 方法
2. `chart-detail.wxml`：按钮文字根据状态变化
3. 集成微信激励视频广告 `wx.createRewardedVideoAd`

---

## 场景二：扫码匹配看结果需看广告

### 后端改动
1. `MatchRecord` 增加字段：`result_unlocked`（默认True，即首次免费）
2. `/match/{id}` 接口：
   - 锁定时返回 `{ locked: true, message: "请看完广告解锁完整匹配结果" }`
   - 不返回 `match_data`
3. 新增 `/match/{id}/unlock` 接口：解锁匹配结果

### 前端改动
1. `match-result.js`：
   - `loadMatchResult()` 检查 `locked` 字段
   - 新增 `watchAdToUnlockMatch()` 方法
   - 新增 `unlockMatchResult()` 方法
2. `match-result.wxml`：添加锁定状态UI（🔒图标 + 解锁按钮）
3. `match-result.wxss`：添加锁定状态样式

---

## 广告集成技术点

微信激励视频广告：
```javascript
const rewardedVideoAd = wx.createRewardedVideoAd({
  adUnitId: 'xxxxxxxx' // 需替换为实际的广告位ID
})
rewardedVideoAd.onClose((res) => {
  if (res.isEnded) {
    // 用户完整观看，解锁内容
  }
})
rewardedVideoAd.show()
```

---

## 实施步骤

### Step 1: 后端 - Chart模型增加字段 ✅
- [x] 添加 `reading_unlocked` 字段（默认True）
- [x] 修改 `/charts/{id}/reading` 校验逻辑

### Step 2: 后端 - MatchRecord增加字段 ✅
- [x] 添加 `result_unlocked` 字段（默认True）
- [x] 修改 `/match/{id}` 返回锁定状态
- [x] 添加 `/match/{id}/unlock` 接口

### Step 3: 前端 - chart-detail广告集成 ✅
- [x] 集成激励视频广告
- [x] 修改 generateReading() 逻辑
- [x] 修改 wxml 按钮文字

### Step 4: 前端 - match-result广告集成 ✅
- [x] 检测解锁状态
- [x] 集成激励视频广告
- [x] 添加解锁按钮UI
- [x] 调用解锁接口

---

## 注意事项

1. **广告位ID**：前端代码中的 `adUnitId: 'xxxxxxxx'` 需要替换为实际的微信广告位ID
2. **测试环境**：广告功能在开发者工具中可能无法正常显示，需要真机测试
3. **默认免费**：新创建的命盘和匹配记录默认是解锁状态（`reading_unlocked=True`, `result_unlocked=True`）
4. **永久解锁**：生成解读或解锁匹配后，可以选择永久解锁或每次重新锁定
