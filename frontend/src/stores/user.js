import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { UserAPI } from '../api/user.js'

export const useUserStore = defineStore('user', () => {
  // 状态
  const userProfile = ref({
    id: '',
    username: '',
    email: '',
    avatar: '',
    created_at: '',
    updated_at: ''
  })

  const healthData = ref({
    age: null,
    gender: '',
    height: null, // cm
    weight: null, // kg
    activity_level: '', // sedentary, light, moderate, active, very_active
    medical_conditions: [],
    allergies: [],
    medications: [],
    sleep_hours: null,
    stress_level: '', // low, medium, high
    smoking: false,
    drinking: '', // none, occasional, moderate, heavy
    updated_at: ''
  })

  const healthGoals = ref([])
  const loading = ref(false)
  const error = ref('')

  // 计算属性
  const isProfileComplete = computed(() => {
    return userProfile.value.username && 
           healthData.value.age && 
           healthData.value.height && 
           healthData.value.weight
  })

  const bmi = computed(() => {
    if (healthData.value.height && healthData.value.weight) {
      const heightInM = healthData.value.height / 100
      return (healthData.value.weight / (heightInM * heightInM)).toFixed(1)
    }
    return null
  })

  const bmiCategory = computed(() => {
    if (!bmi.value) return ''
    const bmiValue = parseFloat(bmi.value)
    if (bmiValue < 18.5) return '偏瘦'
    if (bmiValue < 24) return '正常'
    if (bmiValue < 28) return '超重'
    return '肥胖'
  })

  // 方法
  const fetchUserProfile = async () => {
    loading.value = true
    error.value = ''
    try {
      const response = await UserAPI.getProfile()
      if (response.data) {
        userProfile.value = response.data
      }
    } catch (err) {
      error.value = '获取用户档案失败'
      console.error('获取用户档案失败:', err)
    } finally {
      loading.value = false
    }
  }

  const updateUserProfile = async (profileData) => {
    loading.value = true
    error.value = ''
    try {
      const response = await UserAPI.updateProfile(profileData)
      if (response.data) {
        userProfile.value = { ...userProfile.value, ...response.data }
      }
      return response
    } catch (err) {
      error.value = '更新用户档案失败'
      console.error('更新用户档案失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchHealthData = async () => {
    loading.value = true
    error.value = ''
    try {
      const response = await UserAPI.getHealthData()
      if (response.data) {
        healthData.value = { ...healthData.value, ...response.data }
      }
    } catch (err) {
      error.value = '获取健康数据失败'
      console.error('获取健康数据失败:', err)
    } finally {
      loading.value = false
    }
  }

  const updateHealthData = async (newHealthData) => {
    loading.value = true
    error.value = ''
    try {
      const response = await UserAPI.updateHealthData(newHealthData)
      if (response.data) {
        healthData.value = { ...healthData.value, ...response.data }
      }
      return response
    } catch (err) {
      error.value = '更新健康数据失败'
      console.error('更新健康数据失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchHealthGoals = async () => {
    loading.value = true
    error.value = ''
    try {
      const response = await UserAPI.getHealthGoals()
      if (response.data) {
        healthGoals.value = response.data
      }
    } catch (err) {
      error.value = '获取健康目标失败'
      console.error('获取健康目标失败:', err)
    } finally {
      loading.value = false
    }
  }

  const createHealthGoal = async (goalData) => {
    loading.value = true
    error.value = ''
    try {
      const response = await UserAPI.createHealthGoal(goalData)
      if (response.data) {
        healthGoals.value.push(response.data)
      }
      return response
    } catch (err) {
      error.value = '创建健康目标失败'
      console.error('创建健康目标失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateHealthGoal = async (goalId, goalData) => {
    loading.value = true
    error.value = ''
    try {
      const response = await UserAPI.updateHealthGoal(goalId, goalData)
      if (response.data) {
        const index = healthGoals.value.findIndex(goal => goal.id === goalId)
        if (index !== -1) {
          healthGoals.value[index] = response.data
        }
      }
      return response
    } catch (err) {
      error.value = '更新健康目标失败'
      console.error('更新健康目标失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteHealthGoal = async (goalId) => {
    loading.value = true
    error.value = ''
    try {
      await UserAPI.deleteHealthGoal(goalId)
      healthGoals.value = healthGoals.value.filter(goal => goal.id !== goalId)
    } catch (err) {
      error.value = '删除健康目标失败'
      console.error('删除健康目标失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const setUser = (userData) => {
    if (userData) {
      userProfile.value = { ...userProfile.value, ...userData }
    }
  }

  const clearUserData = () => {
    userProfile.value = {
      id: '',
      username: '',
      email: '',
      avatar: '',
      created_at: '',
      updated_at: ''
    }
    healthData.value = {
      age: null,
      gender: '',
      height: null,
      weight: null,
      activity_level: '',
      medical_conditions: [],
      allergies: [],
      medications: [],
      sleep_hours: null,
      stress_level: '',
      smoking: false,
      drinking: '',
      updated_at: ''
    }
    healthGoals.value = []
    error.value = ''
  }

  return {
    // 状态
    userProfile,
    healthData,
    healthGoals,
    loading,
    error,
    
    // 计算属性
    isProfileComplete,
    bmi,
    bmiCategory,
    
    // 方法
    setUser,
    fetchUserProfile,
    updateUserProfile,
    fetchHealthData,
    updateHealthData,
    fetchHealthGoals,
    createHealthGoal,
    updateHealthGoal,
    deleteHealthGoal,
    clearUserData
  }
})
