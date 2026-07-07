Page({
  data: {
    loading: true,
    todayDate: '',
    dayGanzhi: '',
    fortune: {
      overall_score: 0,
      love_score: 0,
      career_score: 0,
      wealth_score: 0,
      health_score: 0,
      lucky_color: '',
      lucky_number: '',
      lucky_direction: '',
      do_list: [],
      avoid_list: [],
      phrase: '',
      chart_name: ''
    },
    checkinStatus: {
      has_checkin_today: false,
      checkin_days: 0,
      checkin_total: 0
    },
    checkinReward: null,
    enableAds: false,
    bannerAdUnitId: ''
  },

  onLoad() {
    this.formatTodayDate()
    this.initData()
  },

  async initData() {
    const app = getApp()
    try {
      // 确保已登录，未登录时自动静默登录
      if (!app.globalData.token) {
        await app.ensureLogin()
      }
    } catch (err) {
      console.error('登录失败', err)
      wx.showToast({ title: '请先登录', icon: 'none' })
      return
    }
    this.loadFortune()
    this.loadCheckinStatus()
    this.loadAdConfig()
  },

  onShow() {
    // 每次显示时更新活跃时间
    this.updateActiveTime()
  },

  formatTodayDate() {
    const today = new Date()
    const year = today.getFullYear()
    const month = today.getMonth() + 1
    const day = today.getDate()
    const weekdays = ['日', '一', '二', '三', '四', '五', '六']
    const weekday = weekdays[today.getDay()]
    
    this.setData({
      todayDate: `${year}年${month}月${day}日 星期${weekday}`
    })
  },

  async loadFortune() {
    const app = getApp()
    this.setData({ loading: true })
    
    try {
      const res = await app.request({
        url: '/fortune/today',
        method: 'GET'
      })
      
      this.setData({
        fortune: res,
        dayGanzhi: res.day_ganzhi || '',
        loading: false
      })
      
      // 记录行为日志
      this.logAction('fortune_view', { score: res.overall_score })
    } catch (err) {
      console.error('加载运势失败', err)
      this.setData({ loading: false })
      wx.showToast({ title: '加载失败，请先创建命盘', icon: 'none' })
    }
  },

  async loadCheckinStatus() {
    const app = getApp()
    
    try {
      const res = await app.request({
        url: '/fortune/checkin/status',
        method: 'GET'
      })
      
      this.setData({ checkinStatus: res })
    } catch (err) {
      console.error('加载签到状态失败', err)
    }
  },

  async doCheckin() {
    if (this.data.checkinStatus.has_checkin_today) {
      return
    }

    const app = getApp()

    // 确保已登录
    if (!app.globalData.token) {
      try {
        await app.ensureLogin()
      } catch (err) {
        console.error('登录失败', err)
        wx.showToast({ title: '请先登录', icon: 'none' })
        return
      }
    }

    try {
      const res = await app.request({
        url: '/fortune/checkin',
        method: 'POST'
      })

      if (res.success) {
        this.setData({
          checkinStatus: {
            has_checkin_today: true,
            checkin_days: res.checkin_days,
            checkin_total: res.checkin_total
          },
          checkinReward: res.reward
        })

        wx.showToast({ title: '签到成功', icon: 'success' })

        // 记录行为日志
        this.logAction('checkin', { days: res.checkin_days })
      } else {
        wx.showToast({ title: res.message || '已签到', icon: 'none' })
      }
    } catch (err) {
      console.error('签到失败', err)
      // 401 已由 request 处理，这里提示其他错误
      if (err && err.detail) {
        wx.showToast({ title: err.detail, icon: 'none' })
      } else {
        wx.showToast({ title: '签到失败', icon: 'none' })
      }
    }
  },

  async loadAdConfig() {
    const app = getApp()
    
    try {
      const res = await app.request({
        url: '/admin/config',
        method: 'GET'
      })
      
      if (res.enable_ads && res.enable_ads.value === 'true') {
        this.setData({
          enableAds: true,
          bannerAdUnitId: res.ad_banner_unit_id?.value || ''
        })
      }
    } catch (err) {
      // 广告配置加载失败不影响主功能
      console.log('广告配置未加载')
    }
  },

  async updateActiveTime() {
    const app = getApp()
    // 后端在请求时会自动更新活跃时间，这里不需要额外处理
  },

  logAction(action, detail) {
    // 用户行为日志（后端会在请求中自动记录）
    console.log('action:', action, detail)
  },

  onShareAppMessage() {
    const fortune = this.data.fortune
    return {
      title: `今日运势 ${fortune.overall_score}分 - ${fortune.phrase}`,
      path: '/pages/index/index',
      imageUrl: '' // 可以设置分享图片
    }
  }
})