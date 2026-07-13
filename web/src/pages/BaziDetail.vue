<template>
  <div class="page-container">
    <div class="header">
      <button class="back-btn" @click="goBack">←</button>
      <span class="header-title">八字排盘</span>
      <span class="header-placeholder"></span>
    </div>

    <div class="info-card" v-if="baziData">
      <div class="info-row">
        <span class="info-label">农历：</span>
        <span class="info-value">{{ baziData.lunar_date }} {{ baziData.hour_name }} {{ displayGender }}造</span>
      </div>
      <div class="info-row">
        <span class="info-label">阳历：</span>
        <span class="info-value">{{ baziData.solar_date }}</span>
      </div>
    </div>

    <div class="bazi-table" v-if="baziData">
      <div class="table-row header-row">
        <div class="table-cell label-cell">日期</div>
        <div class="table-cell" v-for="(pillar, key) in baziData.pillars" :key="key">
          {{ pillarLabels[key] }}
        </div>
      </div>

      <div class="table-row">
        <div class="table-cell label-cell">主星</div>
        <div class="table-cell" v-for="(pillar, key) in baziData.pillars" :key="key">
          <span class="ten-god">{{ getTenGodGan(key) }}</span>
        </div>
      </div>

      <div class="table-row">
        <div class="table-cell label-cell">天干</div>
        <div class="table-cell" v-for="(pillar, key) in baziData.pillars" :key="key">
          <span class="gan" :class="getWuxingClass(pillar.gan)">{{ pillar.gan }}</span>
          <span class="wuxing-icon">{{ getWuxingIcon(pillar.gan) }}</span>
        </div>
      </div>

      <div class="table-row">
        <div class="table-cell label-cell">地支</div>
        <div class="table-cell" v-for="(pillar, key) in baziData.pillars" :key="key">
          <span class="zhi" :class="getWuxingClass(pillar.zhi)">{{ pillar.zhi }}</span>
          <span class="wuxing-icon">{{ getWuxingIcon(pillar.zhi) }}</span>
        </div>
      </div>

      <div class="table-row">
        <div class="table-cell label-cell">藏干</div>
        <div class="table-cell" v-for="(pillar, key) in baziData.pillars" :key="key">
          <div class="hidden-stems">
            <span v-for="(stem, idx) in getHiddenStems(key)" :key="idx" :class="getWuxingClass(stem)">{{ stem }}</span>
          </div>
        </div>
      </div>

      <div class="table-row">
        <div class="table-cell label-cell">副星</div>
        <div class="table-cell" v-for="(pillar, key) in baziData.pillars" :key="key">
          <div class="ten-gods-zhi">
            <span v-for="(sg, idx) in getTenGodZhi(key)" :key="idx">{{ sg }}</span>
          </div>
        </div>
      </div>

      <div class="table-row">
        <div class="table-cell label-cell">星运</div>
        <div class="table-cell" v-for="(pillar, key) in baziData.pillars" :key="key">
          <span class="di-shi">{{ getDiShi(key) }}</span>
        </div>
      </div>

      <div class="table-row">
        <div class="table-cell label-cell">自坐</div>
        <div class="table-cell" v-for="(pillar, key) in baziData.pillars" :key="key">
          <span class="di-shi">{{ getDiShi(key) }}</span>
        </div>
      </div>

      <div class="table-row">
        <div class="table-cell label-cell">空亡</div>
        <div class="table-cell" v-for="(pillar, key) in baziData.pillars" :key="key">
          <span class="xun-kong">{{ getXunKong(key) }}</span>
        </div>
      </div>

      <div class="table-row">
        <div class="table-cell label-cell">纳音</div>
        <div class="table-cell" v-for="(pillar, key) in baziData.pillars" :key="key">
          <span class="nayin">{{ getNayin(key) }}</span>
        </div>
      </div>

      <div class="table-row">
        <div class="table-cell label-cell">神煞</div>
        <div class="table-cell" v-for="(pillar, key) in baziData.pillars" :key="key">
          <div class="shensha-list">
            <span v-for="(ss, idx) in getShensha(key)" :key="idx">{{ ss }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="reading-section" v-if="baziData">
      <div class="section-header">
        <span class="section-icon">☯</span>
        <span class="section-title">AI命理解读</span>
        <button class="generate-btn" :class="{ disabled: generating }" @click="generateReading">
          <span v-if="!reading && !generating">生成解读</span>
          <span v-else-if="generating">解读中...</span>
          <span v-else>重新解读</span>
        </button>
      </div>

      <div v-if="generating && !reading" class="reading-loading">
        <div class="loading-spinner">
          <span class="spinner-ring"></span>
          <span class="spinner-ring-second"></span>
          <span class="spinner-core">☯</span>
        </div>
        <span class="loading-text">命理师正在推演命局...</span>
      </div>

      <div v-else-if="reading" class="reading-content" v-html="reading"></div>

      <div v-else class="reading-placeholder">
        <div class="placeholder-icon">📜</div>
        <p class="placeholder-text">点击「生成解读」，AI命理师将为你深度解析八字格局</p>
      </div>
    </div>

    <div class="action-bar">
      <button class="action-btn ziwei-btn" @click="goToZiwei">
        <span>🔮</span>
        <span>紫微斗数</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { request } from '@/utils/request'

const router = useRouter()
const route = useRoute()

const baziData = ref(null)
const loading = ref(true)
const reading = ref('')
const generating = ref(false)

const displayGender = computed(() => {
  const gender = route.query.gender || 'male'
  if (gender === '男' || gender === 'male') {
    return '男'
  }
  return '女'
})

const readingCacheKey = computed(() => {
  const d = route.query.date_str || ''
  const h = route.query.hour_index || ''
  const g = displayGender.value
  return `bazi_reading_${d}_${h}_${g}`
})

const pillarLabels = {
  year: '年柱',
  month: '月柱',
  day: '日柱',
  hour: '时柱'
}

const WUXING_MAP = {
  '甲': '木', '乙': '木',
  '丙': '火', '丁': '火',
  '戊': '土', '己': '土',
  '庚': '金', '辛': '金',
  '壬': '水', '癸': '水',
  '子': '水', '丑': '土', '寅': '木', '卯': '木',
  '辰': '土', '巳': '火', '午': '火', '未': '土',
  '申': '金', '酉': '金', '戌': '土', '亥': '水',
}

const WUXING_ICONS = {
  '木': '🌿',
  '火': '🔥',
  '土': '🏔️',
  '金': '⚔️',
  '水': '💧',
}

function getTenGodGan(key) {
  return baziData.value?.ten_gods?.gan?.[key] || ''
}

function getTenGodZhi(key) {
  return baziData.value?.ten_gods?.zhi?.[key] || []
}

function getHiddenStems(key) {
  return baziData.value?.hidden_stems?.[key] || []
}

function getDiShi(key) {
  return baziData.value?.di_shi?.[key] || ''
}

function getXunKong(key) {
  const xk = baziData.value?.xun_kong?.[key] || ''
  return xk.replace('旬空', '')
}

function getNayin(key) {
  return baziData.value?.nayin?.[key] || ''
}

function getShensha(key) {
  return baziData.value?.shensha || []
}

function getWuxing(char) {
  return WUXING_MAP[char] || ''
}

function getWuxingClass(char) {
  const wx = getWuxing(char)
  return `wuxing-${wx}`
}

function getWuxingIcon(char) {
  const wx = getWuxing(char)
  return WUXING_ICONS[wx] || ''
}

async function loadBaziData() {
  const date_str = route.query.date_str || '1990-01-01'
  const hour_index = parseInt(route.query.hour_index) || 0
  const gender = route.query.gender || 'male'

  try {
    const res = await request.post('/bazi/calculate', {
      date_str,
      hour_index,
      gender,
      is_lunar: false
    })
    baziData.value = res
  } catch (e) {
    console.error('加载八字数据失败', e)
  } finally {
    loading.value = false
  }
}

function goBack() {
  router.push('/')
}

async function generateReading() {
  if (generating.value) return

  const date_str = route.query.date_str || '1990-01-01'
  const hour_index = parseInt(route.query.hour_index) || 0
  const gender = route.query.gender || 'male'

  generating.value = true
  reading.value = ''

  try {
    const res = await request.post('/bazi/reading/start', {
      date_str,
      hour_index,
      gender,
      is_lunar: false,
      question: ''
    })

    if (res.status === 'done' && res.result?.reading) {
      reading.value = res.result.reading
      localStorage.setItem(readingCacheKey.value, res.result.reading)
    } else if (res.status === 'failed') {
      reading.value = `<p style="color:#f87171;">解读失败：${res.error || '未知错误'}</p>`
    }
  } catch (e) {
    console.error('解读失败', e)
    reading.value = '<p style="color:#f87171;">解读失败，请稍后重试</p>'
  } finally {
    generating.value = false
  }
}

async function goToZiwei() {
  const date_str = route.query.date_str || '1990-01-01'
  const hour_index = parseInt(route.query.hour_index) || 0
  const gender = route.query.gender || 'male'

  try {
    const res = await request.post('/users/save-chart', {
      solar_date: date_str,
      lunar_date: '',
      hour_index,
      gender,
      is_default: false,
      name: '紫微命盘',
      chart_type: 'ziwei',
      is_leap: false
    })
    router.push(`/chart-detail/${res.id}`)
  } catch (e) {
    router.push({
      path: '/chart-input',
      query: { type: 'ziwei', date_str, hour_index, gender }
    })
  }
}

onMounted(() => {
  const cached = localStorage.getItem(readingCacheKey.value)
  if (cached) {
    reading.value = cached
  }
  loadBaziData()
})
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  background: linear-gradient(180deg, #0a0a15 0%, #1a1525 50%, #0a0a15 100%);
  padding-bottom: 100px;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  padding-top: calc(20px + var(--safe-area-top));
  position: relative;
  z-index: 1;
}

.back-btn {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(212, 175, 55, 0.2);
  border-radius: 12px;
  font-size: 20px;
  color: var(--text-primary);
  cursor: pointer;
}

.header-title {
  font-family: 'Cinzel', serif;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.header-placeholder {
  width: 44px;
}

.info-card {
  margin: 0 20px 20px;
  padding: 16px;
  background: rgba(139, 92, 246, 0.1);
  border: 1px solid rgba(139, 92, 246, 0.2);
  border-radius: 16px;
  position: relative;
  z-index: 1;
}

.info-row {
  display: flex;
  margin-bottom: 8px;
}

.info-row:last-child {
  margin-bottom: 0;
}

.info-label {
  font-size: 13px;
  color: var(--text-muted);
  width: 60px;
}

.info-value {
  font-size: 13px;
  color: var(--text-primary);
}

.bazi-table {
  margin: 0 16px;
  background: rgba(18, 18, 35, 0.8);
  border: 1px solid rgba(212, 175, 55, 0.15);
  border-radius: 16px;
  overflow: hidden;
  position: relative;
  z-index: 1;
}

.table-row {
  display: flex;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.table-row:last-child {
  border-bottom: none;
}

.header-row {
  background: rgba(212, 175, 55, 0.1);
}

.table-cell {
  flex: 1;
  padding: 10px 8px;
  text-align: center;
  font-size: 13px;
  color: var(--text-primary);
  min-height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.label-cell {
  width: 50px;
  flex-shrink: 0;
  background: rgba(0, 0, 0, 0.2);
  color: var(--text-muted);
  font-size: 12px;
}

.ten-god {
  font-size: 13px;
  color: var(--gold-primary);
}

.gan, .zhi {
  font-size: 18px;
  font-weight: 600;
  font-family: 'Cinzel', serif;
}

.wuxing-icon {
  font-size: 12px;
  margin-left: 2px;
}

.wuxing-木 {
  color: #4ade80;
}

.wuxing-火 {
  color: #f87171;
}

.wuxing-土 {
  color: #fbbf24;
}

.wuxing-金 {
  color: #94a3b8;
}

.wuxing-水 {
  color: #60a5fa;
}

.hidden-stems, .ten-gods-zhi, .shensha-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.hidden-stems span, .ten-gods-zhi span, .shensha-list span {
  font-size: 11px;
}

.di-shi {
  font-size: 12px;
  color: var(--text-secondary);
}

.xun-kong {
  font-size: 12px;
  color: var(--text-muted);
}

.nayin {
  font-size: 11px;
  color: #c9a050;
}

.shensha-list span {
  font-size: 10px;
  color: #fbbf24;
}

.action-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 16px 20px;
  padding-bottom: calc(16px + var(--safe-area-bottom));
  background: rgba(10, 10, 20, 0.95);
  border-top: 1px solid rgba(212, 175, 55, 0.15);
  display: flex;
  gap: 16px;
  z-index: 100;
}

.action-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 16px;
  border-radius: 16px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: all 0.3s ease;
}

.ziwei-btn {
  background: linear-gradient(135deg, var(--gold-primary) 0%, var(--gold-secondary) 100%);
  color: #0a0a15;
}

.ziwei-btn:hover {
  transform: scale(1.02);
  box-shadow: 0 0 30px rgba(212, 175, 55, 0.4);
}

.reading-section {
  margin: 20px 16px;
  background: rgba(18, 18, 35, 0.8);
  border: 1px solid rgba(212, 175, 55, 0.15);
  border-radius: 16px;
  overflow: hidden;
  position: relative;
  z-index: 1;
}

.section-header {
  display: flex;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  gap: 8px;
}

.section-icon {
  font-size: 16px;
  color: var(--gold-primary);
}

.section-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  flex: 1;
}

.generate-btn {
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  background: linear-gradient(135deg, var(--gold-primary) 0%, var(--gold-secondary) 100%);
  color: #0a0a15;
  transition: all 0.3s ease;
}

.generate-btn.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.generate-btn:not(.disabled):hover {
  transform: scale(1.05);
  box-shadow: 0 0 20px rgba(212, 175, 55, 0.3);
}

.reading-loading {
  padding: 40px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.loading-spinner {
  position: relative;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.spinner-ring {
  position: absolute;
  width: 100%;
  height: 100%;
  border: 2px solid transparent;
  border-top-color: var(--gold-primary);
  border-radius: 50%;
  animation: spin 1.5s linear infinite;
}

.spinner-ring-second {
  position: absolute;
  width: 80%;
  height: 80%;
  border: 1px solid transparent;
  border-bottom-color: var(--gold-secondary);
  border-radius: 50%;
  animation: spin 2s linear infinite reverse;
}

.spinner-core {
  font-size: 20px;
  color: var(--gold-primary);
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  font-size: 13px;
  color: var(--text-muted);
}

.reading-content {
  padding: 16px;
  font-size: 14px;
  line-height: 1.8;
}

.reading-content :deep(h3) {
  color: #d4a84b;
  font-size: 16px;
  font-weight: bold;
  margin: 20px 0 12px;
}

.reading-content :deep(h3:first-child) {
  margin-top: 0;
}

.reading-content :deep(p) {
  color: #c0c0d8;
  font-size: 14px;
  line-height: 1.8;
  margin: 10px 0;
}

.reading-content :deep(strong) {
  color: #d4a84b;
}

.reading-content :deep(em) {
  color: #c9a050;
  font-style: italic;
}

.reading-content :deep(ul) {
  color: #b0b0c8;
  font-size: 14px;
  line-height: 1.8;
  padding-left: 20px;
  margin: 8px 0;
}

.reading-content :deep(li) {
  margin: 6px 0;
}

.reading-placeholder {
  padding: 40px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.placeholder-icon {
  font-size: 40px;
  opacity: 0.4;
}

.placeholder-text {
  font-size: 13px;
  color: var(--text-muted);
  text-align: center;
}
</style>