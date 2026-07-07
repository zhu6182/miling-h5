<template>
  <div class="profile-page">
    <div v-if="!isLoggedIn" class="profile-header">
      <div class="avatar-placeholder">👤</div>
      <button class="btn-primary mt-20" @click="showLoginModal = true">立即登录</button>
    </div>

    <div v-else class="container">
      <div class="profile-header">
        <div class="avatar">{{ user?.nickname?.charAt(0) || '星' }}</div>
        <div class="nickname">{{ user?.nickname || '星运用户' }}</div>
        <div class="phone">{{ user?.phone || '' }}</div>
      </div>

      <div class="menu-section">
        <div class="menu-item" @click="$router.push('/birth-input')">
          <span class="menu-icon">✨</span>
          <span class="menu-text">新建星盘</span>
          <span class="menu-arrow">›</span>
        </div>

        <div class="menu-item" @click="toggleFriends">
          <span class="menu-icon">👥</span>
          <span class="menu-text">我的好友</span>
          <span v-if="friends.length" class="menu-count">{{ friends.length }}</span>
          <span class="menu-arrow">›</span>
        </div>

        <div v-if="showFriends && friends.length > 0" class="friends-list">
          <div v-for="friend in friends" :key="friend.user_id" class="friend-item">
            <div class="friend-avatar">{{ friend.nickname?.charAt(0) || '友' }}</div>
            <div class="friend-info">
              <div class="friend-name">{{ friend.nickname }}</div>
              <div class="friend-soul">{{ friend.soul_palace }}守护星</div>
            </div>
            <div class="friend-actions">
              <button class="friend-btn match" @click="goMatchWithFriend(friend.user_id)">匹配</button>
              <button class="friend-btn remove" @click="removeFriend(friend.user_id)">删除</button>
            </div>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="section-title">AI 设置</div>
        <div class="ai-provider-row">
          <button 
            v-for="provider in aiProviders" 
            :key="provider.id"
            class="ai-provider-btn"
            :class="{ active: aiProvider === provider.id }"
            @click="selectAiProvider(provider.id)"
          >
            {{ provider.name }}
          </button>
        </div>
        <div v-if="aiProvider !== 'mock'" class="ai-settings">
          <div class="form-item">
            <label class="form-label">API Key</label>
            <input 
              type="password" 
              class="form-input" 
              v-model="aiApiKey" 
              placeholder="请输入 API Key"
            />
          </div>
          <div class="form-item">
            <label class="form-label">模型名称</label>
            <input 
              type="text" 
              class="form-input" 
              v-model="aiModel" 
              placeholder="模型名称"
            />
          </div>
          <div class="form-item">
            <label class="form-label">Base URL</label>
            <input 
              type="text" 
              class="form-input" 
              v-model="aiBaseUrl" 
              placeholder="API 地址"
            />
          </div>
          <button class="save-btn" @click="saveAiSettings">保存设置</button>
        </div>
      </div>

      <div class="card">
        <div class="section-title">服务地址设置</div>
        <div class="form-item">
          <label class="form-label">后端服务地址</label>
          <input 
            type="text" 
            class="form-input" 
            v-model="serverBaseUrl" 
            placeholder="后端服务地址"
          />
        </div>
        <div style="display: flex; gap: 12rpx;">
          <button class="btn-outline" @click="saveServerBaseUrl">保存</button>
          <button class="btn-outline" @click="resetServerBaseUrl">恢复默认</button>
        </div>
      </div>

      <button class="logout-btn" @click="logout">退出登录</button>

      <div class="menu-item">
        <span class="menu-icon">ℹ️</span>
        <span class="menu-text">关于「星运日记」</span>
        <span class="menu-arrow">›</span>
      </div>
    </div>

    <div v-if="showLoginModal" class="login-modal" @click="showLoginModal = false">
      <div class="modal-content-large" @click.stop>
        <div class="close-modal" @click="showLoginModal = false">×</div>
        <div class="modal-title-large">{{ isRegisterMode ? '注册账号' : '登录账号' }}</div>
        <div class="modal-subtitle">{{ isRegisterMode ? '创建新账号开始探索' : '登录你的账号' }}</div>
        
        <div class="form-item">
          <label class="form-label">手机号</label>
          <input type="tel" class="form-input" v-model="loginPhone" placeholder="请输入手机号" />
        </div>
        
        <div class="form-item">
          <label class="form-label">密码</label>
          <input type="password" class="form-input" v-model="loginPassword" placeholder="请输入密码" />
        </div>

        <div v-if="isRegisterMode" class="form-item">
          <label class="form-label">昵称</label>
          <input type="text" class="form-input" v-model="loginNickname" placeholder="请输入昵称" />
        </div>

        <button 
          class="btn-primary mt-20" 
          :disabled="loading"
          @click="handleAuth"
        >
          {{ loading ? '处理中...' : (isRegisterMode ? '注册' : '登录') }}
        </button>

        <div class="switch-mode" @click="isRegisterMode = !isRegisterMode">
          {{ isRegisterMode ? '已有账号？去登录' : '没有账号？去注册' }}
        </div>
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

const isLoggedIn = ref(authStore.isLoggedIn)
const user = ref(authStore.user)
const friends = ref([])
const showFriends = ref(false)

const showLoginModal = ref(false)
const isRegisterMode = ref(false)
const loginPhone = ref('')
const loginPassword = ref('')
const loginNickname = ref('')
const loading = ref(false)

const aiProvider = ref('mock')
const aiApiKey = ref('')
const aiModel = ref('gpt-3.5-turbo')
const aiBaseUrl = ref('')
const serverBaseUrl = ref('')

const aiProviders = [
  { id: 'mock', name: '内置' },
  { id: 'volcengine', name: '豆包' },
  { id: 'openai', name: 'OpenAI' },
  { id: 'tongyi', name: '通义' }
]

async function loadFriends() {
  try {
    const res = await request.get('/match/friends/list')
    friends.value = res || []
  } catch (e) {
    console.error('加载好友失败', e)
  }
}

function toggleFriends() {
  showFriends.value = !showFriends.value
}

function goMatchWithFriend(friendId) {
  router.push(`/match-result?friendId=${friendId}`)
}

async function removeFriend(friendId) {
  if (!confirm('确定删除该好友？')) return
  try {
    await request.delete(`/match/friends/${friendId}`)
    alert('已删除')
    loadFriends()
  } catch (e) {
    console.error('删除好友失败', e)
  }
}

function selectAiProvider(provider) {
  aiProvider.value = provider
  const defaults = {
    mock: { model: '', baseUrl: '' },
    volcengine: { model: 'doubao-pro-32k', baseUrl: 'https://ark.cn-beijing.volces.com/api/v3' },
    openai: { model: 'gpt-3.5-turbo', baseUrl: '' },
    tongyi: { model: 'qwen-turbo', baseUrl: '' }
  }
  const def = defaults[provider] || { model: '', baseUrl: '' }
  aiModel.value = def.model
  aiBaseUrl.value = def.baseUrl
}

async function saveAiSettings() {
  if (aiProvider.value !== 'mock' && !aiApiKey.value) {
    alert('请输入 API Key')
    return
  }
  try {
    const res = await request.put('/users/me', {
      ai_provider: aiProvider.value,
      ai_api_key: aiApiKey.value,
      ai_model: aiModel.value,
      ai_base_url: aiBaseUrl.value
    })
    authStore.setUser(res)
    user.value = res
    alert('保存成功')
  } catch (e) {
    console.error('保存失败', e)
  }
}

function saveServerBaseUrl() {
  const url = serverBaseUrl.value.trim()
  if (!url) {
    alert('请输入服务地址')
    return
  }
  localStorage.setItem('baseUrl', url)
  alert('保存成功，刷新页面生效')
}

function resetServerBaseUrl() {
  localStorage.removeItem('baseUrl')
  serverBaseUrl.value = ''
  alert('已恢复默认')
}

async function handleAuth() {
  if (!loginPhone.value || !loginPassword.value) {
    alert('请填写完整信息')
    return
  }
  loading.value = true
  try {
    if (isRegisterMode.value) {
      await authStore.register(loginPhone.value, loginPassword.value, loginNickname.value)
      alert('注册成功')
    } else {
      await authStore.login(loginPhone.value, loginPassword.value)
      alert('登录成功')
    }
    showLoginModal.value = false
    isLoggedIn.value = true
    user.value = authStore.user
    loadFriends()
  } catch (e) {
    alert(e.detail || '操作失败')
  } finally {
    loading.value = false
  }
}

async function logout() {
  if (!confirm('确定要退出登录吗？')) return
  authStore.logout()
  isLoggedIn.value = false
  user.value = null
  friends.value = []
  alert('已退出')
}

onMounted(() => {
  const customBaseUrl = localStorage.getItem('baseUrl')
  if (customBaseUrl) {
    serverBaseUrl.value = customBaseUrl
  }
  if (isLoggedIn.value) {
    aiProvider.value = user.value?.ai_provider || 'mock'
    aiApiKey.value = user.value?.ai_api_key || ''
    aiModel.value = user.value?.ai_model || 'gpt-3.5-turbo'
    aiBaseUrl.value = user.value?.ai_base_url || ''
    loadFriends()
  }
})
</script>

<style scoped>
.profile-page {
  min-height: 100%;
}

.profile-header {
  text-align: center;
  padding: 60rpx 0 40rpx;
}

.avatar {
  width: 120rpx;
  height: 120rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #c9a050 0%, #e0b868 100%);
  color: #1a1a2e;
  font-size: 48rpx;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20rpx;
}

.avatar-placeholder {
  font-size: 80rpx;
  margin-bottom: 20rpx;
}

.nickname {
  font-size: 34rpx;
  font-weight: 600;
  color: #e0e0f0;
  margin-bottom: 8rpx;
}

.phone {
  font-size: 26rpx;
  color: #8888a0;
}

.menu-section {
  margin-bottom: 24rpx;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 28rpx 32rpx;
  background: rgba(20, 20, 45, 0.8);
  border-radius: 20rpx;
  margin-bottom: 12rpx;
  cursor: pointer;
}

.menu-icon {
  font-size: 36rpx;
  margin-right: 20rpx;
}

.menu-text {
  flex: 1;
  font-size: 28rpx;
  color: #e0e0f0;
}

.menu-count {
  font-size: 24rpx;
  color: #c9a050;
  margin-right: 12rpx;
}

.menu-arrow {
  font-size: 32rpx;
  color: #666680;
}

.friends-list {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
  margin-top: 12rpx;
}

.friend-item {
  display: flex;
  align-items: center;
  padding: 24rpx;
  background: rgba(30, 30, 60, 0.9);
  border-radius: 16rpx;
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

.friend-actions {
  display: flex;
  gap: 12rpx;
}

.friend-btn {
  padding: 12rpx 20rpx;
  border-radius: 20rpx;
  font-size: 22rpx;
  cursor: pointer;
  border: none;
}

.friend-btn.match {
  background: rgba(201, 160, 80, 0.15);
  color: #c9a050;
}

.friend-btn.remove {
  background: rgba(244, 67, 54, 0.15);
  color: #f44336;
}

.form-item {
  margin-bottom: 24rpx;
}

.form-label {
  display: block;
  font-size: 26rpx;
  color: #8888a0;
  margin-bottom: 12rpx;
}

.form-input {
  width: 100%;
  background: rgba(10, 10, 26, 0.6);
  border: 1rpx solid rgba(201, 160, 80, 0.2);
  border-radius: 12rpx;
  padding: 24rpx;
  color: #e0e0f0;
  font-size: 28rpx;
  outline: none;
}

.form-input:focus {
  border-color: #c9a050;
}

.ai-provider-row {
  display: flex;
  gap: 12rpx;
  margin-bottom: 24rpx;
  flex-wrap: wrap;
}

.ai-provider-btn {
  flex: 1;
  min-width: 120rpx;
  padding: 16rpx;
  text-align: center;
  background: rgba(10, 10, 26, 0.6);
  border: 1rpx solid rgba(201, 160, 80, 0.2);
  border-radius: 12rpx;
  color: #8888a0;
  font-size: 24rpx;
  cursor: pointer;
}

.ai-provider-btn.active {
  border-color: #c9a050;
  color: #c9a050;
  background: rgba(201, 160, 80, 0.1);
}

.ai-settings {
  margin-top: 20rpx;
}

.save-btn {
  background: linear-gradient(135deg, #c9a050 0%, #e0b868 100%);
  color: #1a1a2e;
  border: none;
  padding: 24rpx;
  border-radius: 50rpx;
  font-size: 28rpx;
  font-weight: 600;
  cursor: pointer;
  width: 100%;
  margin-top: 16rpx;
}

.logout-btn {
  width: 100%;
  padding: 24rpx;
  background: transparent;
  border: 1rpx solid rgba(244, 67, 54, 0.5);
  color: #f44336;
  border-radius: 50rpx;
  font-size: 28rpx;
  cursor: pointer;
  margin-top: 40rpx;
}

.login-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.modal-content-large {
  background: #1a1a2e;
  border: 1rpx solid rgba(201, 160, 80, 0.2);
  border-radius: 20rpx;
  padding: 40rpx;
  width: 85%;
  max-width: 600rpx;
  position: relative;
}

.modal-title-large {
  font-size: 36rpx;
  font-weight: 600;
  color: #e0e0f0;
  text-align: center;
  margin-bottom: 12rpx;
}

.modal-subtitle {
  font-size: 26rpx;
  color: #8888a0;
  text-align: center;
  margin-bottom: 40rpx;
}

.close-modal {
  position: absolute;
  top: 20rpx;
  right: 24rpx;
  font-size: 36rpx;
  color: #666680;
  cursor: pointer;
}

.switch-mode {
  text-align: center;
  font-size: 26rpx;
  color: #c9a050;
  margin-top: 24rpx;
  cursor: pointer;
}

.mt-20 { margin-top: 20rpx; }
</style>
