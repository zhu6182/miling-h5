Page({
  data: {
    loading: true,
    generating: false,
    bazi: null,
    reading: '',
    date_str: '',
    hour_index: 6,
    gender: 'male',
    activeTab: 'base',
    wuxingList: [],
    chartId: null,
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
    const date_str = options.date_str || ''
    const hour_index = parseInt(options.hour_index || '6')
    const gender = options.gender || 'male'
    this.setData({ date_str, hour_index, gender })
    this.loadBazi()
  },

  _getTwelveZhiIndex(zhi) {
    const zhiList = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
    return zhiList.indexOf(zhi)
  },

  _calcTwelveLongevity(dayGan, zhi) {
    const diShiNames = ['长生', '沐浴', '冠带', '临官', '帝旺', '衰', '病', '死', '墓', '绝', '胎', '养']
    const zhiIndex = this._getTwelveZhiIndex(zhi)
    if (zhiIndex < 0) return ''

    const yangGanChangSheng = {
      '甲': 11,
      '丙': 2,
      '戊': 2,
      '庚': 5,
      '壬': 8,
    }
    const yinGanChangSheng = {
      '乙': 6,
      '丁': 9,
      '己': 9,
      '辛': 0,
      '癸': 3,
    }

    const isYang = ['甲', '丙', '戊', '庚', '壬'].indexOf(dayGan) >= 0
    const changShengZhi = isYang ? yangGanChangSheng[dayGan] : yinGanChangSheng[dayGan]

    if (changShengZhi === undefined) return ''

    let offset
    if (isYang) {
      offset = (zhiIndex - changShengZhi + 12) % 12
    } else {
      offset = (changShengZhi - zhiIndex + 12) % 12
    }

    return diShiNames[offset]
  },

  _getShiShenType(shiShen) {
    if (!shiShen) return ''
    const cai = ['偏财', '正财']
    const guan = ['七杀', '正官']
    const yin = ['偏印', '正印']
    const bi = ['比肩', '劫财']
    const shi = ['食神', '伤官']

    if (cai.indexOf(shiShen) >= 0) return 'cai'
    if (guan.indexOf(shiShen) >= 0) return 'guan'
    if (yin.indexOf(shiShen) >= 0) return 'yin'
    if (bi.indexOf(shiShen) >= 0) return 'bi'
    if (shi.indexOf(shiShen) >= 0) return 'shi'
    return ''
  },

  _extractXunKong(xunKongStr) {
    if (!xunKongStr) return ''
    const parts = xunKongStr.split('旬空')
    return parts.length > 1 ? parts[1] : xunKongStr
  },

  async loadBazi() {
    const app = getApp()
    this.setData({ loading: true })
    try {
      const res = await app.request({
        url: '/bazi/calculate',
        method: 'POST',
        data: {
          date_str: this.data.date_str,
          hour_index: this.data.hour_index,
          gender: this.data.gender
        }
      })
      const wuxingList = []
      const count = res.wuxing.count
      const maxCount = Math.max(count['金'], count['木'], count['水'], count['火'], count['土'], 1)
      const wuxingKeyMap = { '金': 'jin', '木': 'mu', '水': 'shui', '火': 'huo', '土': 'tu' }
      for (const key of ['金', '木', '水', '火', '土']) {
        wuxingList.push({
          name: key,
          key: wuxingKeyMap[key],
          count: count[key],
          pct: Math.round((count[key] / maxCount) * 100)
        })
      }
      res.wuxingList = wuxingList
      res.wuxing.total = count['金'] + count['木'] + count['水'] + count['火'] + count['土']

      const ganColorMap = {
        '甲': '#80e0a0', '乙': '#80e0a0',
        '丙': '#f08080', '丁': '#f08080',
        '戊': '#d0a070', '己': '#d0a070',
        '庚': '#f0d080', '辛': '#f0d080',
        '壬': '#80b0f0', '癸': '#80b0f0',
      }
      const zhiColorMap = {
        '子': '#80b0f0', '丑': '#d0a070',
        '寅': '#80e0a0', '卯': '#80e0a0',
        '辰': '#d0a070', '巳': '#f08080',
        '午': '#f08080', '未': '#d0a070',
        '申': '#f0d080', '酉': '#f0d080',
        '戌': '#d0a070', '亥': '#80b0f0',
      }
      res.ganColorMap = ganColorMap
      res.zhiColorMap = zhiColorMap

      const dayGan = res.pillars.day.gan

      const zizuo = {
        year: this._calcTwelveLongevity(dayGan, res.pillars.year.zhi),
        month: this._calcTwelveLongevity(dayGan, res.pillars.month.zhi),
        day: this._calcTwelveLongevity(dayGan, res.pillars.day.zhi),
        hour: this._calcTwelveLongevity(dayGan, res.pillars.hour.zhi),
      }
      res.zizuo = zizuo

      const xunkongZhi = {
        year: this._extractXunKong(res.xun_kong.year),
        month: this._extractXunKong(res.xun_kong.month),
        day: this._extractXunKong(res.xun_kong.day),
        hour: this._extractXunKong(res.xun_kong.hour),
      }
      res.xunkongZhi = xunkongZhi

      const hiddenStemsWithColor = {
        year: res.hidden_stems.year.map((item) => ({ text: item, color: ganColorMap[item] })),
        month: res.hidden_stems.month.map((item) => ({ text: item, color: ganColorMap[item] })),
        day: res.hidden_stems.day.map((item) => ({ text: item, color: ganColorMap[item] })),
        hour: res.hidden_stems.hour.map((item) => ({ text: item, color: ganColorMap[item] })),
      }
      res.hiddenStemsWithColor = hiddenStemsWithColor

      const zhiShiShenWithType = {
        year: res.ten_gods.zhi.year.map((item) => ({ text: item, type: this._getShiShenType(item) })),
        month: res.ten_gods.zhi.month.map((item) => ({ text: item, type: this._getShiShenType(item) })),
        day: res.ten_gods.zhi.day.map((item) => ({ text: item, type: this._getShiShenType(item) })),
        hour: res.ten_gods.zhi.hour.map((item) => ({ text: item, type: this._getShiShenType(item) })),
      }
      res.zhiShiShenWithType = zhiShiShenWithType

      const ganShiShenWithType = {
        year: { text: res.ten_gods.gan.year, type: this._getShiShenType(res.ten_gods.gan.year) },
        month: { text: res.ten_gods.gan.month, type: this._getShiShenType(res.ten_gods.gan.month) },
        day: { text: '日主', type: 'day' },
        hour: { text: res.ten_gods.gan.hour, type: this._getShiShenType(res.ten_gods.gan.hour) },
      }
      res.ganShiShenWithType = ganShiShenWithType

      const tableRows = [
        {
          label: '藏干',
          cells: [
            hiddenStemsWithColor.year,
            hiddenStemsWithColor.month,
            hiddenStemsWithColor.day,
            hiddenStemsWithColor.hour,
          ],
          multiLine: true
        },
        {
          label: '副星',
          cells: [
            zhiShiShenWithType.year,
            zhiShiShenWithType.month,
            zhiShiShenWithType.day,
            zhiShiShenWithType.hour,
          ],
          multiLine: true
        },
        {
          label: '星运',
          cells: [res.di_shi.year, res.di_shi.month, res.di_shi.day, res.di_shi.hour],
          multiLine: false
        },
        {
          label: '自坐',
          cells: [zizuo.year, zizuo.month, zizuo.day, zizuo.hour],
          multiLine: false
        },
        {
          label: '空亡',
          cells: [xunkongZhi.year, xunkongZhi.month, xunkongZhi.day, xunkongZhi.hour],
          multiLine: false
        },
        {
          label: '纳音',
          cells: [res.nayin.year, res.nayin.month, res.nayin.day, res.nayin.hour],
          multiLine: false
        },
      ]
      res.tableRows = tableRows

      this.setData({ bazi: res })
    } catch (e) {
      wx.showToast({ title: '排盘失败', icon: 'none' })
    }
    this.setData({ loading: false })
  },

  switchTab(e) {
    this.setData({ activeTab: e.currentTarget.dataset.tab })
  },

  async goZiweiDetail() {
    const app = getApp()
    try {
      const res = await app.request({
        url: '/users/save-chart',
        method: 'POST',
        data: {
          solar_date: this.data.date_str,
          gender: this.data.gender === 'male' ? '男' : '女',
          hour_index: this.data.hour_index,
          is_default: false,
          name: '八字同步命盘'
        }
      })
      wx.redirectTo({
        url: '/pages/chart-detail/chart-detail?id=' + res.id
      })
    } catch (e) {
      wx.showToast({ title: '跳转失败', icon: 'none' })
    }
  },

  goLifeKLine() {
    wx.navigateTo({
      url: `/pages/life-kline/life-kline?date_str=${this.data.date_str}&hour_index=${this.data.hour_index}&gender=${this.data.gender}`
    })
  },

  async generateReading() {
    if (this.data.generating) return
    const app = getApp()
    this.setData({ generating: true })
    wx.showLoading({ title: 'AI 解读中...', mask: true })

    try {
      // 1. 发起异步生成
      const startRes = await app.request({
        url: '/bazi/reading/start',
        method: 'POST',
        data: {
          date_str: this.data.date_str,
          hour_index: this.data.hour_index,
          gender: this.data.gender
        }
      })

      if (startRes.locked) {
        wx.showToast({ title: startRes.message || '请看完广告解锁', icon: 'none' })
        return
      }

      const taskId = startRes.task_id

      // 2. 轮询结果（最多30次，每3秒一次，共90秒）
      const maxPolls = 30
      for (let i = 0; i < maxPolls; i++) {
        await new Promise(r => setTimeout(r, 3000))
        const statusRes = await app.request({
          url: `/bazi/reading/status/${taskId}`
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
    } catch (e) {
      wx.showToast({ title: '生成失败', icon: 'none' })
    } finally {
      wx.hideLoading()
      this.setData({ generating: false })
    }
  },

  async openMatchSelector() {
    if (!this.data.chartId) {
      wx.showLoading({ title: '保存命盘中...', mask: true })
      try {
        const app = getApp()
        const res = await app.request({
          url: '/users/save-chart',
          method: 'POST',
          data: {
            solar_date: this.data.date_str,
            gender: this.data.gender === 'male' ? '男' : '女',
            hour_index: this.data.hour_index,
            is_default: false,
            name: '八字匹配命盘'
          }
        })
        this.setData({ chartId: res.id })
      } catch (e) {
        wx.hideLoading()
        wx.showToast({ title: '保存命盘失败', icon: 'none' })
        return
      }
      wx.hideLoading()
    }
    this.setData({ showMatchModal: true })
    this.loadCharts()
  },

  closeMatchSelector() {
    this.setData({ showMatchModal: false })
  },

  stopPropagation() {},

  async loadCharts() {
    const app = getApp()
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
    if (!chartBId || !this.data.chartId) return
    this.setData({ showMatchModal: false })
    wx.showLoading({ title: '匹配中...', mask: true })
    try {
      const app = getApp()
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
    this.setData({
      showAddFriendModal: true,
      friendName: '',
      friendDate: '',
      friendHour: '',
      friendGender: 'male'
    })
  },

  closeAddFriendChart() {
    this.setData({ showAddFriendModal: false })
  },

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
      const app = getApp()
      const hourMap = {
        '子时': 0, '丑时': 1, '寅时': 2, '卯时': 3,
        '辰时': 4, '巳时': 5, '午时': 6, '未时': 7,
        '申时': 8, '酉时': 9, '戌时': 10, '亥时': 11
      }
      const hourIndex = hourMap[friendHour] !== undefined ? hourMap[friendHour] : 6

      await app.request({
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
    const bazi = this.data.bazi
    const name = bazi?.name || '我'
    return {
      title: `来看看${name}的命盘解读`,
      path: '/pages/index/index'
    }
  }
})
