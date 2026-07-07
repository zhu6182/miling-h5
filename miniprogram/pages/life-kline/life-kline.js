Page({
  data: {
    loading: true,
    generating: false,
    date_str: '',
    hour_index: 6,
    gender: 'male',
    klineData: null,
    chartPoints: [],
    analysis: null,
    selectedPoint: null,
    canvasWidth: 0,
    canvasHeight: 0,
    peakYear: null,
    lowYear: null,
    currentAge: null,
    scoreList: []
  },

  onLoad(options) {
    const date_str = options.date_str || ''
    const hour_index = parseInt(options.hour_index || '6')
    const gender = options.gender || 'male'
    this.setData({ date_str, hour_index, gender })
    this.generateKLine()
  },

  async generateKLine() {
    if (this.data.generating) return
    const app = getApp()
    this.setData({ generating: true })
    wx.showLoading({ title: '生成K线中...', mask: true })

    try {
      // 1. 发起异步生成（设置较长超时，避免网络波动导致失败）
      const startRes = await app.request({
        url: '/bazi/kline/start',
        method: 'POST',
        data: {
          date_str: this.data.date_str,
          hour_index: this.data.hour_index,
          gender: this.data.gender
        },
        timeout: 30000
      })

      const taskId = startRes.task_id

      // 2. 轮询结果（最多60次，每2秒一次，共120秒）
      const maxPolls = 60
      for (let i = 0; i < maxPolls; i++) {
        await new Promise(r => setTimeout(r, 2000))
        try {
          const statusRes = await app.request({
            url: `/bazi/kline/status/${taskId}`,
            timeout: 15000,
            silent: true
          })
          if (statusRes.status === 'completed') {
            const klineData = statusRes.result.kline_data
            this.processKLineData(klineData)
            wx.showToast({ title: '生成完成', icon: 'success' })
            return
          }
          if (statusRes.status === 'failed') {
            wx.showModal({ title: '生成失败', content: statusRes.error || '请稍后重试', showCancel: false })
            return
          }
          if (statusRes.status === 'not_found') {
            wx.showToast({ title: '任务不存在', icon: 'none' })
            return
          }
          wx.showLoading({ title: `推演中...${(i + 1) * 2}s`, mask: true })
        } catch (pollErr) {
          // 单次轮询失败不中断，继续重试
          console.warn('poll error:', pollErr)
          wx.showLoading({ title: `重连中...${(i + 1) * 2}s`, mask: true })
        }
      }
      wx.showModal({
        title: '生成超时',
        content: 'AI推演时间较长，是否继续等待？',
        confirmText: '继续等待',
        cancelText: '放弃',
        success: (res) => {
          if (res.confirm) {
            this.generateKLine()
          }
        }
      })
    } catch (e) {
      console.error('kline error:', e)
      const errMsg = (e && e.errMsg) ? e.errMsg : '网络错误'
      wx.showModal({
        title: '生成失败',
        content: errMsg.includes('timeout') ? '网络连接超时，请检查网络后重试' : errMsg,
        showCancel: false
      })
    } finally {
      wx.hideLoading()
      this.setData({ generating: false })
    }
  },

  processKLineData(klineData) {
    const points = klineData.chartPoints || []
    if (points.length === 0) {
      wx.showToast({ title: '数据为空', icon: 'none' })
      return
    }

    // 找到巅峰年和低谷年
    let peak = points[0]
    let low = points[0]
    for (const p of points) {
      if (p.high > peak.high) peak = p
      if (p.low < low.low) low = p
    }

    // 找到当前年龄
    const birthYear = points[0].year
    const currentYear = new Date().getFullYear()
    const currentAge = currentYear - birthYear + 1

    // 构建分析数据
    const analysis = {
      summary: klineData.summary,
      summaryScore: klineData.summaryScore,
      personality: klineData.personality,
      personalityScore: klineData.personalityScore,
      industry: klineData.industry,
      industryScore: klineData.industryScore,
      wealth: klineData.wealth,
      wealthScore: klineData.wealthScore,
      marriage: klineData.marriage,
      marriageScore: klineData.marriageScore,
      health: klineData.health,
      healthScore: klineData.healthScore,
      family: klineData.family,
      familyScore: klineData.familyScore,
    }

    // 构建评分列表用于柱状图
    const scoreList = points.map(p => ({
      age: p.age,
      score: p.score,
      isUp: p.close >= p.open
    }))

    // 大运解读数据
    const dayunAnalysis = klineData.dayunAnalysis || []

    this.setData({
      klineData,
      chartPoints: points,
      analysis,
      scoreList,
      peakYear: peak,
      lowYear: low,
      currentAge,
      dayunAnalysis,
      loading: false
    })

    // 等待页面渲染后绘制K线图
    setTimeout(() => {
      this.drawKLineChart()
    }, 300)
  },

  drawKLineChart() {
    const points = this.data.chartPoints
    if (!points || points.length === 0) return

    const query = wx.createSelectorQuery()
    query.select('#klineCanvas').boundingClientRect()
    query.exec((res) => {
      if (!res || !res[0]) return
      const rect = res[0]
      const width = rect.width
      const height = rect.height
      this.setData({ canvasWidth: width, canvasHeight: height })
      this._drawCanvas(width, height)
    })
  },

  _drawCanvas(width, height) {
    const points = this.data.chartPoints
    const ctx = wx.createCanvasContext('klineCanvas')

    // 背景渐变
    const bgGrad = ctx.createLinearGradient(0, 0, 0, height)
    bgGrad.addColorStop(0, 'rgba(15, 15, 35, 0.6)')
    bgGrad.addColorStop(1, 'rgba(10, 10, 26, 0.9)')
    ctx.setFillStyle(bgGrad)
    ctx.fillRect(0, 0, width, height)

    // 边距
    const padLeft = 8
    const padRight = 8
    const padTop = 20
    const padBottom = 30
    const chartW = width - padLeft - padRight
    const chartH = height - padTop - padBottom

    // 计算价格范围
    let minLow = 999
    let maxHigh = 0
    for (const p of points) {
      if (p.low < minLow) minLow = p.low
      if (p.high > maxHigh) maxHigh = p.high
    }
    const range = maxHigh - minLow || 100
    const yScale = chartH / range

    // 横坐标：年龄刻度
    const pointWidth = chartW / points.length
    const candleWidth = Math.max(pointWidth * 0.6, 1)

    // 绘制水平网格线
    ctx.setStrokeStyle('rgba(255, 255, 255, 0.05)')
    ctx.setLineWidth(0.5)
    for (let i = 0; i <= 4; i++) {
      const y = padTop + (chartH / 4) * i
      ctx.beginPath()
      ctx.moveTo(padLeft, y)
      ctx.lineTo(width - padRight, y)
      ctx.stroke()
      // Y轴标签
      const val = Math.round(maxHigh - (range / 4) * i)
      ctx.setFillStyle('rgba(136, 136, 160, 0.6)')
      ctx.setFontSize(8)
      ctx.fillText(val, padLeft + 2, y - 2)
    }

    // 找大运分界点
    const dayunChanges = []
    for (let i = 0; i < points.length; i++) {
      if (i === 0 || points[i].daYun !== points[i - 1].daYun) {
        dayunChanges.push({ index: i, daYun: points[i].daYun })
      }
    }

    // 绘制大运分界线
    ctx.setStrokeStyle('rgba(201, 160, 80, 0.2)')
    ctx.setLineWidth(0.5)
    ctx.setLineDash([3, 3])
    for (const dc of dayunChanges) {
      const x = padLeft + pointWidth * dc.index
      ctx.beginPath()
      ctx.moveTo(x, padTop)
      ctx.lineTo(x, padTop + chartH)
      ctx.stroke()
      // 大运标签
      if (dc.index > 0 && dc.index < points.length - 2) {
        ctx.setFillStyle('rgba(201, 160, 80, 0.5)')
        ctx.setFontSize(7)
        ctx.fillText(dc.daYun, x + 1, padTop + 8)
      }
    }
    ctx.setLineDash([])

    // 绘制K线
    for (let i = 0; i < points.length; i++) {
      const p = points[i]
      const x = padLeft + pointWidth * i + pointWidth / 2
      const isUp = p.close >= p.open

      const openY = padTop + (maxHigh - p.open) * yScale
      const closeY = padTop + (maxHigh - p.close) * yScale
      const highY = padTop + (maxHigh - p.high) * yScale
      const lowY = padTop + (maxHigh - p.low) * yScale

      const color = isUp ? '#22c55e' : '#ef4444'
      const strokeColor = isUp ? '#16a34a' : '#dc2626'

      // 上下影线
      ctx.setStrokeStyle(strokeColor)
      ctx.setLineWidth(1)
      ctx.beginPath()
      ctx.moveTo(x, highY)
      ctx.lineTo(x, lowY)
      ctx.stroke()

      // 实体
      const bodyTop = Math.min(openY, closeY)
      const bodyH = Math.max(Math.abs(closeY - openY), 1.5)
      ctx.setFillStyle(color)
      ctx.fillRect(x - candleWidth / 2, bodyTop, candleWidth, bodyH)
      ctx.setStrokeStyle(strokeColor)
      ctx.setLineWidth(0.5)
      ctx.strokeRect(x - candleWidth / 2, bodyTop, candleWidth, bodyH)
    }

    // 标记巅峰年
    const peak = this.data.peakYear
    if (peak) {
      const peakIdx = points.indexOf(peak)
      const peakX = padLeft + pointWidth * peakIdx + pointWidth / 2
      const peakY = padTop + (maxHigh - peak.high) * yScale
      // 红星
      ctx.setFillStyle('#fbbf24')
      ctx.beginPath()
      ctx.arc(peakX, peakY - 8, 3, 0, 2 * Math.PI)
      ctx.fill()
      ctx.setFillStyle('rgba(251, 191, 36, 0.8)')
      ctx.setFontSize(8)
      ctx.fillText('★' + peak.score, peakX - 10, peakY - 12)
    }

    // X轴标签（每10岁一个）
    ctx.setFillStyle('rgba(136, 136, 160, 0.6)')
    ctx.setFontSize(8)
    for (let i = 0; i < points.length; i += 10) {
      const x = padLeft + pointWidth * i + pointWidth / 2
      ctx.fillText(points[i].age + '岁', x - 8, height - padBottom + 12)
    }

    // 当前年龄指示线
    const currentAge = this.data.currentAge
    if (currentAge && currentAge > 0 && currentAge <= points.length) {
      const curIdx = currentAge - 1
      const curX = padLeft + pointWidth * curIdx + pointWidth / 2
      ctx.setStrokeStyle('rgba(201, 160, 80, 0.6)')
      ctx.setLineWidth(1)
      ctx.setLineDash([2, 2])
      ctx.beginPath()
      ctx.moveTo(curX, padTop)
      ctx.lineTo(curX, padTop + chartH)
      ctx.stroke()
      ctx.setLineDash([])
      ctx.setFillStyle('#c9a050')
      ctx.setFontSize(7)
      ctx.fillText('现在', curX - 10, padTop - 4)
    }

    ctx.draw()
  },

  onChartTap(e) {
    const points = this.data.chartPoints
    if (!points || points.length === 0) return

    const touch = e.detail
    const x = touch.x
    const width = this.data.canvasWidth
    if (!width) return

    const padLeft = 8
    const padRight = 8
    const chartW = width - padLeft - padRight
    const pointWidth = chartW / points.length

    const idx = Math.floor((x - padLeft) / pointWidth)
    if (idx >= 0 && idx < points.length) {
      this.setData({ selectedPoint: points[idx] })
    }
  },

  closeDetail() {
    this.setData({ selectedPoint: null })
  },

  getScoreColor(score) {
    if (score >= 80) return '#22c55e'
    if (score >= 60) return '#c9a050'
    if (score >= 40) return '#f08080'
    return '#ef4444'
  },

  onShareTap() {
    // 兜底：若用户点击旧的tap按钮（已改为open-type=share，此函数不再被调用）
    wx.showToast({
      title: '点击右上角 ··· 也可分享',
      icon: 'none',
      duration: 2000
    })
  },

  onShareAppMessage() {
    const peak = this.data.peakYear
    const title = peak
      ? `我的人生巅峰在${peak.age}岁，来看看你的人生K线！`
      : '来看看我的人生K线运势图！'
    return {
      title: title,
      path: '/pages/index/index',
      imageUrl: ''
    }
  },

  onShareTimeline() {
    const peak = this.data.peakYear
    return {
      title: peak
        ? `人生K线：巅峰${peak.age}岁${peak.score}分，你的运势如何？`
        : '将一生运势化作K线图，来看看你的人生走势！'
    }
  }
})
