<template>
  <nav class="tab-bar" aria-label="底部导航">
    <button 
      v-for="tab in tabs" 
      :key="tab.path"
      class="tab-item"
      :class="{ active: currentPath === tab.path }"
      @click="$router.push(tab.path)"
      @keydown.enter="$router.push(tab.path)"
      @keydown.space.prevent="$router.push(tab.path)"
    >
      <span class="tab-icon">{{ tab.icon }}</span>
      <span class="tab-text">{{ tab.text }}</span>
    </button>
  </nav>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const tabs = [
  { path: '/', icon: '☯', text: '命盘' },
  { path: '/match', icon: '💕', text: '合缘' },
  { path: '/profile', icon: '👤', text: '我的' }
]

const currentPath = computed(() => router.currentRoute.value.path)
</script>

<style scoped>
.tab-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 64px;
  background: rgba(5, 5, 16, 0.98);
  backdrop-filter: blur(30px);
  -webkit-backdrop-filter: blur(30px);
  display: flex;
  border-top: 1px solid rgba(139, 92, 246, 0.1);
  padding-bottom: env(safe-area-inset-bottom);
  z-index: 100;
  box-shadow: 0 -2px 20px rgba(0, 0, 0, 0.3);
}

.tab-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  color: rgba(128, 128, 160, 0.6);
  border: none;
  background: transparent;
  cursor: pointer;
  transition: color 0.3s ease;
}

.tab-item.active {
  color: #d4af37;
}

.tab-icon {
  font-size: 26px;
  transition: transform 0.3s ease, filter 0.3s ease;
}

.tab-item.active .tab-icon {
  transform: scale(1.1);
  filter: drop-shadow(0 0 8px rgba(212, 175, 55, 0.6));
}

.tab-text {
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 0.5px;
}

.tab-item.active .tab-text {
  text-shadow: 0 0 6px rgba(212, 175, 55, 0.4);
}
</style>
