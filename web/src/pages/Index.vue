<template>
  <div class="page-container">
    <div class="header-section">
      <div class="logo-ring">
        <div class="logo-core">
          <span class="logo-symbol">☽</span>
        </div>
        <div class="ring-orbit"></div>
        <div class="ring-orbit-second"></div>
      </div>
      <h1 class="main-title">命里</h1>
      <p class="sub-title">· 命理玄机 ·</p>
      <p class="slogan">探索八字命运的奥秘</p>
    </div>

    <div class="tabs-container">
      <button class="tab-btn" :class="{ active: activeTab === 'self' }" @click="activeTab = 'self'">
        <span class="tab-text">我的命盘</span>
      </button>
      <button class="tab-btn" :class="{ active: activeTab === 'help' }" @click="activeTab = 'help'">
        <span class="tab-text">帮TA测算</span>
      </button>
    </div>

    <div class="main-content">
      <div v-if="!isLoggedIn" class="welcome-card">
        <div class="card-illustration">
          <span class="illustration-icon">🔮</span>
        </div>
        <h3 class="card-title">欢迎来到命里</h3>
        <p class="card-desc">输入你的生辰，探索专属命理玄机</p>
        <button class="btn-primary" @click="goLogin">
          <span class="btn-text">开启命理之旅</span>
          <span class="btn-arrow">→</span>
        </button>
      </div>

      <div v-if="isLoggedIn && charts.length > 0" class="charts-section">
        <div class="section-header">
          <h2 class="section-title">
            <span class="title-icon">☯</span>
            我的命盘
          </h2>
          <button class="add-chart-btn" @click="goAddChart">
            <span>+ 添加</span>
          </button>
        </div>
        <div class="current-chart-card" v-if="defaultChart" @click="goChartDetail(defaultChart.id)">
          <div class="current-chart-icon">
            <span class="icon-symbol">{{ getChartIcon(defaultChart.chart_type) }}</span>
          </div>
          <div class="current-chart-info">
            <h3 class="current-chart-name">{{ defaultChart.name }}</h3>
            <p class="current-chart-date">{{ defaultChart.solar_date }} · {{ defaultChart.hour_name }} · {{ defaultChart.gender }}</p>
          </div>
          <span class="current-chart-arrow">→</span>
        </div>
        <div class="charts-grid" v-if="charts.length > 1">
          <div class="chart-card" v-for="chart in charts" :key="chart.id" @click="goChartDetail(chart.id)">
            <div class="card-header">
              <div class="chart-icon">
                <span class="icon-symbol">{{ getChartIcon(chart.chart_type) }}</span>
              </div>
              <div class="chart-info">
                <h4 class="chart-name">{{ chart.name }}</h4>
                <p class="chart-date">{{ chart.solar_date }} · {{ chart.hour_name }}</p>
              </div>
            </div>
            <div class="chart-tags">
              <span class="tag" :class="getTagClass(chart.chart_type)">{{ getChartTypeName(chart.chart_type) }}</span>
              <span v-if="chart.is_default" class="tag default-tag">默认</span>
            </div>
            <div class="card-footer">
              <span class="footer-text">查看详情</span>
              <span class="footer-arrow">→</span>
            </div>
          </div>
        </div>
      </div>

      <div class="features-section">
        <div class="section-header">
          <h2 class="section-title">
            <span class="title-icon">☯</span>
            核心功能
          </h2>
        </div>
        <div class="features-grid">
          <button class="feature-card" @click="goFortune">
            <span class="feature-icon">📅</span>
            <h3 class="feature-title">今日运势</h3>
            <p class="feature-desc">每日命理指引</p>
          </button>
          <button class="feature-card" @click="goBaziDetail">
            <span class="feature-icon">📜</span>
            <h3 class="feature-title">八字排盘</h3>
            <p class="feature-desc">四柱命理推算</p>
          </button>
          <button class="feature-card" @click="goChartInput">
            <span class="feature-icon">🔮</span>
            <h3 class="feature-title">紫微命盘</h3>
            <p class="feature-desc">十二宫精准解析</p>
          </button>
          <button class="feature-card" @click="goLifeKline">
            <span class="feature-icon">📈</span>
            <h3 class="feature-title">人生K线</h3>
            <p class="feature-desc">命运起伏曲线</p>
          </button>
        </div>
      </div>

      <div class="daily-card">
        <div class="card-left">
          <span class="daily-icon">☯</span>
          <div class="daily-content">
            <h4 class="daily-title">今日宜忌</h4>
            <p class="daily-text">{{ todayFortune }}</p>
          </div>
        </div>
        <button class="daily-btn" @click="goFortune">
          <span>查看</span>
          <span class="btn-arrow">→</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onActivated } from 'vue'
import { useRouter } from 'vue-router'
import { request } from '@/utils/request'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const activeTab = ref('self')
const charts = ref([])
const todayFortune = ref('加载中...')

const isLoggedIn = computed(() => authStore.isLoggedIn)

const defaultChart = computed(() => {
  return charts.value.find(c => c.is_default) || charts.value[0] || null
})

async function loadTodayFortune() {
  if (!authStore.isLoggedIn) {
    todayFortune.value = '宜出行、求财、动土'
    return
  }
  try {
    const res = await request.get('/fortune/today')
    if (res && res.do_list && res.do_list.length) {
      todayFortune.value = '宜 ' + res.do_list.slice(0, 3).join('、')
    } else {
      todayFortune.value = '今日诸事皆宜'
    }
  } catch (e) {
    todayFortune.value = '宜出行、求财、动土'
  }
}

async function checkLogin() {
  if (authStore.token) {
    try {
      const res = await request.get('/users/me')
      authStore.setUser(res)
      loadCharts()
      loadTodayFortune()
    } catch (e) {
      if (e.response?.status === 401) {
        authStore.logout()
      }
    }
  }
}

async function loadCharts() {
  try {
    const res = await request.get('/charts')
    charts.value = res || []
  } catch (e) {
    console.error('加载命盘失败', e)
  }
}

function goLogin() {
  router.push('/profile')
}

function goAddChart() {
  router.push('/chart-input')
}

function goChartDetail(id) {
  router.push(`/chart-detail/${id}`)
}

function goFortune() {
  if (defaultChart.value) {
    router.push({
      path: '/fortune',
      query: {
        date_str: defaultChart.value.solar_date,
        hour_index: defaultChart.value.hour_index,
        gender: defaultChart.value.gender
      }
    })
  } else {
    router.push('/chart-input')
  }
}

function goChartInput() {
  if (defaultChart.value) {
    router.push(`/chart-detail/${defaultChart.value.id}`)
  } else {
    router.push('/chart-input')
  }
}

function goBaziDetail() {
  if (defaultChart.value) {
    router.push({
      path: '/bazi-detail',
      query: {
        date_str: defaultChart.value.solar_date,
        hour_index: defaultChart.value.hour_index,
        gender: defaultChart.value.gender
      }
    })
  } else {
    router.push('/birth-input?type=bazi')
  }
}

function goLifeKline() {
  if (defaultChart.value) {
    router.push({
      path: '/life-kline',
      query: {
        date_str: defaultChart.value.solar_date,
        hour_index: defaultChart.value.hour_index,
        gender: defaultChart.value.gender
      }
    })
  } else {
    router.push('/chart-input')
  }
}

function getChartIcon(type) {
  return type === 'bazi' ? '📜' : '🔮'
}

function getChartTypeName(type) {
  return type === 'bazi' ? '八字四柱' : '紫微斗数'
}

function getTagClass(type) {
  return type === 'bazi' ? 'bazi-tag' : 'ziwei-tag'
}

const hasLoaded = ref(false)

onMounted(() => {
  if (!hasLoaded.value) {
    checkLogin()
    hasLoaded.value = true
  }
})

onActivated(() => {
  if (authStore.isLoggedIn) {
    if (charts.value.length === 0) {
      loadCharts()
    }
    loadTodayFortune()
  }
})
</script>

<style scoped>
.header-section {
  text-align: center;
  padding: 40px 20px 20px;
}

.logo-ring {
  position: relative;
  width: 80px;
  height: 80px;
  margin: 0 auto 16px;
}

.logo-core {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 40px;
  height: 40px;
  background: radial-gradient(circle, rgba(212, 175, 55, 0.4) 0%, rgba(139, 92, 246, 0.2) 50%, transparent 70%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: pulse-glow 3s ease-in-out infinite;
}

@keyframes pulse-glow {
  0%, 100% { box-shadow: 0 0 15px rgba(212, 175, 55, 0.3); }
  50% { box-shadow: 0 0 30px rgba(212, 175, 55, 0.5), 0 0 50px rgba(139, 92, 246, 0.2); }
}

.logo-symbol {
  font-size: 24px;
  animation: float 4s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-4px); }
}

.ring-orbit {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 70px;
  height: 70px;
  border: 1px solid rgba(212, 175, 55, 0.15);
  border-radius: 50%;
  animation: rotate 25s linear infinite;
}

.ring-orbit-second {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 50px;
  height: 50px;
  border: 1px solid rgba(139, 92, 246, 0.1);
  border-radius: 50%;
  animation: rotate 15s linear infinite reverse;
}

@keyframes rotate {
  from { transform: translate(-50%, -50%) rotate(0deg); }
  to { transform: translate(-50%, -50%) rotate(360deg); }
}

.main-title {
  font-family: 'Cinzel', serif;
  font-size: 42px;
  font-weight: 700;
  background: linear-gradient(135deg, var(--gold-primary) 0%, var(--gold-secondary) 40%, var(--purple-secondary) 60%, var(--gold-primary) 100%);
  background-size: 200% 200%;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 6px;
  letter-spacing: 6px;
  animation: gradient-shift 4s ease infinite;
}

@keyframes gradient-shift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.sub-title {
  font-size: 13px;
  color: rgba(167, 139, 250, 0.7);
  margin-bottom: 6px;
  letter-spacing: 6px;
}

.slogan {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 0;
  font-style: italic;
}

.tabs-container {
  display: flex;
  margin: 0 20px 20px;
  background: rgba(10, 10, 25, 0.6);
  border-radius: 16px;
  padding: 4px;
  border: 1px solid rgba(139, 92, 246, 0.1);
}

.tab-btn {
  flex: 1;
  padding: 12px;
  text-align: center;
  border-radius: 12px;
  border: none;
  background: transparent;
  color: rgba(150, 150, 180, 0.7);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.tab-btn.active {
  background: linear-gradient(135deg, rgba(212, 175, 55, 0.15) 0%, rgba(139, 92, 246, 0.1) 100%);
  color: var(--gold-primary);
}

.main-content {
  padding: 0 20px;
}

.welcome-card {
  background: rgba(10, 10, 25, 0.5);
  border: 1px solid rgba(139, 92, 246, 0.15);
  border-radius: 20px;
  padding: 30px 24px;
  text-align: center;
  margin-bottom: 24px;
}

.card-illustration {
  margin-bottom: 14px;
}

.illustration-icon {
  font-size: 56px;
  animation: float 5s ease-in-out infinite;
}

.card-title {
  font-family: 'Cinzel', serif;
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.card-desc {
  font-size: 13px;
  color: var(--text-muted);
  margin-bottom: 20px;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: linear-gradient(135deg, var(--gold-primary) 0%, var(--gold-secondary) 100%);
  color: #0a0a15;
  border: none;
  border-radius: 24px;
  padding: 13px 32px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary:hover {
  transform: scale(1.02);
  box-shadow: 0 0 30px rgba(212, 175, 55, 0.4);
}

.btn-text {
  font-family: 'Cinzel', serif;
  letter-spacing: 2px;
}

.btn-arrow {
  font-size: 16px;
}

.current-chart-card {
  display: flex;
  align-items: center;
  gap: 14px;
  background: linear-gradient(135deg, rgba(212, 175, 55, 0.12) 0%, rgba(139, 92, 246, 0.08) 100%);
  border: 1px solid rgba(212, 175, 55, 0.25);
  border-radius: 18px;
  padding: 18px;
  margin-bottom: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.current-chart-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(212, 175, 55, 0.15);
}

.current-chart-icon {
  width: 52px;
  height: 52px;
  background: rgba(212, 175, 55, 0.15);
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.current-chart-icon .icon-symbol {
  font-size: 26px;
}

.current-chart-info {
  flex: 1;
  min-width: 0;
}

.current-chart-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 4px;
}

.current-chart-date {
  font-size: 12px;
  color: var(--text-secondary);
  margin: 0;
}

.current-chart-arrow {
  font-size: 18px;
  color: var(--gold-primary);
  flex-shrink: 0;
}

.charts-section {
  margin-bottom: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.section-title {
  font-family: 'Cinzel', serif;
  font-size: 17px;
  font-weight: 600;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 6px;
}

.title-icon {
  color: var(--gold-primary);
  font-size: 14px;
}

.add-chart-btn {
  background: transparent;
  border: 1px solid rgba(212, 175, 55, 0.2);
  color: var(--gold-primary);
  border-radius: 16px;
  padding: 6px 16px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.add-chart-btn:hover {
  background: rgba(212, 175, 55, 0.1);
}

.charts-grid {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.chart-card {
  background: rgba(10, 10, 25, 0.4);
  border: 1px solid rgba(139, 92, 246, 0.08);
  border-radius: 16px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.chart-card:hover {
  border-color: rgba(212, 175, 55, 0.25);
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}

.chart-icon {
  width: 44px;
  height: 44px;
  background: rgba(212, 175, 55, 0.06);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-symbol {
  font-size: 22px;
}

.chart-info {
  flex: 1;
}

.chart-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 2px;
}

.chart-date {
  font-size: 12px;
  color: var(--text-muted);
}

.chart-tags {
  display: flex;
  gap: 6px;
  margin-bottom: 10px;
}

.tag {
  font-size: 10px;
  padding: 3px 10px;
  border-radius: 10px;
  background: rgba(212, 175, 55, 0.06);
  color: var(--gold-primary);
}

.default-tag {
  background: rgba(139, 92, 246, 0.06);
  color: var(--purple-secondary);
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 8px;
  border-top: 1px solid rgba(139, 92, 246, 0.06);
}

.footer-text {
  font-size: 12px;
  color: var(--text-muted);
}

.footer-arrow {
  font-size: 14px;
  color: var(--gold-primary);
}

.features-section {
  margin-bottom: 24px;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.feature-card {
  background: rgba(10, 10, 25, 0.3);
  border: 1px solid rgba(139, 92, 246, 0.06);
  border-radius: 16px;
  padding: 20px 12px;
  text-align: center;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
}

.feature-card:hover {
  border-color: rgba(212, 175, 55, 0.2);
  transform: translateY(-2px);
}

.feature-icon {
  font-size: 24px;
  margin-bottom: 8px;
}

.feature-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.feature-desc {
  font-size: 11px;
  color: var(--text-muted);
}

.daily-card {
  background: rgba(10, 10, 25, 0.4);
  border: 1px solid rgba(139, 92, 246, 0.1);
  border-radius: 16px;
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 80px;
}

.card-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.daily-icon {
  font-size: 28px;
  color: var(--gold-primary);
}

.daily-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.daily-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.daily-text {
  font-size: 12px;
  color: var(--text-muted);
  margin: 0;
}

.daily-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: transparent;
  border: 1px solid rgba(212, 175, 55, 0.2);
  color: var(--gold-primary);
  border-radius: 16px;
  padding: 8px 16px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.daily-btn:hover {
  background: rgba(212, 175, 55, 0.1);
}
</style>
