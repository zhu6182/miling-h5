<template>
  <header class="nav-bar">
    <div v-if="showBack" class="nav-back" @click="$router.back()">‹</div>
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
    'Index': '星运日记',
    'Match': '星座配对',
    'Profile': '我的',
    'Fortune': '今日运势',
    'BirthInput': '星座信息录入',
    'ChartDetail': '星盘详情',
    'MatchResult': '配对结果',
    'BaziDetail': '八字详情',
    'LifeKline': '人生K线'
  }
  return titles[router.currentRoute.value.name] || '星运日记'
})

const showBack = computed(() => !router.currentRoute.value.meta.showTabBar)
</script>

<style scoped>
.nav-bar {
  height: 88rpx;
  background: #0f0f20;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  border-bottom: 1rpx solid rgba(201, 160, 80, 0.1);
  flex-shrink: 0;
  padding: 0 32rpx;
}

.nav-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #e0e0f0;
}

.nav-back {
  position: absolute;
  left: 24rpx;
  font-size: 48rpx;
  color: #c9a050;
  cursor: pointer;
  width: 60rpx;
  height: 60rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-right {
  position: absolute;
  right: 24rpx;
}
</style>
