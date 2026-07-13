<template>
  <div class="page-container">
    <div class="header">
      <button class="back-btn" @click="goBack">←</button>
      <span class="header-title">人生K线</span>
      <span class="header-placeholder"></span>
    </div>

    <!-- 加载中 -->
    <div v-if="loading" class="loading-section">
      <div class="loading-spinner">
        <span class="spinner-ring"></span>
        <span class="spinner-ring-second"></span>
        <span class="spinner-core">📈</span>
      </div>
      <p class="loading-text">{{ loadingText }}</p>
    </div>

    <!-- 错误提示 -->
    <div v-else-if="error" class="error-section">
      <p class="error-text">{{ error }}</p>
      <button class="retry-btn" @click="startKline">重新生成</button>
    </div>

    <!-- 数据展示 -->
    <div v-else-if="klineData" class="kline-content">
      <!-- 八字四柱 -->
      <div class="bazi-card">
        <div class="bazi-title">八字四柱</div>
        <div class="bazi-pillars">
          <div class="pillar" v-for="(gz, i) in klineData.bazi" :key="i">
            <span class="pillar-label">{{ pillarNames[i] }}</span>
            <span class="pillar-gz" :class="pillarClass(gz)">{{ gz }}</span>
          </div>
        </div>
      </div>

      <!-- K线图 -->
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-icon">📈</span>
          <span class="chart-title">运势走势</span>
          <span class="chart-tip">长按查看详情</span>
        </div>
        <div class="chart-wrapper" ref="chartWrapper">
          <canvas ref="canvas" @touchstart="onTouchStart" @touchmove="onTouchMove" @touchend="onTouchEnd"></canvas>
        </div>
        <div v-if="hoverPoint" class="tooltip" :style="tooltipStyle">
          <div class="tooltip-age">{{ hoverPoint.age }}岁 · {{ hoverPoint.year }}年</div>
          <div class="tooltip-ganzhi">{{ hoverPoint.ganZhi }} · {{ hoverPoint.daYun }}</div>
          <div class="tooltip-score">运势 {{ hoverPoint.score }}</div>
          <div class="tooltip-ohlc">开{{ hoverPoint.open }} 高{{ hoverPoint.high }} 低{{ hoverPoint.low }} 收{{ hoverPoint.close }}</div>
          <div class="tooltip-reason">{{ hoverPoint.reason }}</div>
        </div>
      </div>

      <!-- 七维度分析 -->
      <div class="analysis-card">
        <h3 class="section-title"><span class="title-icon">☯</span>命理分析</h3>
        <div class="summary-row">
          <div class="summary-score" :style="scoreStyle(klineData.summaryScore)">{{ klineData.summaryScore }}</div>
          <p class="summary-text">{{ klineData.summary }}</p>
        </div>
        <div class="dim-grid">
          <div class="dim-item" v-for="dim in dimensions" :key="dim.key">
            <div class="dim-header">
              <span class="dim-icon">{{ dim.icon }}</span>
              <span class="dim-name">{{ dim.name }}</span>
              <span class="dim-score" :style="scoreStyle(klineData[dim.scoreKey])">{{ klineData[dim.scoreKey] }}</span>
            </div>
            <p class="dim-text">{{ klineData[dim.key] }}</p>
          </div>
        </div>
      </div>

      <!-- 大运解读 -->
      <div class="dayun-section">
        <h3 class="section-title"><span class="title-icon">🌀</span>大运走势</h3>
        <div class="dayun-list">
          <div class="dayun-item" v-for="(dy, i) in klineData.dayunAnalysis" :key="i" :class="dayunClass(dy.score)">
            <div class="dayun-header">
              <span class="dayun-age">{{ dy.start_age }}-{{ dy.end_age }}岁</span>
              <span class="dayun-gz">{{ dy.ganzhi }}</span>
              <span class="dayun-trend">{{ dy.trend_desc }}</span>
              <span class="dayun-score">{{ dy.score }}</span>
            </div>
            <div class="dayun-shen">
              <span class="shen-tag">{{ dy.gan_shen }}</span>
              <span class="shen-tag">{{ dy.zhi_shen }}</span>
              <span class="shen-wx">{{ dy.gan_wx }}·{{ dy.zhi_wx }}</span>
            </div>
            <div class="dayun-points" v-if="dy.key_points && dy.key_points.length">
              <span class="point-tag" v-for="(p, j) in dy.key_points" :key="j">{{ p }}</span>
            </div>
            <div class="dayun-avg" v-if="dy.avg_score">均分 {{ dy.avg_score }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { request } from '@/utils/request'

const router = useRouter()
const route = useRoute()

const loading = ref(true)
const loadingText = ref('正在排盘推演...')
const error = ref('')
const klineData = ref(null)
const canvas = ref(null)
const chartWrapper = ref(null)
const hoverPoint = ref(null)
const tooltipStyle = ref({})
let pollTimer = null

const pillarNames = ['年柱', '月柱', '日柱', '时柱']

const dimensions = [
  { key: 'personality', scoreKey: 'personalityScore', name: '性格', icon: '🎭' },
  { key: 'industry', scoreKey: 'industryScore', name: '事业', icon: '💼' },
  { key: 'wealth', scoreKey: 'wealthScore', name: '财富', icon: '💰' },
  { key: 'marriage', scoreKey: 'marriageScore', name: '婚姻', icon: '❤️' },
  { key: 'health', scoreKey: 'healthScore', name: '健康', icon: '🌿' },
  { key: 'family', scoreKey: 'familyScore', name: '六亲', icon: '👨‍👩‍👧' },
]

function goBack() {
  router.back()
}

function pillarClass(gz) {
  const wxMap = { '甲乙': 'wood', '丙丁': 'fire', '戊己': 'earth', '庚辛': 'metal', '壬癸': 'water' }
  const gan = gz[0]
  for (const k in wxMap) {
    if (k.includes(gan)) return 'wx-' + wxMap[k]
  }
  return ''
}

function scoreStyle(score) {
  if (score >= 75) return { color: '#4ade80', borderColor: '#4ade80' }
  if (score >= 60) return { color: '#d4af37', borderColor: '#d4af37' }
  if (score >= 40) return { color: '#fbbf24', borderColor: '#fbbf24' }
  return { color: '#f87171', borderColor: '#f87171' }
}

function dayunClass(score) {
  if (score >= 75) return 'great'
  if (score >= 60) return 'good'
  if (score >= 40) return 'normal'
  return 'bad'
}

async function startKline() {
  loading.value = true
  error.value = ''
  loadingText.value = '正在获取命盘信息...'

  let params = {
    date_str: route.query.date_str,
    hour_index: Number(route.query.hour_index),
    gender: route.query.gender,
  }
  if (route.query.is_lunar) params.is_lunar = route.query.is_lunar === 'true'
  if (route.query.is_leap) params.is_leap = route.query.is_leap === 'true'

  // 如果没有传入生辰八字参数，从用户默认命盘获取
  if (!params.date_str) {
    try {
      const charts = await request.get('/charts')
      const chart = charts.find(c => c.is_default) || charts[0]
      if (!chart) {
        error.value = '请先创建命盘'
        loading.value = false
        return
      }
      params.date_str = chart.solar_date
      params.hour_index = chart.hour_index
      params.gender = chart.gender
    } catch (e) {
      error.value = '获取命盘信息失败，请先登录'
      loading.value = false
      return
    }
  }

  loadingText.value = '正在排盘推演...'

  try {
    const res = await request.post('/bazi/kline/start', params)
    pollStatus(res.task_id)
  } catch (e) {
    console.error('启动K线生成失败', e)
    error.value = e.response?.data?.detail || '启动失败，请重试'
    loading.value = false
  }
}

async function pollStatus(taskId) {
  let attempts = 0
  pollTimer = setInterval(async () => {
    attempts++
    try {
      const res = await request.get(`/bazi/kline/status/${taskId}`)
      if (res.status === 'completed' && res.result && res.result.kline_data) {
        clearInterval(pollTimer)
        pollTimer = null
        klineData.value = res.result.kline_data
        loading.value = false
        await nextTick()
        drawChart()
      } else if (res.status === 'failed') {
        clearInterval(pollTimer)
        pollTimer = null
        error.value = res.error || '生成失败，请重试'
        loading.value = false
      } else {
        loadingText.value = '正在推演大运流年...'
      }
    } catch (e) {
      console.error('查询状态失败', e)
    }
    if (attempts > 60) {
      clearInterval(pollTimer)
      pollTimer = null
      error.value = '生成超时，请重试'
      loading.value = false
    }
  }, 1000)
}

function drawChart() {
  const cv = canvas.value
  if (!cv || !klineData.value) return

  const wrapper = chartWrapper.value
  const w = wrapper.clientWidth
  const h = 260
  const dpr = window.devicePixelRatio || 1
  cv.width = w * dpr
  cv.height = h * dpr
  cv.style.width = w + 'px'
  cv.style.height = h + 'px'

  const ctx = cv.getContext('2d')
  ctx.scale(dpr, dpr)

  const padding = { left: 36, right: 12, top: 20, bottom: 28 }
  const chartW = w - padding.left - padding.right
  const chartH = h - padding.top - padding.bottom

  const points = klineData.value.chartPoints
  if (!points || points.length === 0) return

  // 价格范围
  let minLow = Infinity, maxHigh = -Infinity
  points.forEach(p => {
    if (p.low < minLow) minLow = p.low
    if (p.high > maxHigh) maxHigh = p.high
  })
  const range = maxHigh - minLow || 1

  const yOf = (val) => padding.top + chartH * (1 - (val - minLow) / range)
  const xOf = (i) => padding.left + (chartW / (points.length - 1)) * i

  // 背景网格
  ctx.strokeStyle = 'rgba(212, 175, 55, 0.06)'
  ctx.lineWidth = 1
  for (let i = 0; i <= 4; i++) {
    const y = padding.top + (chartH / 4) * i
    ctx.beginPath()
    ctx.moveTo(padding.left, y)
    ctx.lineTo(padding.left + chartW, y)
    ctx.stroke()
  }
  // 纵轴标签
  ctx.fillStyle = 'rgba(128, 128, 160, 0.5)'
  ctx.font = '10px sans-serif'
  ctx.textAlign = 'right'
  for (let i = 0; i <= 4; i++) {
    const val = maxHigh - (range / 4) * i
    const y = padding.top + (chartH / 4) * i
    ctx.fillText(Math.round(val), padding.left - 6, y + 3)
  }
  // 横轴标签（每10年）
  ctx.textAlign = 'center'
  for (let i = 0; i < points.length; i += 10) {
    const x = xOf(i)
    ctx.fillText(points[i].age + '岁', x, h - 10)
  }

  // 渐变填充区域（基于收盘价）
  const coords = points.map((p, i) => ({ x: xOf(i), y: yOf(p.close), ...p }))
  const gradient = ctx.createLinearGradient(0, padding.top, 0, padding.top + chartH)
  gradient.addColorStop(0, 'rgba(212, 175, 55, 0.22)')
  gradient.addColorStop(1, 'rgba(212, 175, 55, 0.01)')
  ctx.beginPath()
  ctx.moveTo(coords[0].x, padding.top + chartH)
  coords.forEach(c => ctx.lineTo(c.x, c.y))
  ctx.lineTo(coords[coords.length - 1].x, padding.top + chartH)
  ctx.closePath()
  ctx.fillStyle = gradient
  ctx.fill()

  // OHLC蜡烛图
  const candleW = Math.max(2, (chartW / points.length) * 0.6)
  coords.forEach((c) => {
    const open = c.open, close = c.close, high = c.high, low = c.low
    const isUp = close >= open
    const color = isUp ? '#4ade80' : '#f87171'

    // 影线
    ctx.strokeStyle = color
    ctx.lineWidth = 1
    ctx.beginPath()
    ctx.moveTo(c.x, yOf(high))
    ctx.lineTo(c.x, yOf(low))
    ctx.stroke()

    // 实体
    const bodyTop = yOf(Math.max(open, close))
    const bodyBot = yOf(Math.min(open, close))
    const bodyH = Math.max(1, bodyBot - bodyTop)
    ctx.fillStyle = color
    ctx.fillRect(c.x - candleW / 2, bodyTop, candleW, bodyH)
  })

  // 曲线（收盘价平滑线）
  ctx.beginPath()
  ctx.moveTo(coords[0].x, coords[0].y)
  for (let i = 1; i < coords.length; i++) {
    const prev = coords[i - 1]
    const curr = coords[i]
    const cpx = (prev.x + curr.x) / 2
    ctx.quadraticCurveTo(prev.x, prev.y, cpx, (prev.y + curr.y) / 2)
  }
  ctx.lineTo(coords[coords.length - 1].x, coords[coords.length - 1].y)
  ctx.strokeStyle = 'rgba(212, 175, 55, 0.8)'
  ctx.lineWidth = 1.5
  ctx.stroke()

  // 存储坐标用于触摸交互
  cv._coords = coords
  cv._chartW = w
}

function onTouchStart(e) {
  e.preventDefault()
  handleTouch(e.touches[0])
}
function onTouchMove(e) {
  e.preventDefault()
  handleTouch(e.touches[0])
}
function onTouchEnd() {
  // 保持tooltip
}

function handleTouch(touch) {
  const cv = canvas.value
  if (!cv || !cv._coords) return
  const rect = cv.getBoundingClientRect()
  const x = touch.clientX - rect.left
  let minDist = Infinity
  let nearest = null
  for (const c of cv._coords) {
    const dist = Math.abs(c.x - x)
    if (dist < minDist) {
      minDist = dist
      nearest = c
    }
  }
  if (nearest && minDist < 30) {
    hoverPoint.value = nearest
    const tooltipX = Math.min(nearest.x + 10, cv._chartW - 150)
    const tooltipY = Math.max(nearest.y - 80, 10)
    tooltipStyle.value = { left: tooltipX + 'px', top: tooltipY + 'px' }
  } else {
    hoverPoint.value = null
  }
}

function handleResize() {
  if (klineData.value) drawChart()
}

onMounted(() => {
  startKline()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background: linear-gradient(180deg, #0a0a15 0%, #1a1525 50%, #0a0a15 100%);
  padding-bottom: 60px;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 16px;
  padding-top: calc(20px + env(safe-area-inset-top));
}

.back-btn {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(212, 175, 55, 0.2);
  border-radius: 10px;
  font-size: 18px;
  color: var(--text-primary);
  cursor: pointer;
}

.header-title {
  font-family: 'Cinzel', serif;
  font-size: 17px;
  font-weight: 600;
  color: var(--text-primary);
}

.header-placeholder {
  width: 40px;
}

.loading-section, .error-section {
  text-align: center;
  padding: 100px 20px;
}

.loading-spinner {
  position: relative;
  width: 70px;
  height: 70px;
  margin: 0 auto 20px;
}

.spinner-ring {
  position: absolute;
  width: 100%;
  height: 100%;
  border: 3px solid rgba(212, 175, 55, 0.1);
  border-top-color: var(--gold-primary);
  border-radius: 50%;
  animation: spin 1.5s linear infinite;
}

.spinner-ring-second {
  position: absolute;
  top: 6px; left: 6px; right: 6px; bottom: 6px;
  border: 2px solid rgba(139, 92, 246, 0.1);
  border-bottom-color: var(--purple-primary);
  border-radius: 50%;
  animation: spin 2s linear infinite reverse;
}

.spinner-core {
  position: absolute;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  font-size: 28px;
}

@keyframes spin { to { transform: rotate(360deg); } }

.loading-text {
  font-size: 14px;
  color: var(--text-muted);
}

.error-text {
  font-size: 14px;
  color: #f87171;
  margin-bottom: 16px;
}

.retry-btn {
  padding: 8px 24px;
  background: rgba(212, 175, 55, 0.15);
  border: 1px solid rgba(212, 175, 55, 0.3);
  border-radius: 10px;
  color: var(--gold-primary);
  font-size: 14px;
  cursor: pointer;
}

.kline-content {
  padding: 0 14px;
}

/* 八字四柱 */
.bazi-card {
  background: rgba(139, 92, 246, 0.08);
  border: 1px solid rgba(139, 92, 246, 0.15);
  border-radius: 14px;
  padding: 14px 16px;
  margin-bottom: 14px;
}

.bazi-title {
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 10px;
}

.bazi-pillars {
  display: flex;
  justify-content: space-around;
}

.pillar {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.pillar-label {
  font-size: 11px;
  color: var(--text-muted);
}

.pillar-gz {
  font-size: 18px;
  font-weight: 700;
  font-family: 'KaiTi', 'STKaiti', serif;
}

.wx-wood { color: #4ade80; }
.wx-fire { color: #f87171; }
.wx-earth { color: #fbbf24; }
.wx-metal { color: #e0e0e0; }
.wx-water { color: #60a5fa; }

/* K线图 */
.chart-card {
  background: rgba(18, 18, 35, 0.6);
  border: 1px solid rgba(212, 175, 55, 0.1);
  border-radius: 14px;
  padding: 14px;
  margin-bottom: 14px;
  position: relative;
}

.chart-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.chart-icon { font-size: 16px; }
.chart-title { font-size: 15px; font-weight: 600; color: var(--text-primary); }
.chart-tip { font-size: 11px; color: var(--text-muted); margin-left: auto; }

.chart-wrapper {
  position: relative;
  width: 100%;
  overflow: hidden;
}

.chart-wrapper canvas {
  display: block;
  touch-action: none;
}

.tooltip {
  position: absolute;
  background: rgba(10, 10, 21, 0.95);
  border: 1px solid rgba(212, 175, 55, 0.3);
  border-radius: 10px;
  padding: 8px 12px;
  min-width: 130px;
  max-width: 180px;
  z-index: 10;
  pointer-events: none;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
}

.tooltip-age { font-size: 13px; font-weight: 600; color: var(--text-primary); }
.tooltip-ganzhi { font-size: 11px; color: var(--purple-secondary); margin-top: 2px; }
.tooltip-score { font-size: 15px; font-weight: 700; color: var(--gold-primary); margin-top: 3px; }
.tooltip-ohlc { font-size: 10px; color: var(--text-muted); margin-top: 2px; }
.tooltip-reason { font-size: 11px; color: var(--text-secondary); margin-top: 3px; line-height: 1.4; }

/* 命理分析 */
.analysis-card {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.08) 0%, rgba(212, 175, 55, 0.04) 100%);
  border: 1px solid rgba(139, 92, 246, 0.12);
  border-radius: 14px;
  padding: 16px;
  margin-bottom: 14px;
}

.section-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.title-icon { font-size: 16px; }

.summary-row {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 16px;
  padding-bottom: 14px;
  border-bottom: 1px solid rgba(212, 175, 55, 0.08);
}

.summary-score {
  font-size: 28px;
  font-weight: 800;
  flex-shrink: 0;
  width: 50px;
  text-align: center;
}

.summary-text {
  font-size: 13px;
  line-height: 1.6;
  color: var(--text-secondary);
  margin: 0;
  flex: 1;
}

.dim-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.dim-item {
  background: rgba(18, 18, 35, 0.4);
  border: 1px solid rgba(212, 175, 55, 0.06);
  border-radius: 10px;
  padding: 10px 12px;
}

.dim-header {
  display: flex;
  align-items: center;
  gap: 5px;
  margin-bottom: 5px;
}

.dim-icon { font-size: 14px; }
.dim-name { font-size: 13px; font-weight: 600; color: var(--text-primary); }
.dim-score { font-size: 14px; font-weight: 700; margin-left: auto; }

.dim-text {
  font-size: 11px;
  line-height: 1.5;
  color: var(--text-muted);
  margin: 0;
}

/* 大运解读 */
.dayun-section {
  margin-bottom: 14px;
}

.dayun-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.dayun-item {
  background: rgba(18, 18, 35, 0.5);
  border: 1px solid rgba(212, 175, 55, 0.06);
  border-radius: 10px;
  padding: 12px 14px;
  border-left: 3px solid transparent;
}

.dayun-item.great { border-left-color: #4ade80; background: rgba(74, 222, 128, 0.04); }
.dayun-item.good { border-left-color: #d4af37; background: rgba(212, 175, 55, 0.04); }
.dayun-item.normal { border-left-color: #fbbf24; }
.dayun-item.bad { border-left-color: #f87171; background: rgba(248, 113, 113, 0.04); }

.dayun-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.dayun-age { font-size: 13px; font-weight: 600; color: var(--gold-primary); }
.dayun-gz { font-size: 15px; font-weight: 700; font-family: 'KaiTi', serif; color: var(--text-primary); }
.dayun-trend { font-size: 11px; color: var(--text-muted); }
.dayun-score { font-size: 14px; font-weight: 700; margin-left: auto; }

.dayun-shen {
  display: flex;
  gap: 6px;
  align-items: center;
  margin-bottom: 6px;
}

.shen-tag {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
  background: rgba(139, 92, 246, 0.12);
  color: var(--purple-secondary);
}

.shen-wx {
  font-size: 10px;
  color: var(--text-muted);
}

.dayun-points {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.point-tag {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
  background: rgba(212, 175, 55, 0.1);
  color: var(--gold-secondary);
}

.dayun-avg {
  font-size: 10px;
  color: var(--text-muted);
  margin-top: 4px;
}
</style>
