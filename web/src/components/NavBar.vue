<template>
  <header class="nav-bar">
    <div v-if="showBack" class="nav-back" @click="$router.back()">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
        <polyline points="15 18 9 12 15 6"></polyline>
      </svg>
    </div>
    <div class="nav-title">{{ title }}</div>
    <div class="nav-right">
      <slot name="right"></slot>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const title = computed(() => {
  const titles = {
    'Index': '',
    'Match': '八字合缘',
    'Profile': '个人中心',
    'Fortune': '今日运势',
    'BirthInput': '输入生辰',
    'ChartDetail': '命盘详情',
    'BaziDetail': '八字排盘',
    'LifeKline': '人生K线'
  }
  return titles[router.currentRoute.value.name] || ''
})

const showBack = computed(() => !router.currentRoute.value.meta.showTabBar)
</script>

<style scoped>
.nav-bar {
  height: 56px;
  background: rgba(5, 5, 16, 0.95);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  border-bottom: 1px solid rgba(212, 175, 55, 0.15);
  flex-shrink: 0;
  padding: 0 16px;
  z-index: 100;
}

.nav-title {
  font-family: 'Cinzel', serif;
  font-size: 18px;
  font-weight: 600;
  color: #f5f5f7;
  letter-spacing: 2px;
}

.nav-back {
  position: absolute;
  left: 12px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #d4af37;
  cursor: pointer;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.nav-back:active {
  background: rgba(212, 175, 55, 0.1);
  transform: scale(0.9);
}

.nav-right {
  position: absolute;
  right: 16px;
}
</style>
