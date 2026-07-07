const DEFAULT_BASE_URL = 'http://192.168.1.2:8000/api/v1'

App({
  globalData: {
    userInfo: null,
    token: '',
    baseUrl: DEFAULT_BASE_URL
  },

  onLaunch() {
    try {
      const token = wx.getStorageSync('token') || ''
      const userInfo = wx.getStorageSync('userInfo') || null
      const customBaseUrl = wx.getStorageSync('baseUrl')
      this.globalData.token = token
      this.globalData.userInfo = userInfo
      if (customBaseUrl) {
        this.globalData.baseUrl = customBaseUrl
      }
    } catch (e) {
      console.error('onLaunch error:', e)
    }
  },

  // 静默登录：若 token 不存在或失效，自动用 wx.login 换取 token
  ensureLogin() {
    if (this._loginPromise) {
      return this._loginPromise
    }
    if (this.globalData.token) {
      return Promise.resolve(this.globalData.token)
    }
    this._loginPromise = new Promise((resolve, reject) => {
      wx.login({
        success: (loginRes) => {
          if (!loginRes.code) {
            this._loginPromise = null
            reject(new Error('wx.login 无 code'))
            return
          }
          wx.request({
            url: this.globalData.baseUrl + '/auth/wechat-login',
            method: 'POST',
            data: { code: loginRes.code, nickname: '微信用户' },
            timeout: 10000,
            header: { 'Content-Type': 'application/json' },
            success: (res) => {
              if (res.statusCode === 200 && res.data && res.data.access_token) {
                const data = res.data
                wx.setStorageSync('token', data.access_token)
                wx.setStorageSync('userInfo', data.user)
                this.globalData.token = data.access_token
                this.globalData.userInfo = data.user
                resolve(data.access_token)
              } else {
                reject(new Error('登录失败'))
              }
            },
            fail: (err) => {
              reject(err)
            },
            complete: () => {
              this._loginPromise = null
            }
          })
        },
        fail: (err) => {
          this._loginPromise = null
          reject(err)
        }
      })
    })
    return this._loginPromise
  },

  request(options) {
    return new Promise((resolve, reject) => {
      const silent = options.silent || false
      wx.request({
        url: this.globalData.baseUrl + options.url,
        method: options.method || 'GET',
        data: options.data || {},
        timeout: options.timeout || 10000,
        header: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + (this.globalData.token || '')
        },
        success: (res) => {
          if (res.statusCode === 200) {
            resolve(res.data)
          } else if (res.statusCode === 401) {
            wx.removeStorageSync('token')
            wx.removeStorageSync('userInfo')
            this.globalData.token = ''
            this.globalData.userInfo = null
            if (!silent) {
              wx.showToast({ title: '请先登录', icon: 'none' })
            }
            reject(res.data)
          } else {
            if (!silent) {
              wx.showToast({ title: res.data && res.data.detail ? res.data.detail : '请求失败', icon: 'none' })
            }
            reject(res.data)
          }
        },
        fail: (err) => {
          console.error('request fail:', options.url, err)
          if (!silent) {
            wx.showToast({ title: '网络错误', icon: 'none' })
          }
          reject(err)
        }
      })
    })
  }
})
