const app = getApp()

Page({
  data: {
    chartType: 'ziwei',
    solarLunar: 'solar',
    solarDate: '',
    lunarDate: '',
    gender: '',
    hourIndex: 1,
    hourText: '',
    hours: [
      { index: 0, name: '早子时', time: '23:00-00:00' },
      { index: 1, name: '丑时', time: '01:00-03:00' },
      { index: 2, name: '寅时', time: '03:00-05:00' },
      { index: 3, name: '卯时', time: '05:00-07:00' },
      { index: 4, name: '辰时', time: '07:00-09:00' },
      { index: 5, name: '巳时', time: '09:00-11:00' },
      { index: 6, name: '午时', time: '11:00-13:00' },
      { index: 7, name: '未时', time: '13:00-15:00' },
      { index: 8, name: '申时', time: '15:00-17:00' },
      { index: 9, name: '酉时', time: '17:00-19:00' },
      { index: 10, name: '戌时', time: '19:00-21:00' },
      { index: 11, name: '亥时', time: '21:00-23:00' }
    ],
    loading: false,
    dateText: '请选择日期',
    ownerType: 'self',
    remark: ''
  },

  onLoad(options) {
    if (options.type) {
      this.setData({ chartType: options.type })
    }
    const today = new Date()
    const defaultDate = `${today.getFullYear()}-${today.getMonth() + 1}-${today.getDate()}`
    this.setData({
      solarDate: defaultDate,
      dateText: defaultDate,
      hourText: this.data.hours[1].name + ' ' + this.data.hours[1].time
    })
  },

  switchChartType(e) {
    this.setData({ chartType: e.currentTarget.dataset.type })
  },

  switchSolarLunar(e) {
    const type = e.currentTarget.dataset.type
    this.setData({
      solarLunar: type,
      dateText: '请选择日期'
    })
  },

  onDateChange(e) {
    this.setData({
      solarDate: e.detail.value,
      dateText: e.detail.value
    })
  },

  selectGender(e) {
    this.setData({ gender: e.currentTarget.dataset.gender })
  },

  selectHour(e) {
    const index = e.currentTarget.dataset.index
    const hour = this.data.hours[index]
    this.setData({
      hourIndex: index,
      hourText: hour.name + ' ' + hour.time
    })
  },

  switchOwnerType(e) {
    this.setData({ ownerType: e.currentTarget.dataset.type })
  },

  onRemarkInput(e) {
    this.setData({ remark: e.detail.value })
  },

  async submit() {
    if (!this.data.solarDate) {
      wx.showToast({ title: '请选择出生日期', icon: 'none' })
      return
    }
    if (!this.data.gender) {
      wx.showToast({ title: '请选择性别', icon: 'none' })
      return
    }
    if (this.data.ownerType === 'helped' && !this.data.remark.trim()) {
      wx.showToast({ title: '请填写备注', icon: 'none' })
      return
    }

    const token = wx.getStorageSync('token')
    if (!token) {
      wx.showToast({ title: '请先登录', icon: 'none' })
      setTimeout(() => {
        wx.switchTab({ url: '/pages/profile/profile' })
      }, 1000)
      return
    }

    this.setData({ loading: true })

    try {
      if (this.data.chartType === 'bazi') {
        setTimeout(() => {
          wx.redirectTo({
            url: `/pages/bazi-detail/bazi-detail?date_str=${this.data.solarDate}&hour_index=${this.data.hourIndex}&gender=${this.data.gender === '男' ? 'male' : 'female'}&owner_type=${this.data.ownerType}&remark=${encodeURIComponent(this.data.remark)}`
          })
        }, 500)
      } else {
        const res = await app.request({
          url: '/users/save-chart',
          method: 'POST',
          data: {
            solar_date: this.data.solarDate,
            lunar_date: null,
            gender: this.data.gender,
            hour_index: this.data.hourIndex,
            is_default: this.data.ownerType === 'self',
            remark: this.data.ownerType === 'helped' ? this.data.remark : ''
          }
        })

        wx.showToast({ title: '排盘成功', icon: 'success' })
        setTimeout(() => {
          wx.redirectTo({
            url: '/pages/chart-detail/chart-detail?id=' + res.id
          })
        }, 1000)
      }
    } catch (err) {
      console.error(err)
    } finally {
      this.setData({ loading: false })
    }
  }
})
