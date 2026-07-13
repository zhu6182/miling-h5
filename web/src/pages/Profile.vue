<template>
  <div class="page-container">
    <div v-if="!isLoggedIn" class="login-section">
      <div class="login-card">
        <div class="card-glow"></div>
        <div class="login-logo">
          <div class="logo-ring">
            <div class="logo-core">
              <span class="logo-symbol">☽</span>
            </div>
            <div class="ring-orbit"></div>
          </div>
        </div>
        <h1 class="login-title">命里</h1>
        <p class="login-desc">命理玄机，探索命运的奥秘</p>
        <div class="form-tabs">
          <button class="form-tab" :class="{ active: activeTab === 'login' }" @click="activeTab = 'login'">登录</button>
          <button class="form-tab" :class="{ active: activeTab === 'register' }" @click="activeTab = 'register'">注册</button>
        </div>
        <div class="login-form">
          <div class="input-wrap">
            <label for="username" class="input-label">用户名</label>
            <input type="text" id="username" class="login-input" v-model="username" placeholder="请输入用户名" autocomplete="username" />
            <span class="input-icon">👤</span>
          </div>
          <div class="input-wrap">
            <label for="password" class="input-label">密码</label>
            <input type="password" id="password" class="login-input" v-model="password" placeholder="请输入密码" autocomplete="current-password" />
            <span class="input-icon">🔒</span>
          </div>
          <div v-if="activeTab === 'register'" class="input-wrap">
            <label for="confirmPassword" class="input-label">确认密码</label>
            <input type="password" id="confirmPassword" class="login-input" v-model="confirmPassword" placeholder="确认密码" autocomplete="new-password" />
            <span class="input-icon">🔒</span>
          </div>
          <button class="submit-btn" :class="{ disabled: loading }" @click="submit">
            <span v-if="activeTab === 'login'">{{ loading ? '登录中...' : '登 录' }}</span>
            <span v-else>{{ loading ? '注册中...' : '注 册' }}</span>
          </button>
        </div>
      </div>
    </div>

    <div v-else class="profile-content">
      <div class="profile-header">
        <div class="header-glow"></div>
        <div class="user-info">
          <div class="avatar">
            <span class="avatar-icon">👤</span>
            <div class="avatar-ring"></div>
          </div>
          <div class="user-detail">
            <h2 class="user-name">{{ userInfo.nickname || '用户' }}</h2>
            <p class="user-id">ID: {{ userInfo.id }}</p>
          </div>
        </div>
        <button class="sign-out-btn" @click="signOut">退出登录</button>
      </div>

      <div class="stats-card">
        <div class="stat-item">
          <span class="stat-value">{{ userInfo.sign_days || 0 }}</span>
          <span class="stat-label">签到天数</span>
          <div class="stat-glow"></div>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-item">
          <span class="stat-value">{{ userInfo.coin || 0 }}</span>
          <span class="stat-label">命币</span>
          <div class="stat-glow"></div>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-item">
          <span class="stat-value">{{ chartCount }}</span>
          <span class="stat-label">命盘数</span>
          <div class="stat-glow"></div>
        </div>
      </div>

      <div class="menu-card">
        <div class="menu-item" @click="goTo('/chart-input')">
          <div class="menu-icon-wrapper">
            <span class="menu-icon">☯</span>
            <div class="icon-glow"></div>
          </div>
          <span class="menu-text">新建命盘</span>
          <span class="menu-arrow">→</span>
        </div>
        <div class="menu-item" @click="goTo('/fortune')">
          <div class="menu-icon-wrapper">
            <span class="menu-icon">📅</span>
            <div class="icon-glow"></div>
          </div>
          <span class="menu-text">今日运势</span>
          <span class="menu-arrow">→</span>
        </div>
        <div class="menu-item" @click="goTo('/life-kline')">
          <div class="menu-icon-wrapper">
            <span class="menu-icon">📈</span>
            <div class="icon-glow"></div>
          </div>
          <span class="menu-text">人生K线</span>
          <span class="menu-arrow">→</span>
        </div>
        <div class="menu-item" @click="goTo('/match')">
          <div class="menu-icon-wrapper">
            <span class="menu-icon">💑</span>
            <div class="icon-glow"></div>
          </div>
          <span class="menu-text">八字合缘</span>
          <span class="menu-arrow">→</span>
        </div>
        <div class="menu-item" @click="onFeedback">
          <div class="menu-icon-wrapper">
            <span class="menu-icon">💬</span>
            <div class="icon-glow"></div>
          </div>
          <span class="menu-text">意见反馈</span>
          <span class="menu-arrow">→</span>
        </div>
        <div class="menu-item" @click="onAbout">
          <div class="menu-icon-wrapper">
            <span class="menu-icon">ℹ️</span>
            <div class="icon-glow"></div>
          </div>
          <span class="menu-text">关于我们</span>
          <span class="menu-arrow">→</span>
        </div>
      </div>

      <div v-if="charts.length > 0" class="charts-section">
        <div class="section-header">
          <span class="section-icon">📋</span>
          <span class="section-title">我的命盘</span>
          <span class="section-more" @click="goTo('/charts')">全部 →</span>
        </div>
        <div class="chart-list">
          <div class="chart-item" v-for="c in charts" :key="c.id">
            <div class="chart-info" @click="goTo(`/chart-detail/${c.id}`)">
              <h4 class="chart-name">{{ c.name }}</h4>
              <p class="chart-meta">{{ c.solar_date }} · {{ c.hour_name }}</p>
            </div>
            <div class="chart-actions">
              <button class="delete-btn" @click.stop="deleteChart(c.id)">删除</button>
              <span class="chart-arrow" @click="goTo(`/chart-detail/${c.id}`)">→</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onActivated, computed } from 'vue'
import { useRouter } from 'vue-router'
import { request } from '@/utils/request'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const activeTab = ref('login')
const username = ref('')
const password = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const charts = ref([])

const isLoggedIn = computed(() => authStore.isLoggedIn)
const userInfo = computed(() => authStore.user || {})
const chartCount = ref(0)

async function checkLogin() {
  if (authStore.token) {
    try {
      const res = await request.get('/users/me')
      authStore.setUser(res)
      loadCharts()
    } catch (e) {
      // token无效才登出，网络错误不清除登录状态
      if (e.response?.status === 401) {
        authStore.logout()
      }
    }
  }
}

async function submit() {
  if (!username.value || !password.value) {
    alert('请输入用户名和密码')
    return
  }
  if (activeTab.value === 'register') {
    if (!confirmPassword.value) {
      alert('请确认密码')
      return
    }
    if (password.value !== confirmPassword.value) {
      alert('两次输入的密码不一致')
      return
    }
  }
  loading.value = true
  try {
    if (activeTab.value === 'login') {
      const res = await request.post('/auth/login', { username: username.value, password: password.value })
      authStore.setToken(res.access_token)
      authStore.setUser(res.user)
    } else {
      const res = await request.post('/auth/register', { username: username.value, password: password.value })
      authStore.setToken(res.access_token)
      authStore.setUser(res.user)
    }
    loadCharts()
  } catch (e) {
    alert(e.response?.data?.detail || '操作失败')
  } finally {
    loading.value = false
  }
}

async function loadCharts() {
  try {
    const res = await request.get('/charts')
    charts.value = res.slice(0, 3)
    chartCount.value = res.length
  } catch (e) {
    console.error('加载星盘列表失败', e)
  }
}

function signOut() {
  authStore.logout()
  charts.value = []
}

function goTo(path) {
  router.push(path)
}

async function deleteChart(chartId) {
  if (!confirm('确定要删除这个命盘吗？')) return
  try {
    await request.delete(`/charts/${chartId}`)
    loadCharts()
    alert('删除成功')
  } catch (e) {
    alert(e.response?.data?.detail || '删除失败')
  }
}

function onFeedback() {
  alert('意见反馈功能开发中')
}

function onAbout() {
  alert('命里 v1.0.0\n星辰指引，遇见更好的自己')
}

const hasLoaded = ref(false)

onMounted(() => {
  if (!hasLoaded.value) {
    checkLogin()
    hasLoaded.value = true
  }
})

onActivated(() => {
  if (authStore.isLoggedIn && chartCount.value === 0) {
    loadCharts()
  }
})
</script>

<style scoped>
.login-section {
  padding: 60px 24px;
}

.login-card {
  background: rgba(18, 18, 35, 0.8);
  border: 1px solid rgba(212, 175, 55, 0.15);
  border-radius: var(--radius-lg);
  padding: 48px 32px;
  text-align: center;
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  position: relative;
  overflow: hidden;
}

.card-glow {
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle at 50% 50%, rgba(139, 92, 246, 0.1) 0%, transparent 60%);
  pointer-events: none;
}

.login-logo {
  margin-bottom: 24px;
}

.logo-ring {
  position: relative;
  width: 80px;
  height: 80px;
  margin: 0 auto;
}

.logo-core {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 40px;
  height: 40px;
  background: radial-gradient(circle, rgba(212, 175, 55, 0.3) 0%, rgba(139, 92, 246, 0.15) 50%, transparent 70%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: pulse-glow 3s ease-in-out infinite;
}

@keyframes pulse-glow {
  0%, 100% { box-shadow: 0 0 15px rgba(212, 175, 55, 0.2); }
  50% { box-shadow: 0 0 30px rgba(212, 175, 55, 0.4), 0 0 50px rgba(139, 92, 246, 0.2); }
}

.logo-symbol {
  font-size: 24px;
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
  animation: rotate 20s linear infinite;
}

@keyframes rotate {
  from { transform: translate(-50%, -50%) rotate(0deg); }
  to { transform: translate(-50%, -50%) rotate(360deg); }
}

.login-title {
  font-family: 'Cinzel', serif;
  font-size: 36px;
  font-weight: 700;
  background: linear-gradient(135deg, var(--gold-primary) 0%, var(--gold-secondary) 50%, var(--purple-secondary) 100%);
  background-size: 200% 200%;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 12px;
  animation: gradient-shift 4s ease infinite;
}

@keyframes gradient-shift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.login-desc {
  font-size: 14px;
  color: var(--text-muted);
  margin-bottom: 28px;
}

.form-tabs {
  display: flex;
  background: rgba(255, 255, 255, 0.03);
  border-radius: var(--radius-md);
  padding: 4px;
  margin-bottom: 24px;
  gap: 4px;
}

.form-tab {
  flex: 1;
  text-align: center;
  padding: 12px 0;
  font-size: 15px;
  color: var(--text-muted);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
  border: none;
  background: transparent;
}

.form-tab:focus-visible {
  outline: 2px solid var(--gold-primary);
  outline-offset: 2px;
}

.form-tab.active {
  background: linear-gradient(135deg, rgba(212, 175, 55, 0.15) 0%, rgba(139, 92, 246, 0.1) 100%);
  color: var(--gold-primary);
  font-weight: 600;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.input-wrap {
  position: relative;
}

.input-label {
  position: absolute;
  top: -8px;
  left: 14px;
  font-size: 11px;
  color: var(--text-muted);
  background: var(--bg-deep);
  padding: 0 6px;
  z-index: 1;
}

.login-input {
  width: 100%;
  padding: 16px 24px 16px 52px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(212, 175, 55, 0.15);
  border-radius: var(--radius-md);
  font-size: 15px;
  color: var(--text-primary);
  box-sizing: border-box;
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
}

.login-input:focus-visible {
  outline: 2px solid var(--gold-primary);
  outline-offset: 2px;
  border-color: var(--gold-primary);
  box-shadow: 0 0 20px rgba(212, 175, 55, 0.15);
}

.login-input::placeholder {
  color: var(--text-dim);
}

.input-icon {
  position: absolute;
  left: 18px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 18px;
  color: var(--text-muted);
}

.submit-btn {
  background: linear-gradient(135deg, var(--gold-primary) 0%, var(--gold-secondary) 100%);
  color: #0a0a15;
  border-radius: var(--radius-md);
  padding: 16px;
  text-align: center;
  font-size: 16px;
  font-weight: 600;
  font-family: 'Cinzel', serif;
  letter-spacing: 2px;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 12px;
  border: none;
  position: relative;
  overflow: hidden;
}

.submit-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
  transition: left 0.6s;
}

.submit-btn:hover::before {
  left: 100%;
}

.submit-btn:hover {
  box-shadow: 0 0 40px rgba(212, 175, 55, 0.5);
}

.submit-btn.disabled {
  opacity: 0.6;
}

.profile-content {
  padding: 0 24px;
}

.profile-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 32px 0;
  position: relative;
}

.header-glow {
  position: absolute;
  top: -50%;
  right: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle at 80% 20%, rgba(139, 92, 246, 0.06) 0%, transparent 50%);
  pointer-events: none;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.avatar {
  position: relative;
  width: 72px;
  height: 72px;
  background: rgba(212, 175, 55, 0.15);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-ring {
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  border: 1px solid rgba(212, 175, 55, 0.3);
  border-radius: 50%;
}

.avatar-icon {
  font-size: 32px;
}

.user-detail {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.user-name {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.user-id {
  font-size: 13px;
  color: var(--text-muted);
  margin: 0;
}

.sign-out-btn {
  font-size: 13px;
  color: var(--text-muted);
  padding: 8px 20px;
  border: 1px solid rgba(212, 175, 55, 0.2);
  border-radius: 20px;
  background: transparent;
  cursor: pointer;
  transition: all 0.3s ease;
}

.sign-out-btn:hover {
  background: rgba(212, 175, 55, 0.08);
}

.stats-card {
  display: flex;
  justify-content: space-around;
  align-items: center;
  background: rgba(18, 18, 35, 0.6);
  border: 1px solid rgba(212, 175, 55, 0.1);
  border-radius: var(--radius-lg);
  padding: 28px 0;
  margin-bottom: 20px;
  position: relative;
  overflow: hidden;
}

.stat-item {
  text-align: center;
  position: relative;
}

.stat-value {
  font-family: 'Cinzel', serif;
  font-size: 28px;
  font-weight: 700;
  color: var(--gold-primary);
  display: block;
}

.stat-label {
  font-size: 13px;
  color: var(--text-muted);
  margin-top: 6px;
  display: block;
}

.stat-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 40px;
  height: 40px;
  background: radial-gradient(circle, rgba(212, 175, 55, 0.1) 0%, transparent 70%);
  border-radius: 50%;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.stat-item:hover .stat-glow {
  opacity: 1;
}

.stat-divider {
  width: 1px;
  height: 48px;
  background: rgba(212, 175, 55, 0.1);
}

.menu-card {
  background: rgba(18, 18, 35, 0.6);
  border: 1px solid rgba(212, 175, 55, 0.1);
  border-radius: var(--radius-lg);
  margin-bottom: 20px;
  overflow: hidden;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 18px 20px;
  border-bottom: 1px solid rgba(212, 175, 55, 0.06);
  cursor: pointer;
  transition: all 0.3s ease;
}

.menu-item:last-child {
  border-bottom: none;
}

.menu-item:hover {
  background: rgba(255, 255, 255, 0.02);
}

.menu-icon-wrapper {
  position: relative;
  width: 40px;
  height: 40px;
  margin-right: 16px;
}

.menu-icon {
  font-size: 22px;
  position: relative;
  z-index: 1;
}

.icon-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 32px;
  height: 32px;
  background: radial-gradient(circle, rgba(212, 175, 55, 0.1) 0%, transparent 70%);
  border-radius: 50%;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.menu-item:hover .icon-glow {
  opacity: 1;
}

.menu-text {
  flex: 1;
  font-size: 15px;
  color: var(--text-primary);
}

.menu-arrow {
  font-size: 16px;
  color: var(--text-dim);
}

.charts-section {
  margin-bottom: 100px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}

.section-icon {
  font-size: 16px;
}

.section-title {
  font-size: 17px;
  font-weight: 600;
  color: var(--text-primary);
}

.section-more {
  font-size: 13px;
  color: var(--gold-primary);
  cursor: pointer;
}

.chart-list {
  background: rgba(18, 18, 35, 0.6);
  border: 1px solid rgba(212, 175, 55, 0.1);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.chart-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18px 20px;
  border-bottom: 1px solid rgba(212, 175, 55, 0.06);
  cursor: pointer;
  transition: all 0.3s ease;
}

.chart-item:last-child {
  border-bottom: none;
}

.chart-item:hover {
  background: rgba(255, 255, 255, 0.02);
}

.chart-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.chart-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.chart-meta {
  font-size: 13px;
  color: var(--text-muted);
  margin: 0;
}

.chart-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.delete-btn {
  font-size: 12px;
  color: #e06060;
  background: rgba(224, 96, 96, 0.1);
  border: 1px solid rgba(224, 96, 96, 0.2);
  padding: 6px 12px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.delete-btn:hover {
  background: rgba(224, 96, 96, 0.15);
}

.chart-arrow {
  font-size: 16px;
  color: var(--gold-primary);
  cursor: pointer;
}

@media (max-width: 380px) {
  .profile-content {
    padding: 0 14px;
  }

  .profile-header {
    padding: 20px 0;
  }

  .avatar {
    width: 56px;
    height: 56px;
  }

  .avatar-icon {
    font-size: 26px;
  }

  .user-info {
    gap: 10px;
  }

  .user-name {
    font-size: 17px;
  }

  .user-id {
    font-size: 11px;
  }

  .sign-out-btn {
    padding: 6px 14px;
    font-size: 12px;
  }

  .stats-card {
    padding: 20px 0;
  }

  .stat-value {
    font-size: 22px;
  }

  .stat-label {
    font-size: 11px;
  }

  .stat-divider {
    height: 36px;
  }

  .menu-item {
    padding: 14px 14px;
  }

  .menu-icon-wrapper {
    width: 34px;
    height: 34px;
    margin-right: 12px;
  }

  .menu-icon {
    font-size: 19px;
  }

  .menu-text {
    font-size: 14px;
  }

  .login-card {
    padding: 36px 20px;
  }

  .login-title {
    font-size: 30px;
  }

  .login-input {
    padding: 14px 20px 14px 46px;
    font-size: 14px;
  }

  .submit-btn {
    padding: 14px;
    font-size: 15px;
  }
}
</style>
