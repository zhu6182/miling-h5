<template>
  <Teleport to="body">
    <div class="picker-overlay" @click="handleOverlayClick">
      <div class="picker-container" @click.stop>
        <div class="picker-header">
          <button class="picker-btn cancel" @click="handleCancel">取消</button>
          <span class="picker-title">{{ title }}</span>
          <button class="picker-btn confirm" @click="handleConfirm">确定</button>
        </div>
        
        <div class="picker-body">
          <div class="wheel-mask-top"></div>
          <div class="wheel-mask-bottom"></div>
          <div class="wheel-highlight"></div>
          
          <div class="wheel-col" ref="yearCol" @touchstart="onTouchStart($event, 'year')"
               @touchmove="onTouchMove($event, 'year')" @touchend="onTouchEnd('year')">
            <div class="wheel-item" :class="{ active: y === selectedYear }"
                 v-for="y in yearList" :key="y" :data-value="y">
              {{ y }}年
            </div>
          </div>
          
          <div class="wheel-col" ref="monthCol" @touchstart="onTouchStart($event, 'month')"
               @touchmove="onTouchMove($event, 'month')" @touchend="onTouchEnd('month')">
            <div class="wheel-item" :class="{ active: m === selectedMonth }"
                 v-for="m in monthList" :key="m" :data-value="m">
              {{ m }}月
            </div>
          </div>
          
          <div class="wheel-col" ref="dayCol" @touchstart="onTouchStart($event, 'day')"
               @touchmove="onTouchMove($event, 'day')" @touchend="onTouchEnd('day')">
            <div class="wheel-item" :class="{ active: d === selectedDay }"
                 v-for="d in dayList" :key="d" :data-value="d">
              {{ d }}日
            </div>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch, onMounted, nextTick } from 'vue'

const props = defineProps({
  modelValue: { type: String, default: '' },
  title: { type: String, default: '选择出生日期' },
  minYear: { type: Number, default: 1930 },
  maxYear: { type: Number, default: 2025 }
})

const emit = defineEmits(['update:modelValue', 'confirm', 'cancel'])

const yearCol = ref(null)
const monthCol = ref(null)
const dayCol = ref(null)

const selectedYear = ref(1995)
const selectedMonth = ref(6)
const selectedDay = ref(15)

const ITEM_HEIGHT = 44
const VISIBLE_ITEMS = 5

const yearList = computed(() => {
  const list = []
  for (let y = props.minYear; y <= props.maxYear; y++) {
    list.push(y)
  }
  return list
})

const monthList = computed(() => {
  return Array.from({ length: 12 }, (_, i) => i + 1)
})

const dayList = computed(() => {
  const days = new Date(selectedYear.value, selectedMonth.value, 0).getDate()
  return Array.from({ length: days }, (_, i) => i + 1)
})

watch(dayList, () => {
  const maxDay = dayList.value.length
  if (selectedDay.value > maxDay) {
    selectedDay.value = maxDay
  }
  nextTick(() => scrollTo('day', selectedDay.value - 1))
})

function getColRef(type) {
  if (type === 'year') return yearCol.value
  if (type === 'month') return monthCol.value
  return dayCol.value
}

function scrollTo(type, index) {
  const col = getColRef(type)
  if (!col) return
  col.scrollTo({
    top: index * ITEM_HEIGHT,
    behavior: 'smooth'
  })
}

function getCurrentIndex(type) {
  const col = getColRef(type)
  if (!col) return 0
  return Math.round(col.scrollTop / ITEM_HEIGHT)
}

function initFromValue() {
  if (props.modelValue) {
    const parts = props.modelValue.split('-')
    if (parts.length === 3) {
      selectedYear.value = parseInt(parts[0])
      selectedMonth.value = parseInt(parts[1])
      selectedDay.value = parseInt(parts[2])
    }
  }
  nextTick(() => {
    scrollTo('year', yearList.value.indexOf(selectedYear.value))
    scrollTo('month', selectedMonth.value - 1)
    scrollTo('day', selectedDay.value - 1)
  })
}

let touchStartY = 0
let touchStartScroll = 0
let isDragging = false

function onTouchStart(e, type) {
  isDragging = true
  touchStartY = e.touches[0].clientY
  touchStartScroll = getColRef(type).scrollTop
}

function onTouchMove(e, type) {
  if (!isDragging) return
  const deltaY = touchStartY - e.touches[0].clientY
  const col = getColRef(type)
  col.scrollTop = touchStartScroll + deltaY
}

function onTouchEnd(type) {
  isDragging = false
  const index = getCurrentIndex(type)
  const col = getColRef(type)
  
  let maxIndex
  if (type === 'year') maxIndex = yearList.value.length - 1
  else if (type === 'month') maxIndex = 11
  else maxIndex = dayList.value.length - 1
  
  const clampedIndex = Math.max(0, Math.min(maxIndex, index))
  scrollTo(type, clampedIndex)
  
  if (type === 'year') {
    selectedYear.value = yearList.value[clampedIndex]
  } else if (type === 'month') {
    selectedMonth.value = clampedIndex + 1
  } else {
    selectedDay.value = clampedIndex + 1
  }
}

function onScroll(type) {
  if (isDragging) return
  const index = getCurrentIndex(type)
  if (type === 'year') {
    if (yearList.value[index] && selectedYear.value !== yearList.value[index]) {
      selectedYear.value = yearList.value[index]
    }
  } else if (type === 'month') {
    if (selectedMonth.value !== index + 1) {
      selectedMonth.value = index + 1
    }
  } else {
    if (selectedDay.value !== index + 1) {
      selectedDay.value = index + 1
    }
  }
}

function handleOverlayClick() {
  emit('cancel')
}

function handleCancel() {
  emit('cancel')
}

function handleConfirm() {
  const y = selectedYear.value
  const m = String(selectedMonth.value).padStart(2, '0')
  const d = String(selectedDay.value).padStart(2, '0')
  const dateStr = `${y}-${m}-${d}`
  emit('update:modelValue', dateStr)
  emit('confirm', dateStr)
}

onMounted(() => {
  initFromValue()
  
  ;[yearCol, monthCol, dayCol].forEach((colRef, i) => {
    const type = ['year', 'month', 'day'][i]
    if (colRef.value) {
      colRef.value.addEventListener('scroll', () => onScroll(type), { passive: true })
    }
  })
})
</script>

<style scoped>
.picker-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  z-index: 1000;
  display: flex;
  align-items: flex-end;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.picker-container {
  width: 100%;
  background: linear-gradient(180deg, #1a1a2e 0%, #0f0f1a 100%);
  border-radius: 24px 24px 0 0;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from { transform: translateY(100%); }
  to { transform: translateY(0); }
}

.picker-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid rgba(212, 175, 55, 0.1);
}

.picker-btn {
  padding: 8px 16px;
  font-size: 15px;
  background: none;
  border: none;
  cursor: pointer;
  font-family: inherit;
}

.picker-btn.cancel {
  color: var(--text-muted);
}

.picker-btn.confirm {
  color: var(--gold-primary);
  font-weight: 600;
}

.picker-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.picker-body {
  display: flex;
  height: 220px;
  position: relative;
  padding: 0 10px;
}

.wheel-col {
  flex: 1;
  overflow-y: scroll;
  scroll-snap-type: y mandatory;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
  -ms-overflow-style: none;
  mask-image: linear-gradient(to bottom, transparent 0%, black 25%, black 75%, transparent 100%);
  -webkit-mask-image: linear-gradient(to bottom, transparent 0%, black 25%, black 75%, transparent 100%);
  padding: 88px 0;
  box-sizing: border-box;
}

.wheel-col::-webkit-scrollbar {
  display: none;
}

.wheel-item {
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 17px;
  color: var(--text-muted);
  scroll-snap-align: center;
  transition: all 0.15s ease;
}

.wheel-item.active {
  color: var(--gold-primary);
  font-size: 20px;
  font-weight: 600;
}

.wheel-highlight {
  position: absolute;
  left: 10px;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  height: 44px;
  background: rgba(212, 175, 55, 0.08);
  border-top: 1px solid rgba(212, 175, 55, 0.25);
  border-bottom: 1px solid rgba(212, 175, 55, 0.25);
  pointer-events: none;
  border-radius: 8px;
}

.wheel-mask-top,
.wheel-mask-bottom {
  position: absolute;
  left: 0;
  right: 0;
  height: 88px;
  pointer-events: none;
  z-index: 1;
}

.wheel-mask-top {
  top: 0;
  background: linear-gradient(to bottom, #1a1a2e, transparent);
}

.wheel-mask-bottom {
  bottom: 0;
  background: linear-gradient(to top, #0f0f1a, transparent);
}
</style>
