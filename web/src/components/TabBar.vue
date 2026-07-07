<template>
  <nav class="tab-bar">
    <div 
      v-for="tab in tabs" 
      :key="tab.path"
      class="tab-item"
      :class="{ active: currentPath === tab.path }"
      @click="$router.push(tab.path)"
    >
      <div class="tab-icon">{{ tab.icon }}</div>
      <div class="tab-text">{{ tab.text }}</div>
    </div>
  </nav>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const tabs = [
  { path: '/', icon: '✨', text: '星盘' },
  { path: '/match', icon: '👥', text: '配对' },
  { path: '/profile', icon: '👤', text: '我的' }
]

const currentPath = computed(() => router.currentRoute.value.path)
</script>

<style scoped>
.tab-bar {
  height: 100rpx;
  background: #0f0f20;
  display: flex;
  border-top: 1rpx solid rgba(201, 160, 80, 0.1);
  flex-shrink: 0;
}

.tab-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4rpx;
  color: #666680;
  cursor: pointer;
  transition: color 0.3s ease;
}

.tab-item.active {
  color: #c9a050;
}

.tab-icon {
  font-size: 40rpx;
}

.tab-text {
  font-size: 22rpx;
}
</style>
