<template>
  <div class="birth-input-page container">
    <div class="form-section">
      <div class="section-label">分析方式</div>
      <div class="option-row">
        <div 
          class="option-item" 
          :class="{ active: chartType === 'ziwei' }"
          @click="chartType = 'ziwei'"
        >星盘解析</div>
        <div 
          class="option-item" 
          :class="{ active: chartType === 'bazi' }"
          @click="chartType = 'bazi'"
        >性格测试</div>
      </div>
    </div>

    <div class="form-section">
      <div class="section-label">历法类型</div>
      <div class="option-row">
        <div 
          class="option-item" 
          :class="{ active: isLunar === false }"
          @click="isLunar = false"
        >公历</div>
        <div 
          class="option-item" 
          :class="{ active: isLunar === true }"
          @click="isLunar = true"
        >农历</div>
      </div>
    </div>

    <div class="form-section">
      <div class="section-label">出生日期</div>
      <input type="date" class="form-input" v-model="birthDate" />
    </div>

    <div class="form-section">
      <div class="section-label">出生时辰</div>
      <div class="hour-grid">
        <div 
          v-for="(hour, index) in hours" 
          :key="index"
          class="hour-item"
          :class="{ active: hourIndex === index }"
          @click="hourIndex = index"
        >{{ hour }}</div>
      </div>
    </div>

    <div class="form-section">
      <div class="section-label">性别</div>
      <div class="option-row">
        <div 
          class="option-item" 
          :class="{ active: gender === 'male' }"
          @click="gender = 'male'"
        >男</div>
        <div 
          class="option-item" 
          :class="{ active: gender === 'female' }"
          @click="gender = 'female'"
        >女</div>
      </div>
    </div>

    <div class="form-section">
      <div class="section-label">查询对象</div>
      <div class="option-row">
        <div 
          class="option-item" 
          :class="{ active: isSelf === true }"
          @click="isSelf = true"
        >为自己查</div>
        <div 
          class="option-item" 
          :class="{ active: isSelf === false }"
          @click="isSelf = false"
        >帮别人查</div>
      </div>
      <input 
        v-if="!isSelf" 
        type="text" 
        class="form-input mt-20" 
        v-model="remark" 
        placeholder="请输入备注名称"
      />
    </div>

    <button 
      class="btn-primary mt-20" 
      :disabled="loading"
      @click="submit"
    >
      {{ loading ? '处理中...' : '生成星盘' }}
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { request } from '@/utils/request'

const router = useRouter()
const route = useRoute()

const chartType = ref(route.query.type === 'bazi' ? 'bazi' : 'ziwei')
const isLunar = ref(false)
const birthDate = ref('')
const hourIndex = ref(0)
const gender = ref('male')
const isSelf = ref(true)
const remark = ref('')
const loading = ref(false)

const hours = ['早子时', '丑时', '寅时', '卯时', '辰时', '巳时', '午时', '未时', '申时', '酉时', '戌时', '亥时']

async function submit() {
  if (!birthDate.value) {
    alert('请选择出生日期')
    return
  }

  loading.value = true
  try {
    const data = {
      solar_date: isLunar.value ? '' : birthDate.value,
      lunar_date: isLunar.value ? birthDate.value : '',
      hour_index: hourIndex.value,
      gender: gender.value,
      is_default: isSelf.value,
      name: isSelf.value ? '我的星盘' : remark.value || '好友星盘',
      remark: isSelf.value ? '' : remark.value,
      chart_type: chartType.value,
      is_leap: false
    }

    if (chartType.value === 'bazi') {
      router.push({
        path: '/bazi-detail',
        query: {
          date_str: birthDate.value,
          hour_index: hourIndex.value,
          gender: gender.value
        }
      })
    } else {
      const res = await request.post('/users/save-chart', data)
      router.push(`/chart-detail/${res.id}`)
    }
  } catch (e) {
    console.error('提交失败', e)
    alert('提交失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.birth-input-page {
  padding: 32rpx;
}

.form-section {
  margin-bottom: 32rpx;
}

.section-label {
  font-size: 28rpx;
  color: #e0e0f0;
  margin-bottom: 16rpx;
  font-weight: 600;
}

.option-row {
  display: flex;
  gap: 12rpx;
}

.option-item {
  flex: 1;
  padding: 20rpx;
  text-align: center;
  background: rgba(10, 10, 26, 0.6);
  border: 1rpx solid rgba(201, 160, 80, 0.2);
  border-radius: 12rpx;
  color: #8888a0;
  font-size: 26rpx;
  cursor: pointer;
}

.option-item.active {
  border-color: #c9a050;
  color: #c9a050;
  background: rgba(201, 160, 80, 0.1);
}

.form-input {
  width: 100%;
  background: rgba(10, 10, 26, 0.6);
  border: 1rpx solid rgba(201, 160, 80, 0.2);
  border-radius: 12rpx;
  padding: 24rpx;
  color: #e0e0f0;
  font-size: 28rpx;
  outline: none;
}

.form-input:focus {
  border-color: #c9a050;
}

.hour-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12rpx;
}

.hour-item {
  padding: 16rpx;
  text-align: center;
  background: rgba(10, 10, 26, 0.6);
  border: 1rpx solid rgba(201, 160, 80, 0.2);
  border-radius: 12rpx;
  color: #8888a0;
  font-size: 24rpx;
  cursor: pointer;
}

.hour-item.active {
  border-color: #c9a050;
  color: #c9a050;
  background: rgba(201, 160, 80, 0.1);
}

.mt-20 { margin-top: 20rpx; }
</style>
