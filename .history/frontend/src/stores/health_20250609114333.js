import { defineStore } from 'pinia'
import { ref } from 'vue'
import request from '../utils/request'

export const useHealthStore = defineStore('health', () => {
  const healthSummary = ref(null)
  const loading = ref(false)
  const error = ref(null)

  async function fetchHealthSummary(days = 7) {
    try {
      loading.value = true
      error.value = null
      const response = await request.get(`/health/summary?days=${days}`)
      console.log(response);
      healthSummary.value = response.data
      console.log(healthSummary.value);
    } catch (err) {
      error.value = err.message || '获取健康数据失败'
      console.error('获取健康数据失败：', err)
    } finally {
      loading.value = false
    }
  }

  return {
    healthSummary,
    loading,
    error,
    fetchHealthSummary
  }
}) 