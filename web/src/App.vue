<template>
  <div id="app">
    <NavBar />
    <main class="page-container">
      <router-view />
    </main>
    <TabBar v-if="showTabBar" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import NavBar from '@/components/NavBar.vue'
import TabBar from '@/components/TabBar.vue'

const router = useRouter()

const showTabBar = computed(() => router.currentRoute.value.meta.showTabBar)
</script>
