import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const baseURL = import.meta.env.VITE_API_URL || '/api/v1'

const instance = axios.create({
  baseURL: baseURL,
  timeout: 10000
})

instance.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

instance.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      const authStore = useAuthStore()
      authStore.logout()
      window.location.href = '/profile'
    }
    const message = error.response?.data?.detail || '请求失败'
    alert(message)
    return Promise.reject(error)
  }
)

export const request = instance
