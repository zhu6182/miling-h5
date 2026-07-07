const app = getApp()

Page({
  data: {
    hasLogin: false,
    userInfo: null,
    showQRModal: false,
    qrCode: '',
    qrImageUrl: '',
    matchType: 'all',
    matchTypes: [
      { value: 'all', label: '全部分析', desc: '姻缘+事业+友谊+贵人' },
      { value: 'love', label: '姻缘匹配', desc: '只看感情契合度' },
      { value: 'career', label: '事业合作', desc: '只看事业配合度' },
    ],
    matchHistory: [],
    loading: false,
    hasCharts: false,
  },

  onShow() {
    const token = wx.getStorageSync('token')
    const userInfo = wx.getStorageSync('userInfo')
    this.setData({
      hasLogin: !!token,
      userInfo
    })
    if (token) {
      this.loadCharts()
      this.loadMatchHistory()
    }
  },

  goLogin() {
    wx.switchTab({ url: '/pages/profile/profile' })
  },

  loadCharts() {
    app.request({
      url: '/users/me/charts',
      method: 'GET'
    }).then(res => {
      this.setData({ hasCharts: res && res.length > 0 })
    }).catch(() => {
      this.setData({ hasCharts: false })
    })
  },

  loadMatchHistory() {
    app.request({
      url: '/match/history',
      method: 'GET'
    }).then(res => {
      this.setData({ matchHistory: res || [] })
    }).catch(() => {
      this.setData({ matchHistory: [] })
    })
  },

  selectMatchType(e) {
    const type = e.currentTarget.dataset.type
    this.setData({ matchType: type })
  },

  async generateQR() {
    if (!this.data.hasCharts) {
      wx.showToast({ title: '请先创建命盘', icon: 'none' })
      setTimeout(() => wx.navigateTo({ url: '/pages/birth-input/birth-input' }), 1000)
      return
    }
    this.setData({ loading: true })
    try {
      const res = await app.request({
        url: '/match/create-qr',
        method: 'POST',
        data: { match_type: this.data.matchType }
      })
      this.setData({
        showQRModal: true,
        qrCode: res.qr_code,
        qrImageUrl: `${app.globalData.baseUrl}/match/qr/${res.qr_code}/image`
      })
    } catch (err) {
      console.error(err)
    } finally {
      this.setData({ loading: false })
    }
  },

  closeQRModal() {
    this.setData({ showQRModal: false })
    this.loadMatchHistory()
  },

  scanQR() {
    if (!this.data.hasCharts) {
      wx.showToast({ title: '请先创建命盘', icon: 'none' })
      setTimeout(() => wx.navigateTo({ url: '/pages/birth-input/birth-input' }), 1000)
      return
    }
    wx.scanCode({
      success: (res) => {
        const qrCode = res.result || res
        if (qrCode && qrCode.length === 12) {
          this.doScanMatch(qrCode)
        } else {
          wx.showToast({ title: '无效的配对码', icon: 'none' })
        }
      },
      fail: () => {
        wx.showToast({ title: '扫码失败', icon: 'none' })
      }
    })
  },

  async doScanMatch(qrCode) {
    wx.showLoading({ title: '匹配中...' })
    try {
      const res = await app.request({
        url: '/match/scan/' + qrCode,
        method: 'POST'
      })
      wx.hideLoading()
      if (res.status === 'accepted') {
        wx.navigateTo({
          url: '/pages/match-result/match-result?id=' + res.match_id
        })
      }
    } catch (err) {
      wx.hideLoading()
      console.error(err)
    }
  },

  goMatchResult(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({
      url: '/pages/match-result/match-result?id=' + id
    })
  },

  showComingSoon() {
    wx.showToast({ title: 'NFC 功能开发中', icon: 'none' })
  },

  onShareAppMessage() {
    const userInfo = wx.getStorageSync('userInfo')
    return {
      title: '命里 - 来和我配对命盘',
      path: '/pages/index/index?from=share',
      imageUrl: '/images/share-cover.png'
    }
  }
})
