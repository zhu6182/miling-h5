<template>
  <div class="chart-detail-page container">
    <div v-if="loading" class="loading-section">加载中...</div>

    <div v-else-if="chart">
      <div class="chart-detail-header">
        <div class="chart-detail-name">{{ chart.name }}</div>
        <div class="chart-detail-meta">
          <span class="meta-tag">{{ chart.five_elements }}</span>
          <span>{{ chart.solar_date }}</span>
          <span>{{ chart.hour_name }}</span>
        </div>
        <div style="display: flex; gap: 12rpx; margin-top: 16rpx;">
          <button class="btn-outline" @click="goBaziDetail">查看八字</button>
          <button class="btn-outline" @click="goLifeKline">人生K线</button>
          <button class="btn-outline" @click="openMatchSelector">找人匹配</button>
        </div>
      </div>

      <div class="sihua-tags">
        <span v-if="chart.chart_data?.sihua?.lu" class="sihua-tag lu">化禄</span>
        <span v-if="chart.chart_data?.sihua?.quan" class="sihua-tag quan">化权</span>
        <span v-if="chart.chart_data?.sihua?.ke" class="sihua-tag ke">化科</span>
        <span v-if="chart.chart_data?.sihua?.ji" class="sihua-tag ji">化忌</span>
      </div>

      <div class="palace-grid">
        <div v-for="(cell, index) in palaceGrid" :key="index" class="palace-cell" :class="{ 'palace-center': cell.center }">
          <div v-if="cell.center">
            <div class="palace-name">星盘</div>
            <div class="palace-main-star">{{ chart.soul_palace }}宫</div>
            <div class="palace-sub-star">{{ chart.five_elements }}</div>
          </div>
          <div v-else>
            <div class="palace-name">{{ cell.name }}</div>
            <div class="palace-main-star">{{ cell.mainStar }}</div>
            <div v-if="cell.subStars" class="palace-sub-star">{{ cell.subStars }}</div>
          </div>
        </div>
      </div>

      <div class="reading-section">
        <div class="section-title">AI 解读</div>
        <button v-if="!readingData" class="btn-primary" @click="generateReading">生成解读</button>
        <div v-else class="reading-card">
          <div class="reading-title">星盘分析</div>
          <div class="reading-body" v-html="readingData"></div>
        </div>
      </div>
    </div>

    <div v-else class="loading-section">星盘不存在</div>

    <div v-if="showMatchModal" class="qr-modal" @click="showMatchModal = false">
      <div class="qr-content" @click.stop>
        <div class="qr-title">选择匹配对象</div>
        <div class="qr-desc">选择一个星盘进行匹配</div>
        <div class="friends-list">
          <div v-for="c in charts" :key="c.id" class="friend-item" @click="selectChartForMatch(c.id)">
            <div class="friend-avatar">{{ c.name?.charAt(0) || '星' }}</div>
            <div class="friend-info">
              <div class="friend-name">{{ c.name }}</div>
              <div class="friend-soul">{{ c.soul_palace }}</div>
            </div>
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
const readingData = ref('')
const showMatchModal = ref(false)
const charts = ref([])

const palaceGrid = computed(() => {
  if (!chart.value?.chart_data?.palaces) {
    return []
  }
  const palaces = chart.value.chart_data.palaces
  return [
    { name: palaces[0]?.name || '命宫', mainStar: palaces[0]?.mainStar || '', subStars: palaces[0]?.subStars?.join(', ') || '' },
    { name: palaces[1]?.name || '财帛', mainStar: palaces[1]?.mainStar || '', subStars: palaces[1]?.subStars?.join(', ') || '' },
    { name: palaces[2]?.name || '兄弟', mainStar: palaces[2]?.mainStar || '', subStars: palaces[2]?.subStars?.join(', ') || '' },
    { name: palaces[3]?.name || '田宅', mainStar: palaces[3]?.mainStar || '', subStars: palaces[3]?.subStars?.join(', ') || '' },
    { name: palaces[11]?.name || '父母', mainStar: palaces[11]?.mainStar || '', subStars: palaces[11]?.subStars?.join(', ') || '' },
    { center: true },
    { name: palaces[4]?.name || '子女', mainStar: palaces[4]?.mainStar || '', subStars: palaces[4]?.subStars?.join(', ') || '' },
    { name: palaces[5]?.name || '奴仆', mainStar: palaces[5]?.mainStar || '', subStars: palaces[5]?.subStars?.join(', ') || '' },
    { name: palaces[10]?.name || '迁移', mainStar: palaces[10]?.mainStar || '', subStars: palaces[10]?.subStars?.join(', ') || '' },
    { name: palaces[9]?.name || '疾厄', mainStar: palaces[9]?.mainStar || '', subStars: palaces[9]?.subStars?.join(', ') || '' },
    { name: palaces[8]?.name || '官禄', mainStar: palaces[8]?.mainStar || '', subStars: palaces[8]?.subStars?.join(', ') || '' },
    { name: palaces[7]?.name || '福德', mainStar: palaces[7]?.mainStar || '', subStars: palaces[7]?.subStars?.join(', ') || '' },
    { name: palaces[6]?.name || '夫妻', mainStar: palaces[6]?.mainStar || '', subStars: palaces[6]?.subStars?.join(', ') || '' }
  ]
})

async function loadChart() {
  try {
    const res = await request.get(`/charts/${route.params.id}`)
    chart.value = res
    if (res.reading_data) {
      readingData.value = res.reading_data.body || ''
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

function goLifeKline() {
  router.push({
    path: '/life-kline',
    query: {
      date_str: chart.value.solar_date,
      hour_index: chart.value.hour_index,
      gender: chart.value.gender
    }
  })
}

async function generateReading() {
  try {
    const res = await request.post(`/charts/${route.params.id}/reading/start`, { ad_watched: true })
    const taskId = res.task_id
    let status = 'processing'
    while (status === 'processing') {
      await new Promise(r => setTimeout(r, 2000))
      const statusRes = await request.get(`/charts/${route.params.id}/reading/status?task_id=${taskId}`)
      status = statusRes.status
      if (status === 'completed') {
        readingData.value = statusRes.result?.reading?.body || ''
        alert('解读生成完成')
      } else if (status === 'failed') {
        alert('生成失败')
        break
      }
    }
  } catch (e) {
    console.error('生成解读失败', e)
    alert('生成失败')
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

onMounted(() => {
  loadChart()
})
</script>

<style scoped>
.chart-detail-page {
  padding: 24rpx;
}

.loading-section {
  text-align: center;
  padding: 80rpx 0;
  color: #8888a0;
}

.chart-detail-header {
  background: rgba(20, 20, 45, 0.8);
  border-radius: 20rpx;
  padding: 32rpx;
  margin-bottom: 24rpx;
}

.chart-detail-name {
  font-size: 36rpx;
  font-weight: 700;
  color: #c9a050;
  margin-bottom: 16rpx;
}

.chart-detail-meta {
  font-size: 24rpx;
  color: #8888a0;
}

.meta-tag {
  font-size: 22rpx;
  color: #c9a050;
  background: rgba(201, 160, 80, 0.15);
  padding: 4rpx 12rpx;
  border-radius: 12rpx;
  margin-right: 12rpx;
}

.sihua-tags {
  display: flex;
  gap: 12rpx;
  margin-bottom: 24rpx;
  flex-wrap: wrap;
}

.sihua-tag {
  font-size: 22rpx;
  padding: 6rpx 16rpx;
  border-radius: 20rpx;
}

.sihua-tag.lu { background: rgba(76, 175, 80, 0.15); color: #4caf50; }
.sihua-tag.quan { background: rgba(244, 67, 54, 0.15); color: #f44336; }
.sihua-tag.ke { background: rgba(79, 172, 254, 0.15); color: #4facfe; }
.sihua-tag.ji { background: rgba(128, 128, 128, 0.15); color: #888; }

.palace-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 4rpx;
  margin-bottom: 24rpx;
  background: rgba(201, 160, 80, 0.2);
  border-radius: 20rpx;
  overflow: hidden;
}

.palace-cell {
  background: rgba(20, 20, 45, 0.8);
  padding: 12rpx;
  min-height: 120rpx;
}

.palace-center {
  background: linear-gradient(135deg, rgba(201, 160, 80, 0.2), rgba(30, 30, 60, 0.9));
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.palace-name {
  font-size: 20rpx;
  color: #8888a0;
  margin-bottom: 4rpx;
}

.palace-main-star {
  font-size: 22rpx;
  color: #c9a050;
  font-weight: 600;
  margin-bottom: 4rpx;
}

.palace-sub-star {
  font-size: 18rpx;
  color: #666680;
}

.reading-section {
  margin-bottom: 24rpx;
}

.reading-card {
  background: rgba(20, 20, 45, 0.8);
  border-radius: 20rpx;
  padding: 24rpx;
  margin-top: 16rpx;
}

.reading-title {
  font-size: 28rpx;
  font-weight: 600;
  color: #c9a050;
  margin-bottom: 12rpx;
}

.reading-body {
  font-size: 26rpx;
  color: #e0e0f0;
  line-height: 1.6;
}

.reading-body h3 {
  color: #c9a050;
  margin: 16rpx 0 8rpx;
}

.reading-body p {
  margin-bottom: 12rpx;
}

.qr-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.qr-content {
  background: #1a1a2e;
  border-radius: 20rpx;
  padding: 40rpx;
  text-align: center;
  max-width: 80%;
  max-height: 80%;
  overflow-y: auto;
}

.qr-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #e0e0f0;
  margin-bottom: 12rpx;
}

.qr-desc {
  font-size: 26rpx;
  color: #8888a0;
  margin-bottom: 24rpx;
}

.friends-list {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.friend-item {
  display: flex;
  align-items: center;
  padding: 24rpx;
  background: rgba(30, 30, 60, 0.9);
  border-radius: 16rpx;
  cursor: pointer;
}

.friend-avatar {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #c9a050 0%, #e0b868 100%);
  color: #1a1a2e;
  font-size: 32rpx;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20rpx;
}

.friend-info {
  flex: 1;
}

.friend-name {
  font-size: 28rpx;
  color: #e0e0f0;
}

.friend-soul {
  font-size: 22rpx;
  color: #8888a0;
}
</style>
