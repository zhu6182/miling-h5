<template>
  <div class="page-container">
    <div class="star-field" ref="starField"></div>
    
    <div class="navbar">
      <button class="back-btn" @click="goBack">
        <span class="back-icon">←</span>
      </button>
      <h1 class="nav-title">合缘结果</h1>
      <div class="nav-right"></div>
    </div>

    <div v-if="loading" class="loading">
      <div class="loading-icon">🔮</div>
      <span>正在配对分析...</span>
    </div>

    <div v-else-if="matchData" class="result-content">
      <div v-if="matchData.locked" class="locked-section">
        <div class="locked-icon">🔒</div>
        <h3 class="locked-title">完整结果已锁定</h3>
        <p class="locked-desc">观看广告解锁完整合缘分析报告</p>
        <button class="unlock-btn" @click="unlockResult">
          <span>🎬</span>
          <span>看广告解锁</span>
        </button>
      </div>

      <template v-else>
        <div class="result-header">
          <div class="users-row">
            <div class="user-info">
              <div class="user-avatar">{{ matchData.user_a_nickname?.charAt(0) || '?' }}</div>
              <div class="user-name">{{ matchData.user_a_nickname }}</div>
              <div class="user-detail">{{ matchData.match_data?.soul_palace_a || '' }}</div>
            </div>
            <div class="match-icon">{{ hasLove ? '💕' : '🤝' }}</div>
            <div class="user-info">
              <div class="user-avatar">{{ matchData.user_b_nickname?.charAt(0) || '?' }}</div>
              <div class="user-name">{{ matchData.user_b_nickname }}</div>
              <div class="user-detail">{{ matchData.match_data?.soul_palace_b || '' }}</div>
            </div>
          </div>
          
          <div class="overall-score">
            <div class="score-label">综合匹配指数</div>
            <div class="score-value">{{ overallScore }}</div>
            <div class="score-unit">分</div>
          </div>
        </div>

        <div class="dimensions">
          <!-- 姻缘配对（同性别不显示） -->
          <div v-if="hasLove" class="dim-card love">
            <div class="dim-header">
              <span class="dim-icon">💖</span>
              <span class="dim-title">姻缘配对</span>
              <span class="dim-score">{{ loveScore }}分</span>
            </div>
            <div class="score-bar">
              <div class="score-fill" :style="{ width: loveScore + '%' }"></div>
            </div>
            <div class="dim-tags">
              <span class="tag" v-for="(tag, i) in loveTags" :key="i">{{ tag }}</span>
            </div>
            <p class="dim-summary">{{ loveSummary }}</p>
            <button class="ai-btn" @click="loadAIAnalysis('love')" :disabled="aiLoading === 'love'">
              <span v-if="aiLoading === 'love'" class="ai-loading-dot"></span>
              <span v-else>🤖</span>
              <span>{{ aiLoading === 'love' ? 'AI分析中...' : 'AI详解' }}</span>
            </button>
          </div>

          <!-- 事业合作 -->
          <div class="dim-card career">
            <div class="dim-header">
              <span class="dim-icon">💼</span>
              <span class="dim-title">事业合作</span>
              <span class="dim-score">{{ careerScore }}分</span>
            </div>
            <div class="score-bar">
              <div class="score-fill" :style="{ width: careerScore + '%' }"></div>
            </div>
            <div class="dim-tags">
              <span class="tag" v-for="(tag, i) in careerTags" :key="i">{{ tag }}</span>
            </div>
            <p class="dim-summary">{{ careerSummary }}</p>
            <button class="ai-btn" @click="loadAIAnalysis('career')" :disabled="aiLoading === 'career'">
              <span v-if="aiLoading === 'career'" class="ai-loading-dot"></span>
              <span v-else>🤖</span>
              <span>{{ aiLoading === 'career' ? 'AI分析中...' : 'AI详解' }}</span>
            </button>
          </div>

          <!-- 友谊缘分 -->
          <div class="dim-card friendship">
            <div class="dim-header">
              <span class="dim-icon">👯</span>
              <span class="dim-title">友谊缘分</span>
              <span class="dim-score">{{ friendshipScore }}分</span>
            </div>
            <div class="score-bar">
              <div class="score-fill" :style="{ width: friendshipScore + '%' }"></div>
            </div>
            <div class="dim-tags">
              <span class="tag" v-for="(tag, i) in friendshipTags" :key="i">{{ tag }}</span>
            </div>
            <p class="dim-summary">{{ friendshipSummary }}</p>
            <button class="ai-btn" @click="loadAIAnalysis('friendship')" :disabled="aiLoading === 'friendship'">
              <span v-if="aiLoading === 'friendship'" class="ai-loading-dot"></span>
              <span v-else>🤖</span>
              <span>{{ aiLoading === 'friendship' ? 'AI分析中...' : 'AI详解' }}</span>
            </button>
          </div>

          <!-- 贵人运 -->
          <div class="dim-card mentor">
            <div class="dim-header">
              <span class="dim-icon">🌟</span>
              <span class="dim-title">贵人运</span>
              <span class="dim-score">{{ mentorScore }}分</span>
            </div>
            <div class="score-bar">
              <div class="score-fill" :style="{ width: mentorScore + '%' }"></div>
            </div>
            <div class="dim-tags">
              <span class="tag" v-for="(tag, i) in mentorTags" :key="i">{{ tag }}</span>
            </div>
            <p class="dim-summary">{{ mentorSummary }}</p>
            <button class="ai-btn" @click="loadAIAnalysis('mentor')" :disabled="aiLoading === 'mentor'">
              <span v-if="aiLoading === 'mentor'" class="ai-loading-dot"></span>
              <span v-else>🤖</span>
              <span>{{ aiLoading === 'mentor' ? 'AI分析中...' : 'AI详解' }}</span>
            </button>
          </div>
        </div>

        <div class="advice-section">
          <h3 class="section-title">💡 合缘建议</h3>
          <div class="advice-list">
            <div class="advice-item" v-if="loveAdvice">
              <span class="advice-label">感情</span>
              <span class="advice-text">{{ loveAdvice }}</span>
            </div>
            <div class="advice-item" v-if="careerAdvice">
              <span class="advice-label">事业</span>
              <span class="advice-text">{{ careerAdvice }}</span>
            </div>
            <div class="advice-item" v-if="friendshipAdvice">
              <span class="advice-label">友谊</span>
              <span class="advice-text">{{ friendshipAdvice }}</span>
            </div>
          </div>
        </div>

        <div class="five-section">
          <h3 class="section-title">🔮 五行格局</h3>
          <div class="five-row">
            <div class="five-item">
              <div class="five-label">{{ matchData.user_a_nickname }}</div>
              <div class="five-value">{{ matchData.match_data?.five_elements_a || '未知' }}</div>
            </div>
            <div class="five-vs">VS</div>
            <div class="five-item">
              <div class="five-label">{{ matchData.user_b_nickname }}</div>
              <div class="five-value">{{ matchData.match_data?.five_elements_b || '未知' }}</div>
            </div>
          </div>
        </div>
      </template>
    </div>

    <div v-else class="no-data">
      <span class="no-data-icon">🔮</span>
      <p class="no-data-text">暂无配对数据</p>
    </div>

    <!-- AI详解弹窗 -->
    <Teleport to="body">
      <div v-if="showAIModal" class="ai-overlay" @click="closeAIModal">
        <div class="ai-modal" @click.stop>
          <div class="ai-modal-header">
            <h3 class="ai-modal-title">🤖 {{ aiModalTitle }}</h3>
            <button class="ai-close-btn" @click="closeAIModal">✕</button>
          </div>
          <div class="ai-modal-body">
            <div v-if="aiLoading" class="ai-loading">
              <div class="ai-loading-spinner"></div>
              <span>正在生成深度分析...</span>
            </div>
            <div v-else class="ai-content" v-html="aiContent"></div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { request } from '@/utils/request'

const route = useRoute()
const router = useRouter()
const loading = ref(true)
const matchData = ref(null)
const starField = ref(null)

// AI详解相关
const showAIModal = ref(false)
const aiLoading = ref(null)
const aiContent = ref('')
const aiModalTitle = ref('')

const matchResult = computed(() => matchData.value?.match_data || {})
const dimensions = computed(() => matchResult.value.dimensions || {})

const overallScore = computed(() => matchResult.value.overall_score || 0)

const hasLove = computed(() => !!dimensions.value.love)
const loveScore = computed(() => dimensions.value.love?.score || 0)
const loveTags = computed(() => dimensions.value.love?.tags || [])
const loveSummary = computed(() => dimensions.value.love?.summary || '')
const loveAdvice = computed(() => dimensions.value.love?.advice || '')

const careerScore = computed(() => dimensions.value.career?.score || 0)
const careerTags = computed(() => dimensions.value.career?.tags || [])
const careerSummary = computed(() => dimensions.value.career?.summary || '')
const careerAdvice = computed(() => dimensions.value.career?.advice || '')

const friendshipScore = computed(() => dimensions.value.friendship?.score || 0)
const friendshipTags = computed(() => dimensions.value.friendship?.tags || [])
const friendshipSummary = computed(() => dimensions.value.friendship?.summary || '')
const friendshipAdvice = computed(() => dimensions.value.friendship?.advice || '')

const mentorScore = computed(() => dimensions.value.mentor?.score || 0)
const mentorTags = computed(() => dimensions.value.mentor?.tags || [])
const mentorSummary = computed(() => dimensions.value.mentor?.summary || '')
const mentorAdvice = computed(() => dimensions.value.mentor?.advice || '')

async function loadMatch() {
  try {
    const res = await request.get(`/match/${route.params.id}`)
    matchData.value = res
  } catch (e) {
    console.error('加载配对数据失败', e)
  } finally {
    loading.value = false
  }
}

async function unlockResult() {
  try {
    const res = await request.post(`/match/${route.params.id}/unlock`, { ad_watched: true })
    matchData.value.match_data = res.match_data
    matchData.value.locked = false
  } catch (e) {
    console.error('解锁失败', e)
    alert('解锁失败，请重试')
  }
}

const DIMENSION_TITLES = {
  love: '姻缘配对深度分析',
  career: '事业合作深度分析',
  friendship: '友谊缘分深度分析',
  mentor: '贵人运深度分析',
}

async function loadAIAnalysis(dimension) {
  const cacheKey = `ai_${dimension}`
  
  // 如果有缓存的数据，直接展示
  if (matchResult.value[cacheKey]) {
    aiModalTitle.value = DIMENSION_TITLES[dimension]
    aiContent.value = matchResult.value[cacheKey]
    showAIModal.value = true
    return
  }

  aiLoading.value = dimension
  aiModalTitle.value = DIMENSION_TITLES[dimension]
  aiContent.value = ''
  showAIModal.value = true

  try {
    // AI分析需要较长时间，单独设置180秒超时
    const res = await request.post(`/match/${route.params.id}/ai-analysis`, { dimension }, { timeout: 180000 })
    aiContent.value = res.analysis
    // 缓存到本地
    if (matchData.value.match_data) {
      matchData.value.match_data[cacheKey] = res.analysis
    }
  } catch (e) {
    const isTimeout = e.code === 'ECONNABORTED' || e.message?.includes('timeout')
    aiContent.value = isTimeout
      ? '<p style="color:#fbbf24;">AI分析超时，大模型正在思考中，请稍后重试</p>'
      : '<p style="color:#ef4444;">AI分析失败，请稍后重试</p>'
    console.error('AI分析失败', e)
  } finally {
    aiLoading.value = null
  }
}

function closeAIModal() {
  showAIModal.value = false
}

function goBack() {
  router.back()
}

function initStars() {
  if (!starField.value) return
  const container = starField.value
  const starCount = 40
  
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
  loadMatch()
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

.star {
  position: absolute;
  background: white;
  border-radius: 50%;
  animation: twinkle 3s ease-in-out infinite;
}

@keyframes twinkle {
  0%, 100% { opacity: 0.2; }
  50% { opacity: 0.8; }
}

.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  background: rgba(10, 10, 25, 0.9);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(212, 175, 55, 0.1);
  z-index: 100;
}

.back-btn {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 20px;
  color: var(--text-primary);
}

.nav-title {
  font-size: 17px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.nav-right {
  width: 40px;
}

.loading {
  text-align: center;
  padding: 150px 0;
  color: var(--text-muted);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.loading-icon {
  font-size: 48px;
  animation: spin 2s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.result-content {
  padding: 76px 16px 40px;
  position: relative;
  z-index: 1;
}

.locked-section {
  text-align: center;
  padding: 80px 20px;
}

.locked-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.locked-title {
  font-size: 20px;
  color: var(--text-primary);
  margin: 0 0 10px;
}

.locked-desc {
  font-size: 14px;
  color: var(--text-muted);
  margin: 0 0 30px;
}

.unlock-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 14px 32px;
  background: linear-gradient(135deg, var(--gold-primary), var(--gold-light));
  border: none;
  border-radius: 28px;
  color: #1a1a2e;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.unlock-btn:active {
  transform: scale(0.95);
}

.result-header {
  text-align: center;
  padding: 20px 0 30px;
}

.users-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  margin-bottom: 24px;
}

.user-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.user-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.3), rgba(212, 175, 55, 0.3));
  border: 2px solid var(--gold-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: 600;
  color: var(--gold-primary);
}

.user-name {
  font-size: 14px;
  color: var(--text-primary);
  font-weight: 500;
}

.user-detail {
  font-size: 12px;
  color: var(--text-muted);
}

.match-icon {
  font-size: 28px;
  animation: heartbeat 1.5s ease-in-out infinite;
}

@keyframes heartbeat {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.15); }
}

.overall-score {
  position: relative;
}

.score-label {
  font-size: 13px;
  color: var(--text-muted);
  margin-bottom: 8px;
}

.score-value {
  font-size: 56px;
  font-weight: 700;
  background: linear-gradient(135deg, var(--gold-primary), #ffd700);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1;
  display: inline;
}

.score-unit {
  font-size: 18px;
  color: var(--gold-primary);
  margin-left: 4px;
}

.dimensions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 24px;
}

.dim-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(212, 175, 55, 0.1);
  border-radius: 16px;
  padding: 16px;
}

.dim-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.dim-icon {
  font-size: 20px;
}

.dim-title {
  flex: 1;
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.dim-score {
  font-size: 16px;
  font-weight: 600;
  color: var(--gold-primary);
}

.score-bar {
  height: 8px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 10px;
}

.score-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 1s ease;
}

.dim-card.love .score-fill { background: linear-gradient(90deg, #ff6b9d, #ff8fab); }
.dim-card.career .score-fill { background: linear-gradient(90deg, #4ecdc4, #6ee7de); }
.dim-card.friendship .score-fill { background: linear-gradient(90deg, #a78bfa, #c4b5fd); }
.dim-card.mentor .score-fill { background: linear-gradient(90deg, #fbbf24, #fcd34d); }

.dim-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 10px;
}

.tag {
  padding: 4px 10px;
  background: rgba(212, 175, 55, 0.1);
  border: 1px solid rgba(212, 175, 55, 0.2);
  border-radius: 12px;
  font-size: 12px;
  color: var(--gold-primary);
}

.dim-summary {
  font-size: 13px;
  line-height: 1.7;
  color: var(--text-secondary);
  margin: 0 0 12px;
}

.ai-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 18px;
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(212, 175, 55, 0.15));
  border: 1px solid rgba(139, 92, 246, 0.3);
  border-radius: 20px;
  color: #c4b5fd;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: inherit;
}

.ai-btn:active {
  transform: scale(0.95);
}

.ai-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.ai-loading-dot {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(196, 181, 253, 0.3);
  border-top-color: #c4b5fd;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.advice-section,
.five-section {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(212, 175, 55, 0.1);
  border-radius: 16px;
  padding: 16px;
  margin-bottom: 16px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 14px;
}

.advice-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.advice-item {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.advice-label {
  flex-shrink: 0;
  padding: 2px 10px;
  background: rgba(212, 175, 55, 0.15);
  border-radius: 10px;
  font-size: 12px;
  color: var(--gold-primary);
  font-weight: 500;
}

.advice-text {
  font-size: 13px;
  line-height: 1.7;
  color: var(--text-secondary);
}

.five-row {
  display: flex;
  align-items: center;
  justify-content: space-around;
}

.five-item {
  text-align: center;
}

.five-label {
  font-size: 13px;
  color: var(--text-muted);
  margin-bottom: 6px;
}

.five-value {
  font-size: 18px;
  font-weight: 600;
  color: var(--gold-primary);
}

.five-vs {
  font-size: 14px;
  color: var(--text-muted);
  font-weight: 600;
}

.no-data {
  text-align: center;
  padding: 150px 0;
  color: var(--text-muted);
}

.no-data-icon {
  font-size: 48px;
  display: block;
  margin-bottom: 12px;
}

.no-data-text {
  font-size: 14px;
  margin: 0;
}

/* AI详解弹窗 */
.ai-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.75);
  z-index: 1000;
  display: flex;
  align-items: flex-end;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.ai-modal {
  width: 100%;
  max-height: 85vh;
  background: linear-gradient(180deg, #1a1a2e 0%, #0f0f1a 100%);
  border-radius: 24px 24px 0 0;
  display: flex;
  flex-direction: column;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from { transform: translateY(100%); }
  to { transform: translateY(0); }
}

.ai-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid rgba(212, 175, 55, 0.1);
  flex-shrink: 0;
}

.ai-modal-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.ai-close-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.05);
  border: none;
  border-radius: 50%;
  color: var(--text-muted);
  font-size: 16px;
  cursor: pointer;
}

.ai-modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  -webkit-overflow-scrolling: touch;
}

.ai-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 60px 0;
  color: var(--text-muted);
  font-size: 14px;
}

.ai-loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(212, 175, 55, 0.15);
  border-top-color: var(--gold-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.ai-content {
  font-size: 14px;
  line-height: 1.9;
  color: var(--text-secondary);
}

.ai-content :deep(strong) {
  color: var(--text-primary);
  font-weight: 600;
}

.ai-content :deep(em) {
  color: var(--gold-primary);
  font-style: normal;
}

.ai-content :deep(.warn) {
  color: #f59e0b;
}

.ai-content :deep(.good) {
  color: #34d399;
}
</style>
