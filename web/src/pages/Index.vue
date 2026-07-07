<template>
  <div class="index-page">
    <div class="header">
      <div class="title">
        <span class="main-title">星运日记</span>
        <span class="sub-title">· 每日星座运势 ·</span>
      </div>
      <div class="slogan">星辰指引，遇见更好的自己</div>
    </div>

    <div v-if="!isLoggedIn" class="welcome-card">
      <div class="welcome-title">欢迎来到星运日记</div>
      <div class="welcome-desc">输入你的生辰，探索专属星座运势</div>
      <button class="btn-primary" @click="$router.push('/profile')">立即登录 / 注册</button>
    </div>

    <div v-else class="container">
      <div class="tab-bar-page">
        <div 
          class="tab-item-page" 
          :class="{ active: activeTab === 'my' }"
          @click="activeTab = 'my'"
        >我的星盘</div>
        <div 
          class="tab-item-page" 
          :class="{ active: activeTab === 'helped' }"
          @click="activeTab = 'helped'"
        >帮亲友查</div>
      </div>

      <div v-if="activeTab === 'my'">
        <div v-if="!hasChart" class="no-chart-card">
          <div class="no-chart-icon">✨</div>
          <div class="no-chart-title">还没有你的星盘</div>
          <div class="no-chart-desc">输入生辰信息，生成你的专属星盘</div>
          <button class="btn-primary" @click="$router.push('/birth-input')">生成星盘</button>
        </div>

        <div v-else>
          <div class="chart-overview" @click="goDetail(defaultChart.id)">
            <div class="chart-header">
              <span class="chart-name">{{ defaultChart.name }}</span>
              <span class="chart-badge">默认星盘</span>
            </div>
            <div class="chart-info">
              <div class="info-item">
                <span class="info-label">守护星</span>
                <span class="info-value text-gold">{{ defaultChart.soul_palace }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">星座元素</span>
                <span class="info-value">{{ defaultChart.five_elements }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">生辰</span>
                <span class="info-value">{{ defaultChart.solar_date }} {{ defaultChart.hour_name }}</span>
              </div>
            </div>
            <div class="chart-action">
              <span>查看完整星盘解读</span>
              <span class="arrow">→</span>
            </div>
          </div>

          <div class="quick-actions">
            <div class="action-item" @click="$router.push('/fortune')">
              <span class="action-icon">🌟</span>
              <span class="action-text">今日运势</span>
            </div>
            <div class="action-item" @click="$router.push('/birth-input')">
              <span class="action-icon">✨</span>
              <span class="action-text">星盘解析</span>
            </div>
            <div class="action-item" @click="goBaziInput">
              <span class="action-icon">🔮</span>
              <span class="action-text">性格测试</span>
            </div>
            <div class="action-item" @click="goLifeKline">
              <span class="action-icon">📈</span>
              <span class="action-text">运势曲线</span>
            </div>
          </div>

          <div class="list-title">我的星盘</div>
          <div 
            v-for="chart in myCharts" 
            :key="chart.id"
            class="chart-card"
            @click="goDetail(chart.id)"
          >
            <div class="chart-card-left">
              <span class="chart-card-name">{{ chart.name }}</span>
              <div class="chart-card-meta">
                <span class="chart-card-tag">{{ chart.soul_palace }}</span>
                <span class="chart-card-desc">{{ chart.solar_date }}</span>
              </div>
            </div>
            <div class="chart-card-right">→</div>
          </div>
        </div>
      </div>

      <div v-if="activeTab === 'helped'">
        <div v-if="helpedCharts.length === 0" class="no-chart-card">
          <div class="no-chart-icon">👥</div>
          <div class="no-chart-title">还没有帮亲友生成的星盘</div>
          <div class="no-chart-desc">帮亲友分析星盘，一键查看运势</div>
          <button class="btn-primary" @click="$router.push('/birth-input')">去生成</button>
        </div>
        <div v-else>
          <div 
            v-for="chart in helpedCharts" 
            :key="chart.id"
            class="chart-card"
            @click="goDetail(chart.id)"
          >
            <div class="chart-card-left">
              <span class="chart-card-name">{{ chart.name }}</span>
              <div class="chart-card-meta">
                <span class="chart-card-tag">{{ chart.soul_palace }}</span>
                <span class="chart-card-desc">{{ chart.solar_date }}</span>
              </div>
            </div>
            <div class="chart-card-right">→</div>
          </div>
        </div>
      </div>

      <div class="feature-section">
        <div class="section-title">核心功能</div>
        <div class="feature-grid">
          <div class="feature-item">
            <span class="feature-icon">🔮</span>
            <span class="feature-name">星盘解析</span>
            <span class="feature-desc">精准分析星座宫位分布</span>
          </div>
          <div class="feature-item">
            <span class="feature-icon">🌟</span>
            <span class="feature-name">星座运势</span>
            <span class="feature-desc">每日星座运势精准预测</span>
          </div>
          <div class="feature-item">
            <span class="feature-icon">🤖</span>
            <span class="feature-name">AI解读</span>
            <span class="feature-desc">智能星座性格分析</span>
          </div>
          <div class="feature-item">
            <span class="feature-icon">👥</span>
            <span class="feature-name">缘分匹配</span>
            <span class="feature-desc">星座配对指数分析</span>
          </div>
          <div class="feature-item">
            <span class="feature-icon">📈</span>
            <span class="feature-name">运势曲线</span>
            <span class="feature-desc">长期运势趋势分析</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { request } from '@/utils/request'

const router = useRouter()
const authStore = useAuthStore()

const activeTab = ref('my')
const myCharts = ref([])
const helpedCharts = ref([])

const isLoggedIn = computed(() => authStore.isLoggedIn)
const hasChart = computed(() => myCharts.value.length > 0)
const defaultChart = computed(() => {
  return myCharts.value.find(c => c.is_default) || myCharts.value[0] || null
})

async function loadCharts(type) {
  try {
    const res = await request.get(`/users/me/charts?type=${type}`)
    if (type === 'my') {
      myCharts.value = res || []
    } else {
      helpedCharts.value = res || []
    }
  } catch (e) {
    console.error('加载星盘失败', e)
  }
}

function goDetail(id) {
  router.push(`/chart-detail/${id}`)
}

function goBaziInput() {
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
    router.push('/birth-input')
  }
}

onMounted(() => {
  if (isLoggedIn.value) {
    loadCharts('my')
    loadCharts('helped')
  }
})
</script>

<style scoped>
.index-page {
  min-height: 100%;
}

.header {
  text-align: center;
  padding: 60rpx 0 40rpx;
}

.main-title {
  font-size: 64rpx;
  font-weight: 700;
  color: #c9a050;
  letter-spacing: 12rpx;
}

.sub-title {
  font-size: 24rpx;
  color: #8888a0;
  margin-left: 16rpx;
  letter-spacing: 4rpx;
}

.slogan {
  font-size: 26rpx;
  color: #666680;
  margin-top: 16rpx;
  letter-spacing: 4rpx;
}

.welcome-card {
  text-align: center;
  padding: 60rpx 32rpx;
}

.welcome-title {
  font-size: 36rpx;
  font-weight: 600;
  color: #e0e0f0;
  margin-bottom: 16rpx;
}

.welcome-desc {
  font-size: 26rpx;
  color: #8888a0;
  margin-bottom: 40rpx;
}

.tab-bar-page {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 32rpx;
  gap: 80rpx;
}

.tab-item-page {
  position: relative;
  font-size: 30rpx;
  color: #8888a0;
  padding: 16rpx 8rpx;
  cursor: pointer;
}

.tab-item-page.active {
  color: #c9a050;
  font-weight: 600;
}

.tab-item-page.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 40rpx;
  height: 4rpx;
  background: #c9a050;
  border-radius: 2rpx;
}

.no-chart-card {
  text-align: center;
  padding: 60rpx 32rpx;
}

.no-chart-icon {
  font-size: 80rpx;
  margin-bottom: 20rpx;
}

.no-chart-title {
  font-size: 32rpx;
  color: #e0e0f0;
  margin-bottom: 12rpx;
}

.no-chart-desc {
  font-size: 26rpx;
  color: #8888a0;
  margin-bottom: 40rpx;
}

.chart-overview {
  background: linear-gradient(135deg, rgba(30, 30, 60, 0.9) 0%, rgba(20, 20, 45, 0.95) 100%);
  border: 1rpx solid rgba(201, 160, 80, 0.3);
  border-radius: 24rpx;
  padding: 36rpx;
  margin-bottom: 32rpx;
  cursor: pointer;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24rpx;
}

.chart-name {
  font-size: 34rpx;
  font-weight: 600;
  color: #e0e0f0;
}

.chart-badge {
  font-size: 22rpx;
  color: #c9a050;
  background: rgba(201, 160, 80, 0.15);
  padding: 6rpx 16rpx;
  border-radius: 20rpx;
}

.chart-info {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
  margin-bottom: 24rpx;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-label {
  font-size: 26rpx;
  color: #8888a0;
}

.info-value {
  font-size: 26rpx;
  color: #e0e0f0;
}

.chart-action {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12rpx;
  padding-top: 20rpx;
  border-top: 1rpx solid rgba(201, 160, 80, 0.15);
  color: #c9a050;
  font-size: 28rpx;
}

.arrow {
  font-size: 28rpx;
}

.quick-actions {
  display: flex;
  justify-content: space-around;
  margin-bottom: 40rpx;
}

.action-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12rpx;
  cursor: pointer;
}

.action-icon {
  font-size: 44rpx;
}

.action-text {
  font-size: 24rpx;
  color: #8888a0;
}

.list-title {
  font-size: 28rpx;
  color: #8888a0;
  margin-bottom: 20rpx;
}

.chart-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(30, 30, 60, 0.9);
  border: 1rpx solid rgba(201, 160, 80, 0.2);
  border-radius: 16rpx;
  padding: 28rpx 32rpx;
  margin-bottom: 20rpx;
  cursor: pointer;
}

.chart-card-left {
  flex: 1;
}

.chart-card-name {
  font-size: 30rpx;
  font-weight: 600;
  color: #e0e0f0;
  display: block;
  margin-bottom: 8rpx;
}

.chart-card-meta {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.chart-card-tag {
  font-size: 20rpx;
  color: #c9a050;
  background: rgba(201, 160, 80, 0.15);
  padding: 4rpx 12rpx;
  border-radius: 12rpx;
}

.chart-card-desc {
  font-size: 24rpx;
  color: #8888a0;
}

.chart-card-right {
  color: #c9a050;
}

.feature-section {
  margin-top: 20rpx;
}

.feature-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20rpx;
}

.feature-item {
  background: rgba(20, 20, 45, 0.6);
  border: 1rpx solid rgba(201, 160, 80, 0.15);
  border-radius: 16rpx;
  padding: 30rpx;
}

.feature-icon {
  font-size: 40rpx;
  display: block;
  margin-bottom: 8rpx;
}

.feature-name {
  font-size: 28rpx;
  font-weight: 600;
  color: #e0e0f0;
  display: block;
  margin-bottom: 4rpx;
}

.feature-desc {
  font-size: 22rpx;
  color: #8888a0;
}
</style>
