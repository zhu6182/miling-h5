<template>
  <div id="app">
    <StarField />
    <NavBar v-if="showNavBar" />
    <main class="router-view-container">
      <router-view v-slot="{ Component, route }">
        <keep-alive :include="cachedPages">
          <component :is="Component" :key="route.fullPath" />
        </keep-alive>
      </router-view>
    </main>
    <TabBar v-if="showTabBar" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import NavBar from '@/components/NavBar.vue'
import TabBar from '@/components/TabBar.vue'
import StarField from '@/components/StarField.vue'

const router = useRouter()

const cachedPages = ['Index', 'Match', 'Profile', 'Charts']

const showTabBar = computed(() => router.currentRoute.value.meta.showTabBar)
const showNavBar = computed(() => {
  const hideRoutes = ['Index']
  return !hideRoutes.includes(router.currentRoute.value.name)
})
</script>

<style>
#app {
  min-height: 100vh;
  position: relative;
  z-index: 1;
}
</style>
