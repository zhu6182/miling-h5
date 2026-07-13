<template>
  <div class="page-container">
    <div class="star-field" ref="starField"></div>

    <div class="date-section">
      <div class="date-card">
        <div class="date-left">
          <span class="date-day">{{ todayDay }}</span>
          <span class="date-month">{{ todayMonth }}</span>
        </div>
        <div class="date-right">
          <span class="ganzhi-text">{{ dayGanzhi }}</span>
          <span class="week-text">{{ todayWeek }}</span>
        </div>
        <div class="date-glow"></div>
      </div>
    </div>

    <div v-if="loading" class="loading-section">
      <div class="loading-spinner">
        <span class="spinner-ring"></span>
        <span class="spinner-ring-second"></span>
        <span class="spinner-core">☯</span>
      </div>
      <p class="loading-text">正在排盘测算...</p>
    </div>

    <div v-else class="fortune-content">
      <div class="overall-section">
        <div class="score-circle">
          <div class="circle-ring">
            <div class="circle-progress" :style="{ '--progress': fortune.overall_score / 100 }"></div>
            <div class="circle-inner">
              <span class="score-number">{{ fortune.overall_score }}</span>
              <span class="score-label">运势指数</span>
            </div>
          </div>
          <div class="score-glow"></div>
          <div class="score-glow-secondary"></div>
        </div>
        <div class="score-tags">
          <span class="score-tag">{{ getScoreLevel(fortune.overall_score) }}</span>
          <span class="score-tag secondary">{{ fortune.lucky_color }}</span>
        </div>
      </div>

      <div class="dimensions-section">
        <h3 class="section-title">
          <span class="title-icon">☯</span>
          运势维度
        </h3>
        <div class="dimensions-grid">
          <div class="dimension-card" v-for="dim in dimensions" :key="dim.name">
            <div class="dim-header">
              <span class="dim-icon">{{ dim.icon }}</span>
              <span class="dim-name">{{ dim.name }}</span>
            </div>
            <div class="dim-bar-container">
              <div class="dim-bar-track">
                <div class="dim-bar-fill" :class="dim.color" :style="{ width: dim.value + '%' }"></div>
              </div>
              <span class="dim-value">{{ dim.value }}%</span>
            </div>
            <div class="dim-glow" :class="dim.color"></div>
          </div>
        </div>
      </div>

      <div class="tips-section">
        <div class="tips-row">
          <div class="tips-card good">
            <div class="tips-header">
              <span class="tips-icon">✓</span>
              <span class="tips-title">宜</span>
            </div>
            <div class="tips-list">
              <span class="tip-item" v-for="item in fortune.do_list" :key="item">{{ item }}</span>
            </div>
            <div class="card-corner"></div>
          </div>
          <div class="tips-card bad">
            <div class="tips-header">
              <span class="tips-icon">✕</span>
              <span class="tips-title">忌</span>
            </div>
            <div class="tips-list">
              <span class="tip-item" v-for="item in fortune.avoid_list" :key="item">{{ item }}</span>
            </div>
            <div class="card-corner"></div>
          </div>
        </div>
      </div>

      <div class="detail-section">
        <h3 class="section-title">
          <span class="title-icon">📖</span>
          命理详解
        </h3>
        <div class="detail-card">
          <div class="detail-item" v-for="(item, index) in detailItems" :key="index">
            <span class="detail-label">{{ item.label }}</span>
            <span v-if="item.type === 'color'" class="detail-value">
              <span class="color-box" :style="{ background: item.value }"></span>
              <span class="detail-text">{{ item.text }}</span>
            </span>
            <span v-else class="detail-value">{{ item.value }}</span>
          </div>
        </div>
      </div>

      <div class="analysis-section">
        <h3 class="section-title">
          <span class="title-icon">☯</span>
          今日运势
        </h3>
        <div class="analysis-card">
          <div class="card-decoration"></div>
          <p class="analysis-text">{{ fortune.phrase }}</p>
        </div>
      </div>

      <div class="footer-section">
        <button class="refresh-btn" @click="loadFortune">
          <span class="refresh-icon">🔄</span>
          <span>重新测算</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onActivated, computed } from 'vue'
import { request } from '@/utils/request'

const starField = ref(null)
const loading = ref(true)
const fortune = ref({
  overall_score: 78,
  love_score: 85,
  career_score: 72,
  wealth_score: 70,
  health_score: 82,
  lucky_color: '#d4af37',
  lucky_number: '8',
  lucky_direction: '东方',
  do_list: ['出行游玩', '约会社交', '学习提升'],
  avoid_list: ['冲动消费', '与人争执'],
  phrase: '今日命理运势平稳上升，贵人相助。适合开展新计划和社交活动，情感方面会有意外惊喜。'
})

const todayDay = computed(() => new Date().getDate())
const todayMonth = computed(() => `${new Date().getMonth() + 1}月`)
const todayWeek = computed(() => {
  const weeks = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  return weeks[new Date().getDay()]
})

const dayGanzhi = ref('')

const dimensions = computed(() => [
  { name: '爱情', value: fortune.value.love_score, icon: '❤️', color: 'love' },
  { name: '事业', value: fortune.value.career_score, icon: '💼', color: 'career' },
  { name: '财运', value: fortune.value.wealth_score, icon: '💰', color: 'wealth' },
  { name: '健康', value: fortune.value.health_score, icon: '💪', color: 'health' }
])

const detailItems = computed(() => [
  { label: '幸运色', type: 'color', value: getColorHex(fortune.value.lucky_color), text: fortune.value.lucky_color },
  { label: '幸运数字', type: 'text', value: fortune.value.lucky_number },
  { label: '幸运方位', type: 'text', value: fortune.value.lucky_direction }
])

function getColorHex(name) {
  const map = {
    '白色': '#ffffff', '银色': '#c0c0c0', '金色': '#d4af37',
    '绿色': '#50c878', '青色': '#00cccc', '翠色': '#3eb370',
    '蓝色': '#4a90d9', '黑色': '#333333', '灰色': '#888888',
    '红色': '#e06060', '橙色': '#ff8c00', '粉色': '#ff90a0',
    '黄色': '#fbbf24', '棕色': '#8b4513', '咖啡色': '#6f4e37'
  }
  return map[name] || '#d4af37'
}

async function loadFortune() {
  loading.value = true
  try {
    const res = await request.get('/fortune/today')
    fortune.value = res
    // 设置干支日历
    if (res.year_ganzhi && res.month_ganzhi && res.day_ganzhi) {
      dayGanzhi.value = `${res.year_ganzhi} · ${res.month_ganzhi} · ${res.day_ganzhi}`
    }
  } catch (e) {
    console.error('获取运势失败', e)
  } finally {
    loading.value = false
  }
}

function getScoreLevel(score) {
  if (score >= 90) return '大吉'
  if (score >= 80) return '吉'
  if (score >= 70) return '中吉'
  if (score >= 60) return '平'
  return '小凶'
}

function initStars() {
  if (!starField.value) return
  const container = starField.value
  const starCount = 50
  
  for (let i = 0; i < starCount; i++) {
    const star = document.createElement('div')
    star.className = 'star'
    star.style.left = Math.random() * 100 + '%'
    star.style.top = Math.random() * 100 + '%'
    star.style.width = Math.random() * 2 + 1 + 'px'
    star.style.height = star.style.width
    star.style.opacity = Math.random() * 0.5 + 0.2
    star.style.animationDelay = Math.random() * 3 + 's'
    container.appendChild(star)
  }
}

onMounted(() => {
  initStars()
  loadFortune()
})

onActivated(() => {
  loadFortune()
})
</script>

<style scoped>
.star-field {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 0;
}

.star {
  position: absolute;
  background: white;
  border-radius: 50%;
  animation: twinkle 3s ease-in-out infinite;
}

@keyframes twinkle {
  0%, 100% { opacity: 0.2; transform: scale(1); }
  50% { opacity: 0.8; transform: scale(1.2); }
}

.date-section {
  padding: 32px 24px;
}

.date-card {
  background: rgba(18, 18, 35, 0.7);
  border: 1px solid rgba(212, 175, 55, 0.15);
  border-radius: 20px;
  padding: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  backdrop-filter: blur(20px);
  position: relative;
  overflow: hidden;
}

.date-glow {
  position: absolute;
  top: -50%;
  right: -50%;
  width: 150%;
  height: 150%;
  background: radial-gradient(circle at 70% 30%, rgba(139, 92, 246, 0.08) 0%, transparent 50%);
  pointer-events: none;
}

.date-left {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.date-day {
  font-family: 'Cinzel', serif;
  font-size: 52px;
  font-weight: 700;
  background: linear-gradient(135deg, var(--gold-primary), var(--gold-secondary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.date-month {
  font-size: 18px;
  color: var(--text-muted);
}

.date-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
}

.ganzhi-text {
  font-size: 16px;
  color: var(--gold-primary);
  font-family: 'Noto Serif SC', serif;
}

.week-text {
  font-size: 14px;
  color: var(--text-muted);
}

.loading-section {
  text-align: center;
  padding: 80px 0;
}

.loading-spinner {
  position: relative;
  width: 120px;
  height: 120px;
  margin: 0 auto 24px;
}

.spinner-ring {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border: 3px solid rgba(212, 175, 55, 0.1);
  border-top-color: var(--gold-primary);
  border-radius: 50%;
  animation: spin 2s linear infinite;
}

.spinner-ring-second {
  position: absolute;
  top: 8px;
  left: 8px;
  right: 8px;
  bottom: 8px;
  border: 2px solid rgba(139, 92, 246, 0.1);
  border-bottom-color: var(--purple-primary);
  border-radius: 50%;
  animation: spin 1.5s linear infinite reverse;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.spinner-core {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 48px;
  animation: float 2s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translate(-50%, -50%) translateY(0); }
  50% { transform: translate(-50%, -50%) translateY(-8px); }
}

.loading-text {
  font-size: 16px;
  color: var(--text-muted);
}

.fortune-content {
  padding: 0 24px;
}

.overall-section {
  text-align: center;
  padding: 40px 0;
}

.score-circle {
  position: relative;
  width: 220px;
  height: 220px;
  margin: 0 auto;
}

.circle-ring {
  position: relative;
  width: 100%;
  height: 100%;
}

.circle-progress {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: conic-gradient(
    var(--gold-primary) calc(var(--progress) * 360deg),
    rgba(212, 175, 55, 0.1) calc(var(--progress) * 360deg)
  );
  mask: radial-gradient(farthest-side, transparent calc(100% - 14px), #fff calc(100% - 14px));
  -webkit-mask: radial-gradient(farthest-side, transparent calc(100% - 14px), #fff calc(100% - 14px));
}

.circle-inner {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 160px;
  height: 160px;
  background: rgba(10, 10, 21, 0.95);
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(212, 175, 55, 0.1);
}

.score-number {
  font-family: 'Cinzel', serif;
  font-size: 60px;
  font-weight: 700;
  background: linear-gradient(135deg, var(--gold-primary), var(--gold-secondary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.score-label {
  font-size: 14px;
  color: var(--text-muted);
  margin-top: 4px;
}

.score-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(212, 175, 55, 0.15) 0%, transparent 70%);
  border-radius: 50%;
  animation: pulse-glow 2s ease-in-out infinite;
}

.score-glow-secondary {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 180px;
  height: 180px;
  background: radial-gradient(circle, rgba(139, 92, 246, 0.08) 0%, transparent 60%);
  border-radius: 50%;
  animation: pulse-glow 3s ease-in-out infinite reverse;
}

@keyframes pulse-glow {
  0%, 100% { opacity: 0.5; transform: translate(-50%, -50%) scale(1); }
  50% { opacity: 1; transform: translate(-50%, -50%) scale(1.05); }
}

.score-tags {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-top: 24px;
}

.score-tag {
  font-size: 14px;
  padding: 6px 20px;
  background: rgba(212, 175, 55, 0.15);
  color: var(--gold-primary);
  border-radius: 20px;
  border: 1px solid rgba(212, 175, 55, 0.3);
}

.score-tag.secondary {
  background: rgba(139, 92, 246, 0.1);
  color: var(--purple-secondary);
  border-color: rgba(139, 92, 246, 0.3);
}

.dimensions-section {
  margin-bottom: 32px;
}

.section-title {
  font-family: 'Cinzel', serif;
  font-size: 19px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 18px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.title-icon {
  color: var(--gold-primary);
}

.dimensions-grid {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.dimension-card {
  background: rgba(18, 18, 35, 0.6);
  border: 1px solid rgba(212, 175, 55, 0.1);
  border-radius: 16px;
  padding: 20px;
  position: relative;
  overflow: hidden;
}

.dim-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
}

.dim-icon {
  font-size: 22px;
}

.dim-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.dim-bar-container {
  display: flex;
  align-items: center;
  gap: 12px;
}

.dim-bar-track {
  flex: 1;
  height: 8px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 4px;
  overflow: hidden;
  position: relative;
}

.dim-bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.8s ease;
  position: relative;
}

.dim-bar-fill::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 50%;
  background: linear-gradient(180deg, rgba(255,255,255,0.2), transparent);
  border-radius: 4px 4px 0 0;
}

.dim-bar-fill.love { background: linear-gradient(90deg, #e06060, #ff8080); }
.dim-bar-fill.career { background: linear-gradient(90deg, #6090c8, #80b0e0); }
.dim-bar-fill.wealth { background: linear-gradient(90deg, var(--gold-primary), var(--gold-secondary)); }
.dim-bar-fill.health { background: linear-gradient(90deg, #50c878, #80e098); }

.dim-value {
  font-size: 14px;
  color: var(--gold-primary);
  font-weight: 600;
  width: 48px;
  text-align: right;
}

.dim-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.dimension-card:hover .dim-glow {
  opacity: 0.5;
}

.dim-glow.love { background: linear-gradient(90deg, #e06060, #ff8080); }
.dim-glow.career { background: linear-gradient(90deg, #6090c8, #80b0e0); }
.dim-glow.wealth { background: linear-gradient(90deg, var(--gold-primary), var(--gold-secondary)); }
.dim-glow.health { background: linear-gradient(90deg, #50c878, #80e098); }

.tips-section {
  margin-bottom: 32px;
}

.tips-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
}

.tips-card {
  background: rgba(18, 18, 35, 0.6);
  border-radius: 16px;
  padding: 20px;
  position: relative;
  overflow: hidden;
}

.tips-card.good {
  border: 1px solid rgba(80, 200, 120, 0.15);
}

.tips-card.bad {
  border: 1px solid rgba(224, 96, 96, 0.15);
}

.card-corner {
  position: absolute;
  top: 0;
  right: 0;
  width: 60px;
  height: 60px;
  border-right: 2px solid rgba(212, 175, 55, 0.1);
  border-top: 2px solid rgba(212, 175, 55, 0.1);
  border-radius: 0 16px 0 0;
}

.tips-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 14px;
}

.tips-card.good .tips-icon {
  color: #50c878;
}

.tips-card.bad .tips-icon {
  color: #e06060;
}

.tips-icon {
  font-size: 18px;
}

.tips-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.tips-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tip-item {
  font-size: 13px;
  padding: 6px 12px;
  border-radius: 12px;
}

.tips-card.good .tip-item {
  background: rgba(80, 200, 120, 0.08);
  color: #80e098;
}

.tips-card.bad .tip-item {
  background: rgba(224, 96, 96, 0.08);
  color: #ff8080;
}

.detail-section {
  margin-bottom: 32px;
}

.detail-card {
  background: rgba(18, 18, 35, 0.6);
  border: 1px solid rgba(212, 175, 55, 0.1);
  border-radius: 16px;
  padding: 8px 0;
}

.detail-item {
  display: flex;
  align-items: center;
  padding: 16px 20px;
  gap: 12px;
  border-bottom: 1px solid rgba(212, 175, 55, 0.06);
}

.detail-item:last-child {
  border-bottom: none;
}

.detail-label {
  font-size: 14px;
  color: var(--text-muted);
  width: 72px;
}

.detail-value {
  font-size: 16px;
  color: var(--gold-primary);
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
}

.color-box {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.detail-text {
  font-size: 16px;
  color: var(--text-primary);
}

.analysis-section {
  margin-bottom: 40px;
}

.analysis-card {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.08) 0%, rgba(59, 130, 246, 0.04) 50%, rgba(212, 175, 55, 0.04) 100%);
  border: 1px solid rgba(139, 92, 246, 0.1);
  border-radius: 16px;
  padding: 24px;
  position: relative;
}

.card-decoration {
  position: absolute;
  top: 12px;
  left: 12px;
  width: 24px;
  height: 24px;
  border-left: 2px solid rgba(212, 175, 55, 0.3);
  border-top: 2px solid rgba(212, 175, 55, 0.3);
}

.card-decoration::after {
  content: '';
  position: absolute;
  bottom: -26px;
  right: -26px;
  width: 24px;
  height: 24px;
  border-right: 2px solid rgba(212, 175, 55, 0.3);
  border-bottom: 2px solid rgba(212, 175, 55, 0.3);
}

.analysis-text {
  font-size: 16px;
  line-height: 1.8;
  color: var(--text-secondary);
  margin: 0;
  text-indent: 2em;
}

.footer-section {
  text-align: center;
  padding-bottom: 40px;
}

.refresh-btn {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  background: transparent;
  border: 1px solid rgba(212, 175, 55, 0.3);
  color: var(--gold-primary);
  border-radius: 24px;
  padding: 14px 32px;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.refresh-btn:hover {
  background: rgba(212, 175, 55, 0.1);
  box-shadow: 0 0 20px rgba(212, 175, 55, 0.2);
}

.refresh-icon {
  font-size: 18px;
}
</style>