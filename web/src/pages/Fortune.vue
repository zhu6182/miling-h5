<template>
  <div class="fortune-page container">
    <div class="date-section">
      <span class="date-text">{{ todayDate }}</span>
      <span class="ganzhi-text">{{ dayGanzhi }}</span>
    </div>

    <div v-if="loading" class="loading-section">加载中...</div>

    <div v-else>
      <div class="overall-section">
        <div class="score-circle">
          <span class="score-number">{{ fortune.overall_score }}</span>
          <span class="score-label">综合评分</span>
        </div>
        <span class="phrase">{{ fortune.phrase }}</span>
        <span class="chart-info-text">基于「{{ fortune.chart_name || '我的星盘' }}」星盘分析</span>
      </div>

      <div class="dimension-section">
        <div class="section-title">运势维度</div>
        <div class="dimension-item">
          <span class="dimension-icon">❤️</span>
          <span class="dimension-label">爱情</span>
          <div class="score-bar">
            <div class="score-fill love" :style="{ width: fortune.love_score + '%' }"></div>
          </div>
          <span class="dimension-score">{{ fortune.love_score }}</span>
        </div>
        <div class="dimension-item">
          <span class="dimension-icon">💼</span>
          <span class="dimension-label">事业</span>
          <div class="score-bar">
            <div class="score-fill career" :style="{ width: fortune.career_score + '%' }"></div>
          </div>
          <span class="dimension-score">{{ fortune.career_score }}</span>
        </div>
        <div class="dimension-item">
          <span class="dimension-icon">💰</span>
          <span class="dimension-label">财运</span>
          <div class="score-bar">
            <div class="score-fill wealth" :style="{ width: fortune.wealth_score + '%' }"></div>
          </div>
          <span class="dimension-score">{{ fortune.wealth_score }}</span>
        </div>
        <div class="dimension-item">
          <span class="dimension-icon">💪</span>
          <span class="dimension-label">健康</span>
          <div class="score-bar">
            <div class="score-fill health" :style="{ width: fortune.health_score + '%' }"></div>
          </div>
          <span class="dimension-score">{{ fortune.health_score }}</span>
        </div>
      </div>

      <div class="yiji-section">
        <div class="yi-box">
          <span class="yiji-title">今日推荐</span>
          <div class="yiji-list">
            <span v-for="item in fortune.do_list" :key="item" class="yi-item">{{ item }}</span>
          </div>
        </div>
        <div class="ji-box">
          <span class="yiji-title">今日注意</span>
          <div class="yiji-list">
            <span v-for="item in fortune.avoid_list" :key="item" class="ji-item">{{ item }}</span>
          </div>
        </div>
      </div>

      <div class="lucky-section">
        <div class="lucky-item">
          <span class="lucky-icon">🎨</span>
          <span class="lucky-label">幸运颜色</span>
          <span class="lucky-value">{{ fortune.lucky_color }}</span>
        </div>
        <div class="lucky-item">
          <span class="lucky-icon">🔢</span>
          <span class="lucky-label">幸运数字</span>
          <span class="lucky-value">{{ fortune.lucky_number }}</span>
        </div>
        <div class="lucky-item">
          <span class="lucky-icon">🧭</span>
          <span class="lucky-label">幸运方位</span>
          <span class="lucky-value">{{ fortune.lucky_direction }}</span>
        </div>
      </div>

      <div class="checkin-section">
        <div class="checkin-header">
          <span class="checkin-title">每日签到</span>
          <div class="checkin-stats">
            <span class="stat-item">连续 {{ checkinStatus.checkin_days }} 天</span>
            <span class="stat-item">累计 {{ checkinStatus.checkin_total }} 天</span>
          </div>
        </div>
        <button 
          class="checkin-btn" 
          :class="{ disabled: checkinStatus.has_checkin_today }"
          :disabled="checkinStatus.has_checkin_today"
          @click="doCheckin"
        >
          {{ checkinStatus.has_checkin_today ? '今日已签到' : '立即签到' }}
        </button>
        <div v-if="checkinReward" class="reward-tip">{{ checkinReward }}</div>
      </div>

      <button class="share-btn" @click="share">分享今日运势</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { request } from '@/utils/request'

const loading = ref(true)
const todayDate = ref('')
const dayGanzhi = ref('')
const fortune = ref({
  overall_score: 0,
  love_score: 0,
  career_score: 0,
  wealth_score: 0,
  health_score: 0,
  lucky_color: '',
  lucky_number: '',
  lucky_direction: '',
  do_list: [],
  avoid_list: [],
  phrase: '',
  chart_name: ''
})
const checkinStatus = ref({
  has_checkin_today: false,
  checkin_days: 0,
  checkin_total: 0
})
const checkinReward = ref('')

function formatTodayDate() {
  const today = new Date()
  const year = today.getFullYear()
  const month = today.getMonth() + 1
  const day = today.getDate()
  const weekdays = ['日', '一', '二', '三', '四', '五', '六']
  const weekday = weekdays[today.getDay()]
  todayDate.value = `${year}年${month}月${day}日 星期${weekday}`
}

async function loadFortune() {
  try {
    const res = await request.get('/fortune/today')
    fortune.value = res
    dayGanzhi.value = res.day_ganzhi || ''
  } catch (e) {
    console.error('加载运势失败', e)
  } finally {
    loading.value = false
  }
}

async function loadCheckinStatus() {
  try {
    const res = await request.get('/fortune/checkin/status')
    checkinStatus.value = res
  } catch (e) {
    console.error('加载签到状态失败', e)
  }
}

async function doCheckin() {
  if (checkinStatus.value.has_checkin_today) return
  try {
    const res = await request.post('/fortune/checkin')
    if (res.success) {
      checkinStatus.value = {
        has_checkin_today: true,
        checkin_days: res.checkin_days,
        checkin_total: res.checkin_total
      }
      checkinReward.value = res.reward || ''
      alert('签到成功')
    } else {
      alert(res.message || '已签到')
    }
  } catch (e) {
    console.error('签到失败', e)
    alert('签到失败')
  }
}

function share() {
  if (navigator.share) {
    navigator.share({
      title: `今日运势 ${fortune.value.overall_score}分 - ${fortune.value.phrase}`,
      text: `今日运势 ${fortune.value.overall_score}分`,
      url: window.location.href
    })
  } else {
    alert('请复制链接分享')
  }
}

onMounted(() => {
  formatTodayDate()
  loadFortune()
  loadCheckinStatus()
})
</script>

<style scoped>
.fortune-page {
  padding: 32rpx;
}

.date-section {
  text-align: center;
  margin-bottom: 40rpx;
}

.date-text {
  display: block;
  font-size: 28rpx;
  color: #8888a0;
}

.ganzhi-text {
  display: block;
  font-size: 24rpx;
  color: #666680;
  margin-top: 8rpx;
}

.loading-section {
  text-align: center;
  padding: 80rpx 0;
  color: #8888a0;
}

.overall-section {
  text-align: center;
  margin-bottom: 40rpx;
}

.score-circle {
  width: 240rpx;
  height: 240rpx;
  border-radius: 50%;
  border: 8rpx solid #c9a050;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin: 0 auto 24rpx;
  background: radial-gradient(circle, rgba(201, 160, 80, 0.1) 0%, transparent 70%);
}

.score-number {
  font-size: 80rpx;
  font-weight: 700;
  color: #c9a050;
}

.score-label {
  font-size: 24rpx;
  color: #8888a0;
  margin-top: 8rpx;
}

.phrase {
  display: block;
  font-size: 30rpx;
  color: #e0e0f0;
  margin-bottom: 12rpx;
  line-height: 1.6;
}

.chart-info-text {
  font-size: 24rpx;
  color: #666680;
}

.dimension-section {
  margin-bottom: 32rpx;
}

.dimension-item {
  display: flex;
  align-items: center;
  gap: 20rpx;
  margin-bottom: 20rpx;
}

.dimension-icon {
  font-size: 36rpx;
  width: 48rpx;
}

.dimension-label {
  font-size: 26rpx;
  color: #e0e0f0;
  width: 80rpx;
}

.score-bar {
  flex: 1;
  height: 16rpx;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8rpx;
  overflow: hidden;
}

.score-fill {
  height: 100%;
  border-radius: 8rpx;
  transition: width 0.5s ease;
}

.score-fill.love { background: linear-gradient(90deg, #ff6b9d, #ff8e9e); }
.score-fill.career { background: linear-gradient(90deg, #4facfe, #00f2fe); }
.score-fill.wealth { background: linear-gradient(90deg, #ffd700, #ffb347); }
.score-fill.health { background: linear-gradient(90deg, #43e97b, #38f9d7); }

.dimension-score {
  font-size: 28rpx;
  font-weight: 600;
  color: #c9a050;
  width: 60rpx;
  text-align: right;
}

.yiji-section {
  display: flex;
  gap: 20rpx;
  margin-bottom: 32rpx;
}

.yi-box, .ji-box {
  flex: 1;
  background: rgba(20, 20, 45, 0.8);
  border-radius: 20rpx;
  padding: 24rpx;
}

.yiji-title {
  display: block;
  font-size: 28rpx;
  font-weight: 600;
  margin-bottom: 16rpx;
  text-align: center;
}

.yi-box .yiji-title { color: #4caf50; }
.ji-box .yiji-title { color: #f44336; }

.yiji-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
  justify-content: center;
}

.yi-item, .ji-item {
  font-size: 24rpx;
  padding: 8rpx 16rpx;
  border-radius: 20rpx;
}

.yi-item {
  background: rgba(76, 175, 80, 0.15);
  color: #4caf50;
}

.ji-item {
  background: rgba(244, 67, 54, 0.15);
  color: #f44336;
}

.lucky-section {
  display: flex;
  gap: 20rpx;
  margin-bottom: 32rpx;
}

.lucky-item {
  flex: 1;
  background: rgba(20, 20, 45, 0.8);
  border-radius: 20rpx;
  padding: 24rpx;
  text-align: center;
}

.lucky-icon {
  font-size: 36rpx;
  display: block;
  margin-bottom: 8rpx;
}

.lucky-label {
  font-size: 22rpx;
  color: #8888a0;
  display: block;
  margin-bottom: 8rpx;
}

.lucky-value {
  font-size: 26rpx;
  color: #c9a050;
  font-weight: 600;
}

.checkin-section {
  background: rgba(20, 20, 45, 0.8);
  border-radius: 20rpx;
  padding: 32rpx;
  margin-bottom: 24rpx;
}

.checkin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24rpx;
}

.checkin-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #e0e0f0;
}

.checkin-stats {
  display: flex;
  gap: 20rpx;
}

.stat-item {
  font-size: 24rpx;
  color: #8888a0;
}

.checkin-btn {
  width: 100%;
  padding: 24rpx;
  border: none;
  border-radius: 50rpx;
  font-size: 30rpx;
  font-weight: 600;
  cursor: pointer;
}

.checkin-btn:not(.disabled) {
  background: linear-gradient(135deg, #c9a050 0%, #e0b868 100%);
  color: #1a1a2e;
}

.checkin-btn.disabled {
  background: rgba(255, 255, 255, 0.1);
  color: #666680;
}

.reward-tip {
  margin-top: 16rpx;
  text-align: center;
  font-size: 24rpx;
  color: #c9a050;
}

.share-btn {
  width: 100%;
  padding: 24rpx;
  background: transparent;
  border: 1rpx solid rgba(201, 160, 80, 0.5);
  color: #c9a050;
  border-radius: 50rpx;
  font-size: 28rpx;
  cursor: pointer;
}
</style>
