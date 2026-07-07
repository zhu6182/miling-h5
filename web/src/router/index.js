import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Index',
    component: () => import('@/pages/Index.vue'),
    meta: { showTabBar: true }
  },
  {
    path: '/match',
    name: 'Match',
    component: () => import('@/pages/Match.vue'),
    meta: { showTabBar: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/pages/Profile.vue'),
    meta: { showTabBar: true }
  },
  {
    path: '/fortune',
    name: 'Fortune',
    component: () => import('@/pages/Fortune.vue'),
    meta: { showTabBar: false }
  },
  {
    path: '/birth-input',
    name: 'BirthInput',
    component: () => import('@/pages/BirthInput.vue'),
    meta: { showTabBar: false }
  },
  {
    path: '/chart-detail/:id',
    name: 'ChartDetail',
    component: () => import('@/pages/ChartDetail.vue'),
    meta: { showTabBar: false }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
