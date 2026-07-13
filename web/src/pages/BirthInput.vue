<template>
  <div class="page-container">
    <div class="star-field" ref="starField"></div>

    <div class="form-card">
      <div class="card-header">
        <span class="card-icon">☯</span>
        <span class="form-title">输入生辰信息</span>
        <span class="card-decoration">☯</span>
      </div>
      <span class="form-desc">精确到时辰，探索命理玄机</span>

      <div class="form-section">
        <span class="section-label">排盘方式</span>
        <div class="type-switch">
          <button class="type-btn" :class="{ active: chartType === 'ziwei' }" @click="switchChartType('ziwei')">
            <span class="type-icon">🔮</span>
            <span>紫微斗数</span>
          </button>
          <button class="type-btn" :class="{ active: chartType === 'bazi' }" @click="switchChartType('bazi')">
            <span class="type-icon">📜</span>
            <span>八字四柱</span>
          </button>
        </div>
      </div>

      <div class="form-section">
        <span class="section-label">历法类型</span>
        <div class="type-switch">
          <button class="type-btn" :class="{ active: solarLunar === 'solar' }" @click="solarLunar = 'solar'">
            <span>公历</span>
          </button>
          <button class="type-btn" :class="{ active: solarLunar === 'lunar' }" @click="solarLunar = 'lunar'">
            <span>农历</span>
          </button>
        </div>
      </div>

      <div class="form-section">
        <span class="section-label">出生日期</span>
        <div class="picker-wrap" @click="showDatePicker = true">
          <div class="picker-input display-input">
            <span :class="{ placeholder: !birthDate }">{{ birthDate || '请选择出生日期' }}</span>
          </div>
          <span class="picker-icon">📅</span>
        </div>
      </div>

      <DateWheelPicker
        v-if="showDatePicker"
        v-model="birthDate"
        title="选择出生日期"
        @confirm="onDateConfirm"
        @cancel="showDatePicker = false"
      />

      <div class="form-section">
        <span class="section-label">出生时辰</span>
        <div class="hour-grid">
          <button class="hour-item" :class="{ 'hour-selected': hourIndex === item.index }"
                v-for="item in hours" :key="item.index"
                @click="hourIndex = item.index">
            <span class="hour-name">{{ item.name }}</span>
            <span class="hour-time">{{ item.time }}</span>
          </button>
        </div>
      </div>

      <div class="form-section">
        <span class="section-label">性别</span>
        <div class="gender-switch">
          <button class="gender-btn" :class="{ active: gender === 'male' }" @click="gender = 'male'">
            <span class="gender-symbol">♂</span>
            <span class="gender-text">男</span>
          </button>
          <button class="gender-btn" :class="{ active: gender === 'female' }" @click="gender = 'female'">
            <span class="gender-symbol">♀</span>
            <span class="gender-text">女</span>
          </button>
        </div>
      </div>

      <div class="form-section">
        <span class="section-label">查询对象</span>
        <div class="type-switch">
          <button class="type-btn" :class="{ active: ownerType === 'self' }" @click="ownerType = 'self'">为自己查</button>
          <button class="type-btn" :class="{ active: ownerType === 'helped' }" @click="ownerType = 'helped'">帮别人查</button>
        </div>
        <div v-if="ownerType === 'helped'" class="remark-input-wrap">
          <div class="picker-wrap">
            <input type="text" class="picker-input" v-model="remark" placeholder="备注：如妈妈、老公、闺蜜" />
            <span class="picker-icon">✏️</span>
          </div>
        </div>
      </div>

      <button class="submit-btn" :class="{ disabled: loading }" @click="submit">
        <span class="submit-icon">☯</span>
        <span>{{ loading ? '排盘中...' : '开始排盘' }}</span>
      </button>

      <div class="tip-card">
        <span class="tip-icon">💡</span>
        <span class="tip-text">不确定时辰？可以选大致时间段，后续可校准</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { request } from '@/utils/request'
import DateWheelPicker from '@/components/DateWheelPicker.vue'

const router = useRouter()
const route = useRoute()
const starField = ref(null)

const chartType = ref(route.query.type === 'bazi' ? 'bazi' : 'ziwei')
const solarLunar = ref('solar')
const birthDate = ref(route.query.date_str || '')
const hourIndex = ref(parseInt(route.query.hour_index) || 0)
const gender = ref(route.query.gender || 'male')
const ownerType = ref('self')
const remark = ref('')
const loading = ref(false)
const showDatePicker = ref(false)

const hours = [
  { index: 0, name: '早子时', time: '00:00-01:00' },
  { index: 1, name: '丑时', time: '01:00-03:00' },
  { index: 2, name: '寅时', time: '03:00-05:00' },
  { index: 3, name: '卯时', time: '05:00-07:00' },
  { index: 4, name: '辰时', time: '07:00-09:00' },
  { index: 5, name: '巳时', time: '09:00-11:00' },
  { index: 6, name: '午时', time: '11:00-13:00' },
  { index: 7, name: '未时', time: '13:00-15:00' },
  { index: 8, name: '申时', time: '15:00-17:00' },
  { index: 9, name: '酉时', time: '17:00-19:00' },
  { index: 10, name: '戌时', time: '19:00-21:00' },
  { index: 11, name: '亥时', time: '21:00-23:00' }
]

async function submit() {
  if (!birthDate.value) {
    alert('请选择出生日期')
    return
  }

  loading.value = true
  try {
    const data = {
      solar_date: solarLunar.value === 'solar' ? birthDate.value : '',
      lunar_date: solarLunar.value === 'lunar' ? birthDate.value : '',
      hour_index: hourIndex.value,
      gender: gender.value,
      is_default: ownerType.value === 'self',
      name: ownerType.value === 'self' ? '我的星盘' : remark.value || '好友星盘',
      remark: ownerType.value === 'self' ? '' : remark.value,
      chart_type: chartType.value,
      is_leap: false
    }

    if (chartType.value === 'bazi') {
      router.push({
        path: '/bazi-detail',
        query: {
          date_str: birthDate.value,
          hour_index: hourIndex.value,
          gender: gender.value
        }
      })
    } else {
      const res = await request.post('/users/save-chart', data)
      router.push(`/chart-detail/${res.id}`)
    }
  } catch (e) {
    console.error('提交失败', e)
    alert('提交失败')
  } finally {
    loading.value = false
  }
}

function switchChartType(type) {
  chartType.value = type
  if (birthDate.value) {
    submit()
  }
}

function onDateConfirm(date) {
  birthDate.value = date
  showDatePicker.value = false
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
  0%, 100% { opacity: 0.2; transform: scale(1); }
  50% { opacity: 0.8; transform: scale(1.2); }
}

.form-card {
  background: rgba(18, 18, 35, 0.7);
  border: 1px solid rgba(212, 175, 55, 0.15);
  border-radius: 24px;
  padding: 32px;
  margin: 24px;
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  position: relative;
  overflow: hidden;
}

.form-card::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -50%;
  width: 150%;
  height: 150%;
  background: radial-gradient(circle at 70% 30%, rgba(139, 92, 246, 0.1) 0%, transparent 50%);
  pointer-events: none;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 8px;
}

.card-icon {
  font-size: 28px;
}

.form-title {
  font-family: 'Cinzel', serif;
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
}

.card-decoration {
  color: var(--gold-primary);
  font-size: 18px;
}

.form-desc {
  font-size: 14px;
  color: var(--text-muted);
  text-align: center;
  margin-bottom: 32px;
  display: block;
}

.form-section {
  margin-bottom: 28px;
}

.section-label {
  font-size: 15px;
  color: var(--gold-primary);
  margin-bottom: 14px;
  font-weight: 500;
  display: block;
  letter-spacing: 1px;
}

.type-switch {
  display: flex;
  gap: 14px;
}

.type-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 18px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(212, 175, 55, 0.15);
  border-radius: 14px;
  font-size: 15px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: inherit;
}

.type-btn:focus-visible {
  outline: 2px solid var(--gold-primary);
  outline-offset: 2px;
}

.type-btn.active {
  background: linear-gradient(135deg, rgba(212, 175, 55, 0.15) 0%, rgba(139, 92, 246, 0.08) 100%);
  border-color: rgba(212, 175, 55, 0.4);
  color: var(--gold-primary);
}

.type-icon {
  font-size: 22px;
}

.picker-wrap {
  position: relative;
}

.picker-input {
  width: 100%;
  padding: 18px 24px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(212, 175, 55, 0.15);
  border-radius: 14px;
  font-size: 15px;
  color: var(--text-primary);
  box-sizing: border-box;
}

.display-input {
  cursor: pointer;
  min-height: 55px;
  display: flex;
  align-items: center;
}

.display-input .placeholder {
  color: var(--text-dim);
}

.picker-input::placeholder {
  color: var(--text-dim);
}

.picker-icon {
  position: absolute;
  right: 18px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 18px;
  color: var(--text-muted);
  pointer-events: none;
}

.hour-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.hour-item {
  text-align: center;
  padding: 14px 8px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(212, 175, 55, 0.1);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: inherit;
}

.hour-item:focus-visible {
  outline: 2px solid var(--gold-primary);
  outline-offset: 2px;
}

.hour-item.hour-selected {
  background: rgba(212, 175, 55, 0.12);
  border-color: var(--gold-primary);
}

.hour-name {
  font-size: 14px;
  color: var(--text-primary);
  margin-bottom: 4px;
  display: block;
}

.hour-time {
  font-size: 11px;
  color: var(--text-muted);
}

.gender-switch {
  display: flex;
  gap: 16px;
}

.gender-btn {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 24px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(212, 175, 55, 0.15);
  border-radius: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: inherit;
}

.gender-btn:focus-visible {
  outline: 2px solid var(--gold-primary);
  outline-offset: 2px;
}

.gender-btn.active {
  background: rgba(212, 175, 55, 0.12);
  border-color: var(--gold-primary);
}

.gender-symbol {
  font-size: 32px;
  color: var(--text-muted);
}

.gender-btn.active .gender-symbol {
  color: var(--gold-primary);
}

.gender-text {
  font-size: 15px;
  color: var(--text-muted);
}

.gender-btn.active .gender-text {
  color: var(--gold-primary);
}

.remark-input-wrap {
  margin-top: 14px;
}

.submit-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: 100%;
  background: linear-gradient(135deg, var(--gold-primary) 0%, var(--gold-secondary) 100%);
  color: #0a0a15;
  border-radius: 30px;
  padding: 18px;
  font-size: 16px;
  font-weight: 600;
  font-family: 'Cinzel', serif;
  letter-spacing: 2px;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 32px;
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
  transform: scale(1.02);
  box-shadow: 0 0 40px rgba(212, 175, 55, 0.5);
}

.submit-btn.disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.submit-icon {
  font-size: 18px;
}

.tip-card {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin-top: 20px;
  padding: 16px;
  background: rgba(139, 92, 246, 0.06);
  border: 1px solid rgba(139, 92, 246, 0.1);
  border-radius: 12px;
}

.tip-icon {
  font-size: 16px;
  flex-shrink: 0;
}

.tip-text {
  font-size: 13px;
  color: var(--text-muted);
  line-height: 1.5;
}
</style>