const app = getApp()

Page({
  data: {
    matchId: null,
    matchData: null,
    userA: null,
    userB: null,
    userBId: null,
    loading: true,
    activeTab: 'love',
    displayScore: 0,
    displayScoreColor: '#c9a050',
    displayScoreLabel: '一般',
    dimDisplay: null,
    resultLocked: false,  // 匹配结果是否锁定
  },

  onLoad(options) {
    this.setData({ matchId: options.id, userBId: options.friendId })
    this.loadMatchResult()
  },

  async loadMatchResult() {
    try {
      let res
      if (this.data.userBId) {
        res = await app.request({
          url: '/match/nfc/' + this.data.userBId,
          method: 'POST'
        })
      } else {
        res = await app.request({
          url: '/match/' + this.data.matchId,
          method: 'GET'
        })
      }

      // 检查是否锁定
      if (res.locked) {
        this.setData({
          resultLocked: true,
          userA: res.user_a_nickname || '用户A',
          userB: res.user_b_nickname || '用户B',
          loading: false
        })
        wx.showToast({ title: res.message || '请看完广告解锁', icon: 'none' })
        return
      }

      const matchData = res.match_data || res.result
      const userAName = res.user_a_nickname || res.user_a?.nickname || '用户A'
      const userBName = res.user_b_nickname || res.user_b?.nickname || '用户B'
      const userBId = res.user_b_id || res.user_b?.user_id || this.data.userBId

      const overallScore = matchData?.overall_score || 0
      const activeTab = matchData?.dimensions?.love ? 'love' : 'career'
      const dimKey = activeTab
      const dimData = matchData?.dimensions?.[dimKey] || {}

      this.setData({
        matchData,
        userA: userAName,
        userB: userBName,
        userBId: userBId,
        loading: false,
        resultLocked: false,
        activeTab,
        displayScore: overallScore,
        displayScoreColor: this._getScoreColor(overallScore),
        displayScoreLabel: this._getScoreLabel(overallScore),
        dimDisplay: {
          score: dimData.score || 0,
          scoreColor: this._getScoreColor(dimData.score || 0),
          tags: dimData.tags || [],
          summary: dimData.summary || '',
          advice: dimData.advice || '',
        }
      })
    } catch (err) {
      console.error(err)
      wx.showToast({ title: '加载失败', icon: 'none' })
    }
  },

  // 观看激励视频广告解锁匹配结果
  watchAdToUnlockMatch() {
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
          // 用户完整观看广告，解锁匹配结果
          this.unlockMatchResult()
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

  // 调用后端接口解锁匹配结果
  async unlockMatchResult() {
    try {
      const res = await app.request({
        url: '/match/' + this.data.matchId + '/unlock',
        method: 'POST'
      })
      if (!res.locked && res.match_data) {
        this.setData({ resultLocked: false })
        this.loadMatchResult()
        wx.showToast({ title: '解锁成功', icon: 'success' })
      }
    } catch (err) {
      console.error(err)
      wx.showToast({ title: '解锁失败', icon: 'none' })
    }
  },

  _getScoreColor(score) {
    if (score >= 80) return '#50c878'
    if (score >= 65) return '#c9a050'
    return '#e06060'
  },

  _getScoreLabel(score) {
    if (score >= 80) return '极佳'
    if (score >= 65) return '较好'
    if (score >= 50) return '一般'
    return '待提升'
  },

  switchTab(e) {
    const tab = e.currentTarget.dataset.tab
    const dims = this.data.matchData?.dimensions || {}
    const dimData = dims[tab] || {}
    this.setData({
      activeTab: tab,
      dimDisplay: {
        score: dimData.score || 0,
        scoreColor: this._getScoreColor(dimData.score || 0),
        tags: dimData.tags || [],
        summary: dimData.summary || '',
        advice: dimData.advice || '',
      }
    })
  },

  saveToAlbum() {
    wx.showLoading({ title: '生成中...' })
    const token = wx.getStorageSync('token')
    wx.downloadFile({
      url: `${app.globalData.baseUrl}/share/match/${this.data.matchId}/image`,
      header: { Authorization: 'Bearer ' + token },
      success: (res) => {
        wx.hideLoading()
        wx.saveImageToPhotosAlbum({
          filePath: res.tempFilePath,
          success: () => {
            wx.showToast({ title: '已保存到相册', icon: 'success' })
          },
          fail: () => {
            wx.showToast({ title: '保存失败', icon: 'none' })
          }
        })
      },
      fail: () => {
        wx.hideLoading()
        wx.showToast({ title: '生成失败', icon: 'none' })
      }
    })
  },

  addFriend() {
    if (!this.data.userBId) return
    app.request({
      url: '/match/add-friend/' + this.data.userBId,
      method: 'POST'
    }).then(() => {
      wx.showToast({ title: '已添加好友', icon: 'success' })
    }).catch(err => {
      wx.showToast({ title: err.detail || '添加失败', icon: 'none' })
    })
  },

  onShareTap() {
    wx.showToast({
      title: '点击右上角 ··· 分享给好友',
      icon: 'none',
      duration: 2000
    })
  },

  onShareAppMessage() {
    const userB = this.data.userB || '对方'
    const score = this.data.displayScore || 0
    return {
      title: `我和${userB}的缘分指数${score}分`,
      path: '/pages/index/index'
    }
  }
})
