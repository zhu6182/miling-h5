<template>
  <div class="page-container">
    <div class="star-field" ref="starField"></div>

    <div v-if="loading" class="loading">
      <div class="loading-spinner">
        <span class="spinner-ring"></span>
        <span class="spinner-ring-second"></span>
        <span class="spinner-core">☯</span>
      </div>
      <span>排盘测算之中...</span>
    </div>

    <div v-else-if="chart">
      <div class="chart-header-info">
        <div class="header-glow"></div>
        <div class="chart-title-row">
          <span class="chart-name">{{ chart.name }}</span>
          <span class="chart-elements">{{ chart.five_elements }}</span>
        </div>
        <span class="chart-meta">{{ chart.solar_date }} · {{ chart.hour_name }} · {{ chart.gender }}</span>
        <div class="header-actions">
          <span class="switch-type-btn" @click="goBaziDetail">查看八字排盘 →</span>
          <span class="match-btn share-btn" @click="onShareTap">
            <span class="match-icon">📤</span>
            <span>分享</span>
          </span>
          <span class="match-btn" @click="openMatchSelector">
            <span class="match-icon">👥</span>
            <span>找人合缘</span>
          </span>
        </div>
      </div>

      <div v-if="chart.chart_data?.sihua" class="four-hua-row">
        <span class="four-hua-label">生年四化</span>
        <div class="four-hua-tags">
          <span v-if="chart.chart_data.sihua.lu" class="hua-tag hua-lu">{{ chart.chart_data.sihua.lu }}禄</span>
          <span v-if="chart.chart_data.sihua.quan" class="hua-tag hua-quan">{{ chart.chart_data.sihua.quan }}权</span>
          <span v-if="chart.chart_data.sihua.ke" class="hua-tag hua-ke">{{ chart.chart_data.sihua.ke }}科</span>
          <span v-if="chart.chart_data.sihua.ji" class="hua-tag hua-ji">{{ chart.chart_data.sihua.ji }}忌</span>
        </div>
      </div>

      <div class="chart-container">
        <div class="chart-glow-ring"></div>
        <div class="chart-grid">
          <div class="grid-cell" :class="{ 'center-cell': cell.center }" v-for="(cell, index) in palaceGrid" :key="index">
            <template v-if="cell.center">
              <div class="center-area">
                <div class="center-ring"></div>
                <span class="center-title">命盘</span>
                <span class="center-sub">{{ chart.soul_palace }}宫命</span>
                <div class="center-glow"></div>
              </div>
            </template>
            <template v-else-if="cell.palace">
              <div class="palace-cell" :class="{ active: cell.palace.tags?.[0] === '命宫', 'body-palace': cell.palace.tags?.[0] === '身宫' }">
                <span class="palace-name">{{ cell.palace.name }}</span>
                <span class="palace-branch">{{ cell.palace.earthly_branch }}</span>
                <div class="palace-stars">
                  <span class="star main" v-for="star in cell.palace.major_stars" :key="star">{{ star }}</span>
                  <span class="star minor" v-for="star in cell.palace.minor_stars" :key="star">{{ star }}</span>
                  <span v-if="!cell.palace.major_stars?.length" class="star empty">空宫</span>
                </div>
                <div class="palace-corner"></div>
              </div>
            </template>
            <template v-else>
              <div class="palace-cell empty-cell"></div>
            </template>
          </div>
        </div>
      </div>

      <div class="reading-section">
        <div class="section-header">
          <span class="section-icon">☯</span>
          <span class="section-title">命理解读</span>
          <span class="generate-btn" :class="{ disabled: generating }" @click="generateReading">
            <span v-if="!reading && !generating">生成解读</span>
            <span v-else-if="generating">生成中...</span>
            <span v-else>重新解读</span>
          </span>
        </div>

        <div v-if="reading" class="reading-cards">
          <div class="reading-card" v-for="item in readingCards" :key="item.title">
            <div class="card-decoration"></div>
            <div class="card-header">
              <span class="card-title">{{ item.title }}</span>
              <span v-if="item.badge" class="card-badge">{{ item.badge }}</span>
            </div>
            <div class="card-body" v-html="item.body"></div>
          </div>
        </div>

        <div v-else class="no-reading">
          <div class="no-reading-icon">☯</div>
          <div class="no-reading-text">点击上方按钮，生成命理解读</div>
        </div>
      </div>
    </div>

    <div v-if="showMatchModal" class="modal-mask" @click="showMatchModal = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <span class="modal-title">选择要匹配的命盘</span>
          <span class="modal-close" @click="showMatchModal = false">×</span>
        </div>
        <div v-if="chartsLoading" class="modal-loading">
          <span>加载中...</span>
        </div>
        <div v-else-if="filteredCharts.length === 0" class="modal-empty">
          <span class="empty-icon">📋</span>
          <span class="empty-text">暂无其他命盘可匹配</span>
        </div>
        <div v-else class="chart-list">
          <div class="chart-item" v-for="c in filteredCharts" :key="c.id" @click="selectChartForMatch(c.id)">
            <div class="chart-item-left">
              <span class="chart-item-name">{{ c.remark || c.name }}</span>
              <div class="chart-item-meta">
                <span class="chart-item-gender">{{ c.gender }}</span>
                <span class="chart-item-date">{{ c.solar_date }} {{ c.hour_name }}</span>
              </div>
            </div>
            <span class="chart-item-arrow">→</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { request } from '@/utils/request'

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const chart = ref(null)
const reading = ref('')
const generating = ref(false)
const showMatchModal = ref(false)
const chartsLoading = ref(false)
const charts = ref([])
const starField = ref(null)

const readingCards = computed(() => {
  if (!reading.value) return []
  // 如果后端返回的是 cards 数组，直接展示；否则兼容旧版 body 文本
  if (Array.isArray(reading.value.cards)) {
    return reading.value.cards
  }
  if (typeof reading.value === 'string') {
    return [{ title: '星盘深度分析', body: reading.value }]
  }
  if (reading.value.body) {
    return [{ title: '星盘深度分析', body: reading.value.body }]
  }
  return []
})

const palaceGrid = computed(() => {
  if (!chart.value?.chart_data?.palaces) return []
  const palaces = chart.value.chart_data.palaces
  return [
    { palace: palaces[0] },
    { palace: palaces[1] },
    { palace: palaces[2] },
    { palace: palaces[3] },
    { palace: palaces[11] },
    { center: true },
    { palace: palaces[4] },
    { palace: palaces[5] },
    { palace: palaces[10] },
    { palace: palaces[9] },
    { palace: palaces[8] },
    { palace: palaces[7] },
    { palace: palaces[6] }
  ]
})

const filteredCharts = computed(() => {
  return charts.value.filter(c => c.id !== route.params.id)
})

async function loadChart() {
  try {
    const res = await request.get(`/charts/${route.params.id}`)
    chart.value = res
    console.log('命盘数据:', res)
    console.log('宫位数据:', res.chart_data?.palaces)
    if (res.reading_data) {
      reading.value = res.reading_data
    }
  } catch (e) {
    console.error('加载星盘失败', e)
  } finally {
    loading.value = false
  }
}

function goBaziDetail() {
  router.push({
    path: '/bazi-detail',
    query: {
      date_str: chart.value.solar_date,
      hour_index: chart.value.hour_index,
      gender: chart.value.gender
    }
  })
}

function onShareTap() {
  if (navigator.share) {
    navigator.share({
      title: `${chart.value.name}的星盘`,
      url: window.location.href
    })
  } else {
    alert('请复制链接分享')
  }
}

async function openMatchSelector() {
  try {
    const res = await request.get('/charts')
    charts.value = res || []
    showMatchModal.value = true
  } catch (e) {
    console.error('加载星盘列表失败', e)
  }
}

async function selectChartForMatch(chartId) {
  try {
    const res = await request.post('/match/direct', {
      chart_a_id: route.params.id,
      chart_b_id: chartId,
      match_type: 'all'
    })
    showMatchModal.value = false
    router.push(`/match-result/${res.match_id}`)
  } catch (e) {
    console.error('匹配失败', e)
    alert('匹配失败')
  }
}

async function generateReading() {
  if (generating.value) return
  generating.value = true
  try {
    const res = await request.post(`/charts/${route.params.id}/reading/start`, { ad_watched: true })
    const taskId = res.task_id
    let status = 'processing'
    while (status === 'processing') {
      await new Promise(r => setTimeout(r, 2000))
      const statusRes = await request.get(`/charts/${route.params.id}/reading/status?task_id=${taskId}`)
      status = statusRes.status
      if (status === 'completed') {
        reading.value = statusRes.result?.reading || null
        alert('解读生成完成')
      } else if (status === 'failed') {
        alert('生成失败')
        break
      }
    }
  } catch (e) {
    console.error('生成解读失败', e)
    alert('生成失败')
  } finally {
    generating.value = false
  }
}

function initStars() {
  if (!starField.value) return
  const container = starField.value
  const starCount = 60
  
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
  loadChart()
  initStars()
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

.star-field .star {
  position: absolute;
  background: white;
  border-radius: 50%;
  animation: twinkle 3s ease-in-out infinite;
}

@keyframes twinkle {
  0%, 100% { opacity: 0.2; transform: scale(1); }
  50% { opacity: 0.8; transform: scale(1.2); }
}

.loading {
  text-align: center;
  padding: 100px 0;
  color: var(--text-muted);
}

.loading-spinner {
  position: relative;
  width: 100px;
  height: 100px;
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
  font-size: 36px;
  animation: float 2s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translate(-50%, -50%) translateY(0); }
  50% { transform: translate(-50%, -50%) translateY(-8px); }
}

.chart-header-info {
  text-align: center;
  padding: 24px 24px 30px;
  position: relative;
}

.header-glow {
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle at 50% 0%, rgba(139, 92, 246, 0.08) 0%, transparent 50%);
  pointer-events: none;
}

.chart-title-row {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-bottom: 8px;
}

.chart-name {
  font-family: 'Cinzel', serif;
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
}

.chart-elements {
  font-size: 13px;
  color: var(--gold-primary);
  background: rgba(212, 175, 55, 0.1);
  padding: 4px 14px;
  border-radius: 16px;
}

.chart-meta {
  font-size: 14px;
  color: var(--text-muted);
}

.header-actions {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
  margin-top: 16px;
  flex-wrap: wrap;
}

.switch-type-btn {
  display: inline-block;
  font-size: 13px;
  color: var(--gold-primary);
  background: rgba(212, 175, 55, 0.08);
  padding: 8px 20px;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.switch-type-btn:hover {
  background: rgba(212, 175, 55, 0.12);
}

.match-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--gold-primary);
  background: rgba(212, 175, 55, 0.08);
  border: 1px solid rgba(212, 175, 55, 0.2);
  padding: 8px 18px;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.match-btn:hover {
  background: rgba(212, 175, 55, 0.12);
}

.match-icon {
  font-size: 14px;
}

.four-hua-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  padding: 0 24px;
}

.four-hua-label {
  font-size: 14px;
  color: var(--text-muted);
}

.four-hua-tags {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.hua-tag {
  font-size: 12px;
  padding: 5px 12px;
  border-radius: 12px;
  font-weight: 500;
}

.hua-lu { color: #50c878; background: rgba(80, 200, 120, 0.1); }
.hua-quan { color: var(--gold-primary); background: rgba(212, 175, 55, 0.1); }
.hua-ke { color: #6090c8; background: rgba(96, 144, 200, 0.1); }
.hua-ji { color: #e06060; background: rgba(224, 96, 96, 0.1); }

.chart-container {
  position: relative;
  padding: 0 24px;
  margin-bottom: 32px;
}

.chart-glow-ring {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 90%;
  height: 90%;
  background: radial-gradient(circle, rgba(212, 175, 55, 0.03) 0%, rgba(139, 92, 246, 0.02) 50%, transparent 70%);
  border-radius: 50%;
  pointer-events: none;
}

.chart-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
  aspect-ratio: 1;
}

.grid-cell {
  position: relative;
}

.center-cell {
  grid-column: 2 / 4;
  grid-row: 2 / 4;
}

.center-area {
  background: rgba(212, 175, 55, 0.08);
  border: 1px solid rgba(212, 175, 55, 0.2);
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100%;
  width: 100%;
  position: relative;
  overflow: hidden;
}

.center-ring {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 80%;
  height: 80%;
  border: 1px solid rgba(212, 175, 55, 0.15);
  border-radius: 50%;
  animation: rotate 30s linear infinite;
}

@keyframes rotate {
  from { transform: translate(-50%, -50%) rotate(0deg); }
  to { transform: translate(-50%, -50%) rotate(360deg); }
}

.center-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 60px;
  height: 60px;
  background: radial-gradient(circle, rgba(212, 175, 55, 0.2) 0%, transparent 70%);
  border-radius: 50%;
  animation: pulse-glow 3s ease-in-out infinite;
}

@keyframes pulse-glow {
  0%, 100% { opacity: 0.5; transform: translate(-50%, -50%) scale(1); }
  50% { opacity: 1; transform: translate(-50%, -50%) scale(1.1); }
}

.center-title {
  font-family: 'Cinzel', serif;
  font-size: 22px;
  font-weight: 600;
  color: var(--gold-primary);
  letter-spacing: 6px;
}

.center-sub {
  font-size: 13px;
  color: var(--text-muted);
  margin-top: 6px;
}

.palace-cell {
  background: rgba(18, 18, 35, 0.6);
  border: 1px solid rgba(212, 175, 55, 0.1);
  border-radius: 12px;
  padding: 8px 4px;
  min-height: 80px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  position: relative;
  transition: all 0.3s ease;
}

.palace-cell:active {
  transform: scale(0.98);
}

.palace-cell.active {
  background: rgba(224, 96, 96, 0.08);
  border-color: rgba(224, 96, 96, 0.3);
}

.palace-cell.body-palace {
  background: rgba(96, 144, 200, 0.08);
  border-color: rgba(96, 144, 200, 0.3);
}

.palace-corner {
  position: absolute;
  top: 2px;
  right: 2px;
  width: 10px;
  height: 10px;
  border-right: 1px solid rgba(212, 175, 55, 0.15);
  border-top: 1px solid rgba(212, 175, 55, 0.15);
  border-radius: 0 12px 0 0;
}

.palace-name {
  font-size: 11px;
  color: var(--text-muted);
}

.palace-branch {
  font-size: 13px;
  color: var(--gold-primary);
  font-weight: 500;
}

.palace-stars {
  display: flex;
  flex-wrap: wrap;
  gap: 2px 4px;
}

.palace-stars .star {
  font-size: 11px;
  color: var(--text-secondary);
  position: static;
  background: none;
  border-radius: 0;
  animation: none;
  display: inline;
}

.palace-stars .star.main {
  color: var(--text-primary);
  font-weight: 500;
}

.palace-stars .star.empty {
  color: var(--text-dim);
  font-style: italic;
}

.empty-cell {
  background: transparent;
  border: none;
}

.reading-section {
  margin-top: 16px;
  padding: 0 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-icon {
  font-size: 18px;
}

.section-title {
  font-family: 'Cinzel', serif;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.generate-btn {
  font-size: 14px;
  color: var(--gold-primary);
  background: rgba(212, 175, 55, 0.1);
  border: 1px solid rgba(212, 175, 55, 0.3);
  padding: 8px 20px;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.generate-btn:hover {
  background: rgba(212, 175, 55, 0.15);
}

.generate-btn.disabled {
  opacity: 0.6;
}

.reading-cards {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.reading-card {
  background: rgba(18, 18, 35, 0.7);
  border: 1px solid rgba(212, 175, 55, 0.1);
  border-radius: 18px;
  padding: 24px;
  position: relative;
  overflow: hidden;
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

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.card-badge {
  font-size: 12px;
  color: var(--gold-primary);
}

.card-body {
  font-size: 14px;
  line-height: 1.8;
  color: var(--text-secondary);
}

.card-body :deep(strong) { color: var(--text-primary); font-weight: 600; }
.card-body :deep(em) { color: var(--gold-primary); font-style: normal; }

.no-reading {
  text-align: center;
  padding: 48px 20px;
  color: var(--text-muted);
}

.no-reading-icon {
  font-size: 56px;
  display: block;
  margin-bottom: 16px;
  animation: float 4s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.no-reading-text {
  font-size: 14px;
}

.modal-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  z-index: 1000;
  display: flex;
  align-items: flex-end;
}

.modal-content {
  width: 100%;
  max-height: 70vh;
  background: linear-gradient(180deg, rgba(18, 18, 35, 0.95) 0%, rgba(5, 5, 16, 0.98) 100%);
  border-radius: 24px 24px 0 0;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid rgba(212, 175, 55, 0.1);
}

.modal-title {
  font-family: 'Cinzel', serif;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.modal-close {
  font-size: 32px;
  color: var(--text-muted);
  line-height: 1;
  cursor: pointer;
}

.modal-loading {
  text-align: center;
  padding: 48px 0;
  color: var(--text-muted);
}

.modal-empty {
  text-align: center;
  padding: 48px 0;
  color: var(--text-muted);
}

.empty-icon {
  font-size: 48px;
  display: block;
  margin-bottom: 12px;
}

.empty-text {
  font-size: 14px;
}

.chart-list {
  flex: 1;
  max-height: 50vh;
  padding: 12px 24px 40px;
}

.chart-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(212, 175, 55, 0.1);
  border-radius: 14px;
  margin-bottom: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.chart-item:active {
  transform: scale(0.98);
}

.chart-item-left {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.chart-item-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.chart-item-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

.chart-item-gender {
  font-size: 12px;
  color: var(--gold-primary);
  background: rgba(212, 175, 55, 0.1);
  padding: 4px 10px;
  border-radius: 12px;
}

.chart-item-date {
  font-size: 13px;
  color: var(--text-muted);
}

.chart-item-arrow {
  font-size: 18px;
  color: var(--gold-primary);
}
</style>
