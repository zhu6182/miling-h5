<template>
  <div class="page-container">
    <div v-if="!isLoggedIn" class="guest-wrap">
      <div class="guest-card">
        <div class="card-glow"></div>
        <div class="guest-icon">💫</div>
        <h2 class="guest-title">登录后解锁合缘功能</h2>
        <p class="guest-desc">八字合缘，探索你和TA的命理缘分</p>
        <button class="btn-primary" @click="$router.push('/profile')">立即登录</button>
      </div>
    </div>

    <div v-else class="match-content">
      <div class="match-hero">
        <div class="hero-glow"></div>
        <div class="hero-icon">💕</div>
        <h1 class="hero-title">八字合缘</h1>
        <p class="hero-sub">探索你与TA的命理缘分</p>
        <div class="hero-ornament">
          <span class="ornament-line"></span>
          <span class="ornament-dot">☯</span>
          <span class="ornament-line"></span>
        </div>
      </div>

      <div class="type-selector">
        <div class="type-label">
          <span class="label-icon">☯</span>
          选择合缘类型
        </div>
        <div class="type-grid">
          <div 
            class="type-card"
            :class="{ active: matchType === 'love' }"
            @click="matchType = 'love'"
          >
            <div class="type-icon love">💕</div>
            <div class="type-name">姻缘合缘</div>
            <div class="type-desc">八字婚配指数</div>
            <div class="type-glow love"></div>
          </div>
          <div 
            class="type-card"
            :class="{ active: matchType === 'career' }"
            @click="matchType = 'career'"
          >
            <div class="type-icon career">💼</div>
            <div class="type-name">事业合运</div>
            <div class="type-desc">命理默契指数</div>
            <div class="type-glow career"></div>
          </div>
          <div 
            class="type-card"
            :class="{ active: matchType === 'all' }"
            @click="matchType = 'all'"
          >
            <div class="type-icon all">☯</div>
            <div class="type-name">综合合缘</div>
            <div class="type-desc">全方位命理分析</div>
            <div class="type-glow all"></div>
          </div>
        </div>
      </div>

      <div class="action-section">
        <div class="action-card primary" @click="generateQR">
          <div class="action-icon-wrapper">
            <div class="action-icon">📱</div>
            <div class="icon-glow"></div>
          </div>
          <div class="action-info">
            <div class="action-title">生成合缘码</div>
            <div class="action-desc">让对方扫码，开启命理合缘</div>
          </div>
          <div class="action-arrow">→</div>
        </div>

        <div class="action-card" @click="scanQR">
          <div class="action-icon-wrapper">
            <div class="action-icon">🔍</div>
            <div class="icon-glow"></div>
          </div>
          <div class="action-info">
            <div class="action-title">扫码合缘</div>
            <div class="action-desc">扫描对方的合缘二维码</div>
          </div>
          <div class="action-arrow">→</div>
        </div>

        <div class="action-card disabled">
          <div class="action-icon-wrapper">
            <div class="action-icon">📡</div>
            <div class="icon-glow"></div>
          </div>
          <div class="action-info">
            <div class="action-title">NFC碰一碰</div>
            <div class="action-desc">开发中，敬请期待</div>
          </div>
          <span class="coming-tag">即将上线</span>
        </div>
      </div>

      <div class="history-section">
        <div class="section-header">
          <span class="section-icon">📋</span>
          <span class="section-title">合缘历史</span>
        </div>
        <div v-if="history.length === 0" class="empty-history">
          <div class="empty-icon">💫</div>
          <span class="empty-text">暂无匹配记录</span>
        </div>
        <div v-else class="history-list">
          <div 
            v-for="item in history" 
            :key="item.id"
            class="history-item"
            @click="goMatchResult(item.id)"
          >
            <div class="history-users">
              <div class="user-avatar a">{{ item.user_a_nickname?.charAt(0) || 'A' }}</div>
              <div class="vs-icon">✦</div>
              <div class="user-avatar b">{{ item.user_b_nickname?.charAt(0) || 'B' }}</div>
            </div>
            <div class="history-names">
              <span>{{ item.user_a_nickname }}</span>
              <span class="vs-text">vs</span>
              <span>{{ item.user_b_nickname || '对方' }}</span>
            </div>
            <div class="history-meta">
              <span class="match-type-tag" :class="item.match_type">
                {{ getMatchTypeName(item.match_type) }}
              </span>
              <span class="history-score">
                {{ item.overall_score || '--' }}%
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showQRModal" class="modal-overlay" @click="closeQRModal">
      <div class="qr-modal" @click.stop>
        <button class="modal-close" @click="closeQRModal">×</button>
        <div class="qr-header">
          <div class="qr-glow"></div>
          <div class="qr-icon">☯</div>
          <h3 class="qr-title">你的合缘码</h3>
          <p class="qr-desc">让对方扫描此二维码开始合缘</p>
        </div>
        <div class="qr-image-box">
          <img v-if="qrImage" :src="qrImage" class="qr-image" alt="配对码" />
          <div v-else class="qr-placeholder">生成中...</div>
        </div>
        <div v-if="qrCode" class="qr-code-text">
          <span class="code-label">合缘码</span>
          <span class="code-value">{{ qrCode }}</span>
        </div>
        <div class="qr-tip">💡 提示：对方打开「扫码合缘」即可</div>
      </div>
    </div>

    <div v-if="showScanner" class="scanner-overlay" @click="closeScanner">
      <div class="scanner-container" @click.stop>
        <div class="scanner-header">
          <button class="scanner-back" @click="closeScanner">✕</button>
          <span class="scanner-title">扫码合缘</span>
          <div style="width: 36px;"></div>
        </div>
        <div class="scanner-view">
          <video ref="videoRef" class="scanner-video" autoplay playsinline muted></video>
          <canvas ref="canvasRef" style="display: none;"></canvas>
          <div class="scan-frame" v-if="scanning">
            <div class="scan-corner tl"></div>
            <div class="scan-corner tr"></div>
            <div class="scan-corner bl"></div>
            <div class="scan-corner br"></div>
            <div class="scan-line" :class="{ active: scanning }"></div>
          </div>
          <div v-if="scanError" class="scan-error">{{ scanError }}</div>
          <div v-else-if="!scanning" class="scan-tip">正在启动相机...</div>
          <div v-else class="scan-tip">将合缘码放入框内</div>
          
          <div v-if="scanError && !scanning" class="album-fallback" @click="pickFromAlbum">
            <div class="album-icon">🖼️</div>
            <div class="album-text">从相册选择图片识别</div>
          </div>
        </div>
        <div class="scanner-actions">
          <button class="scan-btn" @click="toggleFlash" v-if="flashSupported">
            <span class="btn-icon">{{ flashOn ? '🔦' : '💡' }}</span>
            <span>{{ flashOn ? '关灯' : '开灯' }}</span>
          </button>
          <button class="scan-btn" @click="pickFromAlbum">
            <span class="btn-icon">🖼️</span>
            <span>相册</span>
          </button>
          <input ref="fileInputRef" type="file" accept="image/*" style="display: none;" @change="handleFileSelect">
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onActivated } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { request } from '@/utils/request'
import jsQR from 'jsqr'

const router = useRouter()
const authStore = useAuthStore()

const matchType = ref('all')
const history = ref([])
const showQRModal = ref(false)
const qrCode = ref('')
const qrImage = ref('')

const isLoggedIn = computed(() => authStore.isLoggedIn)

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
    console.error('生成合缘码失败', e)
    alert('生成合缘码失败')
  }
}

function closeQRModal() {
  showQRModal.value = false
}

// ==================== 扫码相关 ====================
const showScanner = ref(false)
const scanning = ref(false)
const scanError = ref('')
const videoRef = ref(null)
const canvasRef = ref(null)
const fileInputRef = ref(null)
const flashOn = ref(false)
const flashSupported = ref(false)
let stream = null
let scanTimer = null

async function scanQR() {
  showScanner.value = true
  scanError.value = ''
  scanning.value = false
  flashOn.value = false
  flashSupported.value = false
  await startCamera()
}

async function startCamera() {
  try {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      if (!window.isSecureContext) {
        scanError.value = '当前为HTTP环境，无法调用相机\n请使用HTTPS访问或选择相册识别'
      } else {
        scanError.value = '当前浏览器不支持相机\n可尝试从相册选择图片识别'
      }
      return
    }
    
    if (!window.isSecureContext) {
      scanError.value = '非安全环境无法调用相机\n请使用HTTPS访问或从相册选择'
      return
    }
    
    const constraints = {
      video: {
        facingMode: { ideal: 'environment' },
        width: { ideal: 1280 },
        height: { ideal: 720 }
      },
      audio: false
    }
    stream = await navigator.mediaDevices.getUserMedia(constraints)
    if (videoRef.value) {
      videoRef.value.srcObject = stream
      await videoRef.value.play()
      scanning.value = true
      checkFlashSupport()
      startScanLoop()
    }
  } catch (e) {
    console.error('相机启动失败', e)
    if (e.name === 'NotAllowedError' || e.name === 'PermissionDeniedError') {
      scanError.value = '请允许相机权限后重试\n也可从相册选择图片识别'
    } else if (e.name === 'NotFoundError' || e.name === 'DevicesNotFoundError') {
      scanError.value = '未找到相机设备\n可从相册选择图片识别'
    } else if (e.name === 'NotReadableError' || e.name === 'TrackStartError') {
      scanError.value = '相机被其他应用占用\n请关闭后重试或从相册选择'
    } else if (e.name === 'OverconstrainedError') {
      scanError.value = '相机参数不支持\n可从相册选择图片识别'
    } else if (!window.isSecureContext) {
      scanError.value = 'HTTP环境无法调用相机\n请使用HTTPS或从相册选择'
    } else {
      scanError.value = '相机启动失败\n可从相册选择图片识别'
    }
  }
}

function checkFlashSupport() {
  if (!stream) return
  const track = stream.getVideoTracks()[0]
  if (!track) return
  const capabilities = track.getCapabilities ? track.getCapabilities() : {}
  flashSupported.value = !!capabilities.torch
}

async function toggleFlash() {
  if (!stream || !flashSupported.value) return
  try {
    const track = stream.getVideoTracks()[0]
    flashOn.value = !flashOn.value
    await track.applyConstraints({ advanced: [{ torch: flashOn.value }] })
  } catch (e) {
    console.error('闪光灯切换失败', e)
  }
}

function startScanLoop() {
  if (scanTimer) clearInterval(scanTimer)
  scanTimer = setInterval(() => {
    if (!scanning.value || !videoRef.value || !canvasRef.value) return
    const video = videoRef.value
    const canvas = canvasRef.value
    if (video.readyState !== video.HAVE_ENOUGH_DATA) return
    const ctx = canvas.getContext('2d', { willReadFrequently: true })
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height)
    const code = jsQR(imageData.data, imageData.width, imageData.height, {
      inversionAttempts: 'dontInvert'
    })
    if (code && code.data) {
      handleScanResult(code.data)
    }
  }, 300)
}

function stopScanner() {
  scanning.value = false
  if (scanTimer) {
    clearInterval(scanTimer)
    scanTimer = null
  }
  if (stream) {
    stream.getTracks().forEach(track => track.stop())
    stream = null
  }
  if (videoRef.value) {
    videoRef.value.srcObject = null
  }
}

function closeScanner() {
  stopScanner()
  showScanner.value = false
}

function handleScanResult(data) {
  stopScanner()
  const qrCodeStr = extractQRCode(data)
  if (!qrCodeStr) {
    scanError.value = '未识别到有效的合缘码'
    setTimeout(() => {
      scanning.value = true
      startScanLoop()
    }, 1500)
    return
  }
  doScanMatch(qrCodeStr)
}

function extractQRCode(data) {
  if (!data) return ''
  if (/^[A-Z0-9]{6,}$/.test(data)) return data
  const match = data.match(/[?&]code=([A-Z0-9]+)/)
  if (match) return match[1]
  const match2 = data.match(/\/match\?code=([A-Z0-9]+)/)
  if (match2) return match2[1]
  return ''
}

async function doScanMatch(code) {
  try {
    const res = await request.post(`/match/scan/${code}`)
    closeScanner()
    if (res.match_id) {
      router.push(`/match-result/${res.match_id}`)
    } else {
      alert('合缘成功')
      loadMatchHistory()
    }
  } catch (e) {
    scanError.value = e.response?.data?.detail || '扫码失败，请重试'
    setTimeout(() => {
      scanError.value = ''
      scanning.value = true
      startScanLoop()
    }, 2000)
  }
}

function pickFromAlbum() {
  if (fileInputRef.value) {
    fileInputRef.value.click()
  }
}

function handleFileSelect(e) {
  const file = e.target.files?.[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = (ev) => {
    const img = new Image()
    img.onload = () => {
      const canvas = document.createElement('canvas')
      const ctx = canvas.getContext('2d')
      canvas.width = img.width
      canvas.height = img.height
      ctx.drawImage(img, 0, 0)
      const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height)
      const code = jsQR(imageData.data, imageData.width, imageData.height)
      if (code && code.data) {
        handleScanResult(code.data)
      } else {
        scanError.value = '图片中未识别到合缘码'
        setTimeout(() => { scanError.value = '' }, 2000)
      }
    }
    img.src = ev.target.result
  }
  reader.readAsDataURL(file)
  e.target.value = ''
}

function goMatchResult(id) {
  router.push(`/match-result/${id}`)
}

const hasLoaded = ref(false)

onMounted(() => {
  if (!hasLoaded.value && isLoggedIn.value) {
    loadMatchHistory()
    hasLoaded.value = true
  }
})

onActivated(() => {
  if (authStore.isLoggedIn && history.value.length === 0) {
    loadMatchHistory()
  }
})
</script>

<style scoped>
.guest-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
}

.guest-card {
  text-align: center;
  background: rgba(18, 18, 35, 0.8);
  border: 1px solid rgba(212, 175, 55, 0.15);
  border-radius: var(--radius-lg);
  padding: 50px 32px;
  width: 100%;
  max-width: 340px;
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

.guest-icon {
  font-size: 72px;
  margin-bottom: 24px;
  animation: float 4s ease-in-out infinite;
  position: relative;
  z-index: 1;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.guest-title {
  font-family: 'Cinzel', serif;
  font-size: 22px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 14px;
  position: relative;
  z-index: 1;
}

.guest-desc {
  font-size: 14px;
  color: var(--text-muted);
  margin-bottom: 32px;
  line-height: 1.6;
  position: relative;
  z-index: 1;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--gold-primary) 0%, var(--gold-secondary) 100%);
  color: #0a0a15;
  border: none;
  border-radius: 30px;
  padding: 16px 48px;
  font-size: 16px;
  font-weight: 600;
  font-family: 'Cinzel', serif;
  letter-spacing: 2px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  z-index: 1;
  overflow: hidden;
}

.btn-primary::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.4), transparent);
  transition: left 0.6s;
}

.btn-primary:hover::before {
  left: 100%;
}

.btn-primary:hover {
  transform: scale(1.02);
  box-shadow: 0 0 40px rgba(212, 175, 55, 0.5);
}

.match-content {
  padding: 0 24px 24px;
}

.match-hero {
  text-align: center;
  padding: 40px 0 32px;
  position: relative;
}

.hero-glow {
  position: absolute;
  top: -30%;
  left: 50%;
  transform: translateX(-50%);
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(236, 72, 153, 0.1) 0%, rgba(139, 92, 246, 0.05) 50%, transparent 70%);
  border-radius: 50%;
  pointer-events: none;
}

.hero-icon {
  font-size: 56px;
  margin-bottom: 16px;
  animation: float 3s ease-in-out infinite;
}

.hero-title {
  font-family: 'Cinzel', serif;
  font-size: 32px;
  font-weight: 700;
  background: linear-gradient(135deg, var(--purple-secondary) 0%, var(--pink-accent) 50%, var(--gold-secondary) 100%);
  background-size: 200% 200%;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 8px;
  animation: gradient-shift 4s ease infinite;
}

@keyframes gradient-shift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.hero-sub {
  font-size: 14px;
  color: var(--text-muted);
  letter-spacing: 2px;
  margin-bottom: 20px;
}

.hero-ornament {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.ornament-line {
  width: 40px;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--gold-primary));
}

.hero-ornament:last-child .ornament-line {
  background: linear-gradient(90deg, var(--gold-primary), transparent);
}

.ornament-dot {
  color: var(--gold-primary);
  font-size: 12px;
}

.type-selector {
  margin-bottom: 32px;
}

.type-label {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.label-icon {
  color: var(--gold-primary);
}

.type-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.type-card {
  background: rgba(18, 18, 35, 0.5);
  border: 1px solid rgba(212, 175, 55, 0.1);
  border-radius: 18px;
  padding: 22px 10px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.type-card:active {
  transform: scale(0.95);
}

.type-card.active {
  border-color: rgba(167, 139, 250, 0.4);
  background: rgba(139, 92, 246, 0.08);
}

.type-icon {
  font-size: 32px;
  margin-bottom: 10px;
}

.type-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.type-desc {
  font-size: 12px;
  color: var(--text-muted);
}

.type-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.type-card:hover .type-glow,
.type-card.active .type-glow {
  opacity: 0.6;
}

.type-glow.love { background: linear-gradient(90deg, #ec4899, #f472b6); }
.type-glow.career { background: linear-gradient(90deg, #60a5fa, #93c5fd); }
.type-glow.all { background: linear-gradient(90deg, var(--purple-primary), var(--gold-primary)); }

.action-section {
  margin-bottom: 32px;
}

.action-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: rgba(18, 18, 35, 0.5);
  border: 1px solid rgba(212, 175, 55, 0.1);
  border-radius: 20px;
  margin-bottom: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.action-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(212, 175, 55, 0.3), transparent);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.action-card:hover::before {
  opacity: 1;
}

.action-card:active {
  transform: scale(0.98);
}

.action-card.primary {
  border-color: rgba(167, 139, 250, 0.25);
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.08) 0%, rgba(236, 72, 153, 0.04) 100%);
}

.action-card.disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.action-card.disabled:active {
  transform: none;
}

.action-icon-wrapper {
  position: relative;
  width: 52px;
  height: 52px;
  flex-shrink: 0;
}

.action-icon {
  width: 100%;
  height: 100%;
  background: rgba(139, 92, 246, 0.1);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26px;
  position: relative;
  z-index: 1;
}

.icon-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 44px;
  height: 44px;
  background: radial-gradient(circle, rgba(139, 92, 246, 0.2) 0%, transparent 70%);
  border-radius: 50%;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.action-card:hover .icon-glow {
  opacity: 1;
}

.action-info {
  flex: 1;
  min-width: 0;
}

.action-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.action-desc {
  font-size: 13px;
  color: var(--text-muted);
}

.action-arrow {
  color: var(--gold-primary);
  font-size: 18px;
  flex-shrink: 0;
}

.coming-tag {
  font-size: 12px;
  color: var(--text-muted);
  background: rgba(255, 255, 255, 0.06);
  padding: 4px 12px;
  border-radius: 20px;
  flex-shrink: 0;
}

.history-section {
  margin-bottom: 16px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}

.section-icon {
  font-size: 18px;
}

.section-title {
  font-size: 17px;
  font-weight: 600;
  color: var(--text-primary);
}

.empty-history {
  text-align: center;
  padding: 48px 20px;
  background: rgba(18, 18, 35, 0.5);
  border: 1px solid rgba(212, 175, 55, 0.1);
  border-radius: 20px;
}

.empty-icon {
  font-size: 40px;
  margin-bottom: 12px;
  opacity: 0.6;
}

.empty-text {
  font-size: 14px;
  color: var(--text-muted);
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.history-item {
  background: rgba(18, 18, 35, 0.5);
  border: 1px solid rgba(212, 175, 55, 0.1);
  border-radius: 18px;
  padding: 22px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.history-item:active {
  transform: scale(0.98);
}

.history-users {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-bottom: 14px;
}

.user-avatar {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  font-weight: 700;
  color: white;
  position: relative;
}

.user-avatar.a {
  background: linear-gradient(135deg, var(--purple-primary), #8b5cf6);
}

.user-avatar.b {
  background: linear-gradient(135deg, var(--pink-accent), #f472b6);
}

.user-avatar::after {
  content: '';
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 50%;
}

.vs-icon {
  color: var(--gold-primary);
  font-size: 16px;
  opacity: 0.6;
}

.history-names {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-bottom: 12px;
  font-size: 15px;
  font-weight: 500;
  color: var(--text-primary);
}

.vs-text {
  color: var(--text-muted);
  font-size: 13px;
}

.history-meta {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 14px;
}

.match-type-tag {
  font-size: 12px;
  padding: 5px 12px;
  border-radius: 20px;
  font-weight: 500;
}

.match-type-tag.love {
  background: rgba(236, 72, 153, 0.12);
  color: #f472b6;
}

.match-type-tag.career {
  background: rgba(96, 165, 250, 0.12);
  color: #60a5fa;
}

.match-type-tag.all {
  background: rgba(167, 139, 250, 0.12);
  color: var(--purple-secondary);
}

.history-score {
  font-size: 15px;
  font-weight: 700;
  color: var(--gold-primary);
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
  padding: 24px;
}

.qr-modal {
  position: relative;
  background: linear-gradient(180deg, rgba(18, 18, 35, 0.98) 0%, rgba(5, 5, 16, 0.99) 100%);
  border: 1px solid rgba(212, 175, 55, 0.15);
  border-radius: 24px;
  padding: 36px 24px 28px;
  width: 100%;
  max-width: 360px;
  text-align: center;
  animation: slideUp 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.modal-close {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 36px;
  height: 36px;
  border: none;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 50%;
  color: var(--text-muted);
  font-size: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.modal-close:active {
  transform: scale(0.9);
}

.qr-header {
  margin-bottom: 24px;
  position: relative;
}

.qr-glow {
  position: absolute;
  top: -50%;
  left: 50%;
  transform: translateX(-50%);
  width: 150px;
  height: 150px;
  background: radial-gradient(circle, rgba(139, 92, 246, 0.1) 0%, transparent 70%);
  border-radius: 50%;
  pointer-events: none;
}

.qr-icon {
  font-size: 44px;
  margin-bottom: 14px;
  position: relative;
  z-index: 1;
}

.qr-title {
  font-family: 'Cinzel', serif;
  font-size: 22px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
  position: relative;
  z-index: 1;
}

.qr-desc {
  font-size: 14px;
  color: var(--text-muted);
  position: relative;
  z-index: 1;
}

.qr-image-box {
  background: white;
  border-radius: 18px;
  padding: 24px;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.qr-image {
  width: 220px;
  height: 220px;
}

.qr-placeholder {
  width: 220px;
  height: 220px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  font-size: 15px;
}

.qr-code-text {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 20px;
  padding: 14px 24px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(212, 175, 55, 0.1);
  border-radius: 14px;
}

.code-label {
  font-size: 13px;
  color: var(--text-muted);
}

.code-value {
  font-size: 16px;
  font-weight: 700;
  color: var(--purple-secondary);
  letter-spacing: 3px;
}

.qr-tip {
  font-size: 13px;
  color: var(--text-muted);
}

@media (max-width: 360px) {
  .hero-title { font-size: 28px; }
  .type-grid { gap: 10px; }
  .type-card { padding: 18px 8px; }
  .type-name { font-size: 13px; }
}

/* 扫码界面 */
.scanner-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: #000;
  z-index: 1000;
  display: flex;
  flex-direction: column;
}

.scanner-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
}

.scanner-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: rgba(0, 0, 0, 0.6);
  position: relative;
  z-index: 10;
}

.scanner-back {
  width: 36px;
  height: 36px;
  border: none;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  color: white;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.scanner-title {
  color: white;
  font-size: 17px;
  font-weight: 600;
}

.scanner-view {
  flex: 1;
  position: relative;
  overflow: hidden;
  background: #000;
}

.scanner-video {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.scan-frame {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 260px;
  height: 260px;
  border-radius: 20px;
}

.scan-corner {
  position: absolute;
  width: 30px;
  height: 30px;
  border: 3px solid var(--gold-primary, #d4af37);
}

.scan-corner.tl {
  top: -2px;
  left: -2px;
  border-right: none;
  border-bottom: none;
  border-top-left-radius: 8px;
}

.scan-corner.tr {
  top: -2px;
  right: -2px;
  border-left: none;
  border-bottom: none;
  border-top-right-radius: 8px;
}

.scan-corner.bl {
  bottom: -2px;
  left: -2px;
  border-right: none;
  border-top: none;
  border-bottom-left-radius: 8px;
}

.scan-corner.br {
  bottom: -2px;
  right: -2px;
  border-left: none;
  border-top: none;
  border-bottom-right-radius: 8px;
}

.scan-line {
  position: absolute;
  top: 0;
  left: 8px;
  right: 8px;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--gold-primary, #d4af37), transparent);
  box-shadow: 0 0 10px var(--gold-primary, #d4af37);
  opacity: 0;
}

.scan-line.active {
  opacity: 1;
  animation: scanLine 2.5s ease-in-out infinite;
}

@keyframes scanLine {
  0% { top: 8px; }
  50% { top: calc(100% - 10px); }
  100% { top: 8px; }
}

.scan-tip {
  position: absolute;
  bottom: 40px;
  left: 0;
  right: 0;
  text-align: center;
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.8);
}

.scan-error {
  position: absolute;
  bottom: 40px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(239, 68, 68, 0.95);
  color: white;
  padding: 12px 24px;
  border-radius: 16px;
  font-size: 14px;
  line-height: 1.6;
  text-align: center;
  max-width: 80%;
  white-space: pre-line;
  box-shadow: 0 4px 20px rgba(239, 68, 68, 0.4);
}

.album-fallback {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 32px 40px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(212, 175, 55, 0.3);
  border-radius: 20px;
  cursor: pointer;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.album-fallback:active {
  transform: translate(-50%, -50%) scale(0.95);
}

.album-fallback .album-icon {
  font-size: 48px;
}

.album-fallback .album-text {
  font-size: 15px;
  color: var(--gold-primary, #d4af37);
  font-weight: 500;
  text-align: center;
}

.scanner-actions {
  display: flex;
  justify-content: center;
  gap: 40px;
  padding: 30px 20px 50px;
  background: rgba(0, 0, 0, 0.8);
}

.scan-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  padding: 8px;
}

.scan-btn .btn-icon {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.scan-btn span:last-child {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.8);
}
</style>
