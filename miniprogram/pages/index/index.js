const app = getApp()

Page({
  data: {
    userInfo: null,
    hasChart: false,
    chart: null,
    loading: false,
    activeTab: 'my',
    myCharts: [],
    helpedCharts: []
  },

  onShow() {
    const token = wx.getStorageSync('token')
    const userInfo = wx.getStorageSync('userInfo')
    if (token && userInfo) {
      this.setData({ userInfo })
      this.loadCharts('my')
      this.loadCharts('helped')
    }
  },

  goLogin() {
    wx.switchTab({
      url: '/pages/profile/profile'
    })
  },

  goBirthInput() {
    wx.navigateTo({
      url: '/pages/birth-input/birth-input'
    })
  },

  goBaziInput() {
    const chart = this.data.chart
    if (chart && chart.solar_date) {
      const gender = chart.gender === '男' ? 'male' : (chart.gender === '女' ? 'female' : chart.gender)
      wx.navigateTo({
        url: `/pages/bazi-detail/bazi-detail?date_str=${chart.solar_date}&hour_index=${chart.hour_index}&gender=${gender}`
      })
    } else {
      wx.navigateTo({
        url: '/pages/birth-input/birth-input?type=bazi'
      })
    }
  },

  goLifeKLine() {
    const chart = this.data.chart
    if (chart && chart.solar_date) {
      const gender = chart.gender === '男' ? 'male' : (chart.gender === '女' ? 'female' : chart.gender)
      wx.navigateTo({
        url: `/pages/life-kline/life-kline?date_str=${chart.solar_date}&hour_index=${chart.hour_index}&gender=${gender}`
      })
    } else {
      wx.navigateTo({
        url: '/pages/birth-input/birth-input?type=bazi'
      })
    }
  },

  goFortune() {
    wx.navigateTo({
      url: '/pages/fortune/fortune'
    })
  },

  goDetail(e) {
    const id = e.currentTarget.dataset.id || this.data.chart.id
    wx.navigateTo({
      url: '/pages/chart-detail/chart-detail?id=' + id
    })
  },

  switchTab(e) {
    const tab = e.currentTarget.dataset.tab
    if (tab === this.data.activeTab) return
    this.setData({ activeTab: tab })
  },

  loadCharts(type) {
    this.setData({ loading: true })
    app.request({
      url: '/users/me/charts?type=' + type,
      method: 'GET'
    }).then(res => {
      if (type === 'my') {
        if (res && res.length > 0) {
          const defaultChart = res.find(c => c.is_default) || res[0]
          this.setData({
            hasChart: true,
            chart: defaultChart,
            myCharts: res
          })
        } else {
          this.setData({
            hasChart: false,
            myCharts: []
          })
        }
      } else {
        this.setData({
          helpedCharts: res || []
        })
      }
    }).catch(() => {
      if (type === 'my') {
        this.setData({ hasChart: false, myCharts: [] })
      } else {
        this.setData({ helpedCharts: [] })
      }
    }).finally(() => {
      this.setData({ loading: false })
    })
  }
})
