import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { request } from '@/utils/request'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(JSON.parse(localStorage.getItem('userInfo') || 'null'))

  const isLoggedIn = computed(() => !!token.value)

  function setToken(newToken) {
    token.value = newToken
    localStorage.setItem('token', newToken)
  }

  function setUser(newUser) {
    user.value = newUser
    localStorage.setItem('userInfo', JSON.stringify(newUser))
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
  }

  async function login(phone, password) {
    const res = await request.post('/auth/login', { phone, password })
    setToken(res.access_token)
    setUser(res.user)
    return res
  }

  async function register(phone, password, nickname) {
    const res = await request.post('/auth/register', { 
      phone, 
      password, 
      nickname: nickname || '星运用户' 
    })
    setToken(res.access_token)
    setUser(res.user)
    return res
  }

  return { token, user, isLoggedIn, setToken, setUser, logout, login, register }
})
