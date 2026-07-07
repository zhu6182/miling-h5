<template>
  <div class="match-page">
    <div v-if="!isLoggedIn" class="welcome-card">
      <div class="welcome-title">请先登录</div>
      <div class="welcome-desc">登录后才能进行星座配对</div>
      <button class="btn-primary" @click="$router.push('/profile')">立即登录</button>
    </div>

    <div v-else class="container">
      <div class="match-header">
        <div class="header-title">星运日记</div>
        <div class="header-sub">星座配对，看看缘分</div>
      </div>

      <div class="match-type-selector">
        <div class="type-label">匹配维度</div>
        <div class="type-row">
          <div 
            class="type-item" 
            :class="{ active: matchType === 'love' }"
            @click="matchType = 'love'"
          >
            <div class="type-name">❤️ 姻缘</div>
            <div class="type-desc">爱情配对</div>
          </div>
          <div 
            class="type-item" 
            :class="{ active: matchType === 'career' }"
            @click="matchType = 'career'"
          >
            <div class="type-name">💼 事业</div>
            <div class="type-desc">事业搭档</div>
          </div>
          <div 
            class="type-item" 
            :class="{ active: matchType === 'all' }"
            @click="matchType = 'all'"
          >
            <div class="type-name">✨ 全部</div>
            <div class="type-desc">综合匹配</div>
          </div>
        </div>
      </div>

      <div class="action-cards">
        <div class="action-card primary" @click="generateQR">
          <div class="action-icon-large">📱</div>
          <div class="action-content">
            <div class="action-title">生成配对码</div>
            <div class="action-desc">让对方扫码，开启缘分测试</div>
          </div>
          <div class="action-arrow">→</div>
        </div>

        <div class="action-card" @click="scanQR">
          <div class="action-icon-large">🔍</div>
          <div class="action-content">
            <div class="action-title">扫码匹配</div>
            <div class="action-desc">扫描对方的配对二维码</div>
          </div>
          <div class="action-arrow">→</div>
        </div>

        <div class="action-card">
          <div class="action-icon-large">📡</div>
          <div class="action-content">
            <div class="action-title">NFC碰一碰</div>
            <div class="action-desc">开发中，敬请期待 <span class="coming-tag">开发中</span></div>
          </div>
        </div>
      </div>

      <div class="match-history">
        <div class="section-title">匹配历史</div>
        <div v-if="history.length === 0" class="loading-section">暂无匹配记录</div>
        <div v-else class="history-list">
          <div 
            v-for="item in history" 
            :key="item.id"
            class="history-item"
            @click="goMatchResult(item.id)"
          >
            <div class="history-users">
              <span class="user-name">{{ item.user_a_nickname }}</span>
              <span class="vs"> vs </span>
              <span class="user-name">{{ item.user_b_nickname || '对方' }}</span>
            </div>
            <div class="history-meta">
              <span 
                class="match-type-tag" 
                :class="{ love: item.match_type === 'love', career: item.match_type === 'career' }"
              >
                {{ getMatchTypeName(item.match_type) }}
              </span>
              <span class="history-score">匹配度 {{ item.overall_score || '--' }}%</span>
              <span class="history-status">{{ item.status }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showQRModal" class="qr-modal" @click="showQRModal = false">
      <div class="qr-content" @click.stop>
        <div class="qr-title">配对码</div>
        <div class="qr-desc">让对方扫描此码开始匹配</div>
        <div class="qr-image-wrapper">
          <img v-if="qrImage" :src="qrImage" class="qr-image" />
        </div>
        <div v-if="qrCode" class="qr-code-text">配对码：{{ qrCode }}</div>
        <div class="qr-tips">提示：对方打开扫码匹配即可</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { request } from '@/utils/request'

const router = useRouter()
const authStore = useAuthStore()

const matchType = ref('all')
const history = ref([])
const showQRModal = ref(false)
const qrCode = ref('')
const qrImage = ref('')

const isLoggedIn = ref(authStore.isLoggedIn)

function getMatchTypeName(type) {
  const names = { love: '姻缘', career: '事业', friendship: '友谊', all: '综合' }
  return names[type] || type
}

async function loadMatchHistory() {
  try {
    const res = await request.get('/match/history')
    history.value = res || []
  } catch (e) {
    console.error('加载匹配历史失败', e)
  }
}

async function generateQR() {
  try {
    const res = await request.post('/match/create-qr', { match_type: matchType.value })
    qrCode.value = res.qr_code
    qrImage.value = `${import.meta.env.VITE_API_URL || '/api/v1'}/match/qr/${res.qr_code}/image`
    showQRModal.value = true
  } catch (e) {
    console.error('生成配对码失败', e)
    alert('生成配对码失败')
  }
}

async function scanQR() {
  alert('请使用手机浏览器扫描功能扫描配对码')
}

function goMatchResult(id) {
  router.push(`/match-result/${id}`)
}

onMounted(() => {
  if (isLoggedIn.value) {
    loadMatchHistory()
  }
})
</script>

<style scoped>
.match-page {
  min-height: 100%;
}

.welcome-card {
  text-align: center;
  padding: 80rpx 32rpx;
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

.match-header {
  text-align: center;
  padding: 40rpx 0;
}

.header-title {
  font-size: 48rpx;
  font-weight: 700;
  color: #c9a050;
  margin-bottom: 8rpx;
}

.header-sub {
  font-size: 26rpx;
  color: #8888a0;
}

.match-type-selector {
  margin-bottom: 32rpx;
}

.type-label {
  font-size: 28rpx;
  color: #e0e0f0;
  margin-bottom: 16rpx;
}

.type-row {
  display: flex;
  gap: 12rpx;
}

.type-item {
  flex: 1;
  padding: 24rpx;
  text-align: center;
  background: rgba(10, 10, 26, 0.6);
  border: 1rpx solid rgba(201, 160, 80, 0.2);
  border-radius: 12rpx;
  cursor: pointer;
}

.type-item.active {
  border-color: #c9a050;
  background: rgba(201, 160, 80, 0.1);
}

.type-name {
  font-size: 28rpx;
  color: #e0e0f0;
  margin-bottom: 4rpx;
}

.type-desc {
  font-size: 22rpx;
  color: #8888a0;
}

.action-cards {
  margin-bottom: 32rpx;
}

.action-card {
  display: flex;
  align-items: center;
  padding: 28rpx;
  background: rgba(20, 20, 45, 0.8);
  border: 1rpx solid rgba(201, 160, 80, 0.2);
  border-radius: 20rpx;
  margin-bottom: 16rpx;
  cursor: pointer;
}

.action-card.primary {
  border-color: #c9a050;
  background: linear-gradient(135deg, rgba(201, 160, 80, 0.1), rgba(30, 30, 60, 0.9));
}

.action-icon-large {
  font-size: 48rpx;
  margin-right: 24rpx;
}

.action-content {
  flex: 1;
}

.action-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #e0e0f0;
  margin-bottom: 4rpx;
}

.action-desc {
  font-size: 24rpx;
  color: #8888a0;
}

.action-arrow {
  color: #c9a050;
  font-size: 32rpx;
}

.coming-tag {
  font-size: 20rpx;
  color: #666680;
  background: rgba(255, 255, 255, 0.1);
  padding: 4rpx 12rpx;
  border-radius: 12rpx;
}

.match-history {
  margin-bottom: 32rpx;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.history-item {
  background: rgba(20, 20, 45, 0.8);
  border: 1rpx solid rgba(201, 160, 80, 0.2);
  border-radius: 20rpx;
  padding: 24rpx;
  cursor: pointer;
}

.history-users {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-bottom: 12rpx;
}

.user-name {
  font-size: 28rpx;
  color: #e0e0f0;
}

.vs {
  color: #c9a050;
}

.history-meta {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.match-type-tag {
  font-size: 20rpx;
  color: #c9a050;
  background: rgba(201, 160, 80, 0.15);
  padding: 4rpx 12rpx;
  border-radius: 12rpx;
}

.match-type-tag.love { color: #ff6b9d; background: rgba(255, 107, 157, 0.15); }
.match-type-tag.career { color: #4facfe; background: rgba(79, 172, 254, 0.15); }

.history-score {
  font-size: 24rpx;
  color: #c9a050;
  font-weight: 600;
}

.history-status {
  font-size: 22rpx;
  color: #8888a0;
  margin-left: auto;
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

.qr-image-wrapper {
  margin-bottom: 24rpx;
}

.qr-image {
  width: 400rpx;
  height: 400rpx;
}

.qr-code-text {
  font-size: 24rpx;
  color: #c9a050;
  margin-bottom: 24rpx;
}

.qr-tips {
  font-size: 24rpx;
  color: #8888a0;
}

.loading-section {
  text-align: center;
  padding: 40rpx;
  color: #8888a0;
}
</style>
