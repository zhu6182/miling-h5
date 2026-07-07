const app = getApp()

Page({
  data: {
    chartId: null,
    chart: null,
    reading: null,
    loading: true,
    generating: false,
    palaceGrid: [],
    soulBranch: '',
    fourHuaTags: [],
    calAnswers: {},
    readingLocked: false,
    showMatchModal: false,
    chartsLoading: false,
    allCharts: [],
    filteredCharts: [],
    showAddFriendModal: false,
    friendName: '',
    friendDate: '',
    friendHour: '',
    friendGender: 'male'
  },

  onLoad(options) {
    this.setData({ chartId: options.id })
    this.loadChart()
  },

  selectCalAnswer(e) {
    const qIndex = e.currentTarget.dataset.qindex
    const answer = e.currentTarget.dataset.answer
    const calAnswers = { ...this.data.calAnswers }
    calAnswers[qIndex] = answer
    this.setData({ calAnswers })
  },

  submitCalibration() {
    const total = this.data.reading.calibration_questions.length
    const answered = Object.keys(this.data.calAnswers).length
    if (answered < total) {
      wx.showToast({ title: `请回答全部 ${total} 个问题`, icon: 'none' })
      return
    }
    wx.showToast({ title: '校准成功，解读已更新', icon: 'success' })
  },

  async loadChart() {
    try {
      const chart = await app.request({
        url: `/charts/${this.data.chartId}`,
        method: 'GET'
      })
      this.setData({ chart })
      this.buildPalaceGrid(chart.chart_data)
      if (chart.reading_data) {
        this.setData({ reading: chart.reading_data })
      }
      if (chart.reading_unlocked === false) {
        this.setData({ readingLocked: true })
      }
    } catch (err) {
      console.error(err)
    } finally {
      this.setData({ loading: false })
    }
  },

  goBaziDetail() {
    const chart = this.data.chart
    if (!chart) return
    const gender = chart.gender === '男' ? 'male' : (chart.gender === '女' ? 'female' : chart.gender)
    wx.redirectTo({
      url: `/pages/bazi-detail/bazi-detail?date_str=${chart.solar_date}&hour_index=${chart.hour_index}&gender=${gender}`
    })
  },

  buildPalaceGrid(chartData) {
    if (!chartData || !chartData.palaces) return
    const branchGridMap = {
      '巳': { row: 1, col: 1 }, '午': { row: 1, col: 2 },
      '未': { row: 1, col: 3 }, '申': { row: 1, col: 4 },
      '辰': { row: 2, col: 1 }, '酉': { row: 2, col: 4 },
      '卯': { row: 3, col: 1 }, '戌': { row: 3, col: 4 },
      '寅': { row: 4, col: 1 }, '丑': { row: 4, col: 2 },
      '子': { row: 4, col: 3 }, '亥': { row: 4, col: 4 }
    }
    const grid = {}
    chartData.palaces.forEach(p => {
      const pos = branchGridMap[p.earthly_branch]
      if (pos) {
        grid[`${pos.row}-${pos.col}`] = p
      }
    })
    const cells = []
    for (let row = 1; row <= 4; row++) {
      for (let col = 1; col <= 4; col++) {
        if (row >= 2 && row <= 3 && col >= 2 && col <= 3) {
          cells.push({ isCenter: row === 2 && col === 2 })
        } else {
          cells.push({ palace: grid[`${row}-${col}`] || null })
        }
      }
    }
    this.setData({
      palaceGrid: cells,
      soulBranch: chartData.soul_palace_branch,
      fourHuaTags: chartData.year_mutagens || []
    })
  },

  // 观看激励视频广告解锁AI解读
  watchAdToUnlockReading() {
    let rewardedVideoAd = null
    try {
      rewardedVideoAd = wx.createRewardedVideoAd({
        adUnitId: 'xxxxxxxx' // 替换为实际的广告位ID
      })
      rewardedVideoAd.onLoad(() => {
        console.log('激励视频广告加载成功')
      })
      rewardedVideoAd.onError((err) => {
        console.error('激励视频广告加载失败', err)
        wx.showToast({ title: '广告加载失败，请重试', icon: 'none' })
      })
      rewardedVideoAd.onClose((res) => {
        if (res.isEnded) {
          // 用户完整观看广告，解锁AI解读
          this.setData({ readingLocked: false })
          this.generateReading()
        } else {
          wx.showToast({ title: '请完整观看广告', icon: 'none' })
        }
        rewardedVideoAd && rewardedVideoAd.destroy()
      })
      rewardedVideoAd.load().then(() => {
        rewardedVideoAd.show()
      }).catch(err => {
        console.error('激励视频广告显示失败', err)
        wx.showToast({ title: '广告加载失败，请重试', icon: 'none' })
      })
    } catch (e) {
      console.error('激励视频广告创建失败', e)
      wx.showToast({ title: '广告功能暂不可用', icon: 'none' })
    }
  },

  async generateReading() {
    if (this.data.generating) return

    if (this.data.readingLocked) {
      this.watchAdToUnlockReading()
      return
    }

    this.setData({ generating: true })
    wx.showLoading({ title: 'AI 解读中...', mask: true })

    try {
      // 1. 发起异步生成
      const startRes = await app.request({
        url: `/charts/${this.data.chartId}/reading/start`,
        method: 'POST',
        data: { ad_watched: !this.data.readingLocked }
      })

      if (startRes.locked) {
        this.setData({ readingLocked: true })
        wx.showToast({ title: startRes.message || '请看完广告解锁', icon: 'none' })
        return
      }

      const taskId = startRes.task_id

      // 2. 轮询结果（最多30次，每3秒一次，共90秒）
      const maxPolls = 30
      for (let i = 0; i < maxPolls; i++) {
        await new Promise(r => setTimeout(r, 3000))
        const statusRes = await app.request({
          url: `/charts/${this.data.chartId}/reading/status`,
          data: { task_id: taskId }
        })
        if (statusRes.status === 'completed') {
          this.setData({ reading: statusRes.result.reading })
          wx.showToast({ title: '解读完成', icon: 'success' })
          return
        }
        if (statusRes.status === 'failed') {
          wx.showToast({ title: '生成失败：' + (statusRes.error || ''), icon: 'none' })
          return
        }
        if (statusRes.status === 'not_found') {
          wx.showToast({ title: '任务不存在', icon: 'none' })
          return
        }
        // 更新loading文字显示已等待时间
        wx.showLoading({ title: `AI 解读中...${(i + 1) * 3}s`, mask: true })
      }
      // 超时
      wx.showToast({ title: '生成超时，请重试', icon: 'none' })
    } catch (err) {
      console.error(err)
      wx.showToast({ title: '生成失败', icon: 'none' })
    } finally {
      wx.hideLoading()
      this.setData({ generating: false })
    }
  },

  openMatchSelector() {
    this.setData({ showMatchModal: true })
    this.loadCharts()
  },

  closeMatchSelector() {
    this.setData({ showMatchModal: false })
  },

  stopPropagation() {},

  async loadCharts() {
    this.setData({ chartsLoading: true })
    try {
      const res = await app.request({
        url: '/charts',
        method: 'GET'
      })
      const charts = Array.isArray(res) ? res : (res.charts || [])
      const filtered = charts.filter(c => c.id !== this.data.chartId)
      this.setData({
        allCharts: charts,
        filteredCharts: filtered
      })
    } catch (err) {
      console.error(err)
    } finally {
      this.setData({ chartsLoading: false })
    }
  },

  async selectChartForMatch(e) {
    const chartBId = e.currentTarget.dataset.id
    if (!chartBId) return
    this.setData({ showMatchModal: false })
    wx.showLoading({ title: '匹配中...', mask: true })
    try {
      const res = await app.request({
        url: '/match/direct',
        method: 'POST',
        data: {
          chart_a_id: this.data.chartId,
          chart_b_id: chartBId,
          match_type: 'all'
        }
      })
      const matchId = res.id || res.match_id
      if (matchId) {
        wx.navigateTo({
          url: '/pages/match-result/match-result?id=' + matchId
        })
      } else {
        wx.showToast({ title: '匹配失败', icon: 'none' })
      }
    } catch (err) {
      console.error(err)
    } finally {
      wx.hideLoading()
    }
  },

  openAddFriendChart() {
    this.setData({ showAddFriendModal: true })
  },

  closeAddFriendChart() {
    this.setData({
      showAddFriendModal: false,
      friendName: '',
      friendDate: '',
      friendHour: '',
      friendGender: 'male'
    })
  },

  stopPropagation() {},

  bindFriendNameInput(e) {
    this.setData({ friendName: e.detail.value })
  },

  bindFriendDateInput(e) {
    this.setData({ friendDate: e.detail.value })
  },

  bindFriendHourInput(e) {
    const hourList = ['子时', '丑时', '寅时', '卯时', '辰时', '巳时', '午时', '未时', '申时', '酉时', '戌时', '亥时']
    this.setData({ friendHour: hourList[e.detail.value] })
  },

  switchFriendGender(e) {
    this.setData({ friendGender: e.currentTarget.dataset.gender })
  },

  async saveFriendChart() {
    const { friendName, friendDate, friendHour, friendGender } = this.data
    if (!friendName.trim()) {
      wx.showToast({ title: '请输入好友备注名', icon: 'none' })
      return
    }
    if (!friendDate) {
      wx.showToast({ title: '请选择出生日期', icon: 'none' })
      return
    }
    if (!friendHour) {
      wx.showToast({ title: '请选择出生时辰', icon: 'none' })
      return
    }

    wx.showLoading({ title: '保存中...', mask: true })
    try {
      const hourMap = {
        '子时': 0, '丑时': 1, '寅时': 2, '卯时': 3,
        '辰时': 4, '巳时': 5, '午时': 6, '未时': 7,
        '申时': 8, '酉时': 9, '戌时': 10, '亥时': 11
      }
      const hourIndex = hourMap[friendHour] !== undefined ? hourMap[friendHour] : 6

      const res = await app.request({
        url: '/users/save-chart',
        method: 'POST',
        data: {
          solar_date: friendDate,
          gender: friendGender === 'male' ? '男' : '女',
          hour_index: hourIndex,
          name: friendName,
          remark: friendName,
          is_default: false
        }
      })

      wx.showToast({ title: '添加成功', icon: 'success' })
      this.closeAddFriendChart()
      this.loadCharts()
    } catch (err) {
      wx.showToast({ title: '保存失败', icon: 'none' })
    } finally {
      wx.hideLoading()
    }
  },

  onShareTap() {
    wx.showToast({
      title: '点击右上角 ··· 分享给好友',
      icon: 'none',
      duration: 2000
    })
  },

  onShareAppMessage() {
    const chart = this.data.chart
    const name = chart?.name || '我'
    return {
      title: `来看看${name}的命盘解读`,
      path: '/pages/index/index'
    }
  }
})
