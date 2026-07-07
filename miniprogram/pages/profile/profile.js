const app = getApp()

Page({
  data: {
    userInfo: null,
    showLogin: false,
    aiProvider: 'mock',
    showFriends: false,
    friends: [],
    aiApiKey: '',
    aiModel: 'gpt-3.5-turbo',
    aiBaseUrl: '',
    serverBaseUrl: '',
    showServerConfig: false,
    loading: false
  },

  onShow() {
    const userInfo = wx.getStorageSync('userInfo')
    const serverBaseUrl = wx.getStorageSync('baseUrl') || ''
    if (userInfo) {
      this.setData({
        userInfo,
        aiProvider: userInfo.ai_provider || 'mock',
        aiModel: userInfo.ai_model || 'gpt-3.5-turbo',
        aiBaseUrl: userInfo.ai_base_url || '',
        serverBaseUrl
      })
    } else {
      this.setData({ serverBaseUrl })
    }
    if (userInfo && wx.getStorageSync('token')) {
      this.loadFriends()
    }
  },

  showLoginModal() {
    this.setData({ showLogin: true })
  },

  closeLoginModal() {
    this.setData({ showLogin: false })
  },

  wechatLogin() {
    if (this.data.loading) return
    this.setData({ loading: true })

    wx.login({
      success: (loginRes) => {
        console.log('wx.login success:', loginRes)
        if (!loginRes.code) {
          wx.showToast({ title: '登录失败', icon: 'none' })
          this.setData({ loading: false })
          return
        }
        this.doLogin(loginRes.code)
      },
      fail: (err) => {
        console.error('wx.login fail:', err)
        wx.showToast({ title: '微信登录失败', icon: 'none' })
        this.setData({ loading: false })
      }
    })
  },

  doLogin(code) {
    wx.request({
      url: getApp().globalData.baseUrl + '/auth/wechat-login',
      method: 'POST',
      data: { code: code, nickname: '微信用户' },
      timeout: 10000,
      header: { 'Content-Type': 'application/json' },
      success: (res) => {
        console.log('login response:', res)
        if (res.statusCode === 200 && res.data && res.data.access_token) {
          const data = res.data
          wx.setStorageSync('token', data.access_token)
          wx.setStorageSync('userInfo', data.user)
          const app = getApp()
          app.globalData.token = data.access_token
          app.globalData.userInfo = data.user
          this.setData({ userInfo: data.user, showLogin: false, loading: false })
          wx.showToast({ title: '登录成功', icon: 'success' })
          this.loadFriends()
        } else {
          wx.showToast({ title: '登录失败', icon: 'none' })
          this.setData({ loading: false })
        }
      },
      fail: (err) => {
        console.error('login request fail:', err)
        wx.showToast({ title: '网络错误', icon: 'none' })
        this.setData({ loading: false })
      }
    })
  },

  logout() {
    wx.showModal({
      title: '确认退出',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          wx.removeStorageSync('token')
          wx.removeStorageSync('userInfo')
          app.globalData.token = ''
          app.globalData.userInfo = null
          this.setData({ userInfo: null, friends: [] })
          wx.showToast({ title: '已退出', icon: 'success' })
        }
      }
    })
  },

  goBirthInput() {
    wx.navigateTo({ url: '/pages/birth-input/birth-input' })
  },

  selectAiProvider(e) {
    const provider = e.currentTarget.dataset.provider
    const defaults = {
      mock: { model: '', baseUrl: '' },
      volcengine: { model: 'doubao-pro-32k', baseUrl: 'https://ark.cn-beijing.volces.com/api/v3' },
      openai: { model: 'gpt-3.5-turbo', baseUrl: '' },
      tongyi: { model: 'qwen-turbo', baseUrl: '' }
    }
    const def = defaults[provider] || { model: '', baseUrl: '' }
    this.setData({
      aiProvider: provider,
      aiModel: def.model,
      aiBaseUrl: def.baseUrl
    })
  },

  async saveAiSettings() {
    if (this.data.aiProvider !== 'mock' && !this.data.aiApiKey) {
      wx.showToast({ title: '请输入 API Key', icon: 'none' })
      return
    }
    this.setData({ loading: true })
    try {
      const res = await app.request({
        url: '/users/me',
        method: 'PUT',
        data: {
          ai_provider: this.data.aiProvider,
          ai_api_key: this.data.aiApiKey,
          ai_model: this.data.aiModel,
          ai_base_url: this.data.aiBaseUrl
        }
      })
      wx.setStorageSync('userInfo', res)
      wx.showToast({ title: '保存成功', icon: 'success' })
    } catch (err) {
      console.error(err)
    } finally {
      this.setData({ loading: false })
    }
  },

  onAiApiKeyInput(e) {
    this.setData({ aiApiKey: e.detail.value })
  },
  onAiModelInput(e) {
    this.setData({ aiModel: e.detail.value })
  },
  onAiBaseUrlInput(e) {
    this.setData({ aiBaseUrl: e.detail.value })
  },

  toggleServerConfig() {
    this.setData({ showServerConfig: !this.data.showServerConfig })
  },

  onServerBaseUrlInput(e) {
    this.setData({ serverBaseUrl: e.detail.value })
  },

  saveServerBaseUrl() {
    const url = this.data.serverBaseUrl.trim()
    if (!url) {
      wx.showToast({ title: '请输入服务地址', icon: 'none' })
      return
    }
    wx.setStorageSync('baseUrl', url)
    getApp().globalData.baseUrl = url
    wx.showToast({ title: '保存成功，重启小程序生效', icon: 'success' })
  },

  resetServerBaseUrl() {
    wx.removeStorageSync('baseUrl')
    const defaultUrl = 'http://192.168.1.2:8000/api/v1'
    getApp().globalData.baseUrl = defaultUrl
    this.setData({ serverBaseUrl: defaultUrl })
    wx.showToast({ title: '已恢复默认', icon: 'success' })
  },

  toggleFriends() {
    this.setData({ showFriends: !this.data.showFriends })
  },

  async loadFriends() {
    try {
      const res = await app.request({ url: '/match/friends/list', method: 'GET' })
      this.setData({ friends: res || [] })
    } catch (err) {
      console.error(err)
    }
  },

  async removeFriend(e) {
    const friendId = e.currentTarget.dataset.id
    wx.showModal({
      title: '确认删除',
      content: '确定删除该好友？',
      success: async (res) => {
        if (res.confirm) {
          try {
            await app.request({
              url: '/match/friends/' + friendId,
              method: 'DELETE'
            })
            wx.showToast({ title: '已删除', icon: 'success' })
            this.loadFriends()
          } catch (err) {
            console.error(err)
          }
        }
      }
    })
  },

  goMatchWithFriend(e) {
    const friendId = e.currentTarget.dataset.id
    wx.navigateTo({ url: '/pages/match-result/match-result?friendId=' + friendId })
  }
})
