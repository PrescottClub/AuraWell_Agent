import { defineStore } from 'pinia'
import { ref } from 'vue'
import request from '../utils/request'

export const useHealthStore = defineStore('health', () => {
  const healthSummary = ref(null)
  const loading = ref(false)
  const error = ref(null)
  const periodInfo = ref({
    start: null,
    end: null
  })

  async function fetchHealthSummary(days = 7) {
    try {
      loading.value = true
      error.value = null
      const response = await request.get(`/health/summary?days=${days}`)
      
      if (response.success && response.status === 'success') {
        healthSummary.value = {
          activity: response.activity_summary,
          sleep: response.sleep_summary,
          heartRate: response.average_heart_rate,
          weightTrend: response.weight_trend,
          insights: response.key_insights
        }
        periodInfo.value = {
          start: response.period_start,
          end: response.period_end
        }
      } else {
        throw new Error(response.message || '获取健康数据失败')
      }
    } catch (err) {
      error.value = err.message || '获取健康数据失败'
      console.error('获取健康数据失败：', err)
    } finally {
      loading.value = false
    }
  }

  return {
    healthSummary,
    periodInfo,
    loading,
    error,
    fetchHealthSummary
  }
}) 