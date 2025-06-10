import { defineStore } from 'pinia'
import { ref } from 'vue'
import { login, getUserInfo, logout } from '../api/user'
import { setToken, getToken, removeToken, setUserInfo, removeUserInfo } from '../utils/auth'

export const useUserStore = defineStore('user', () => {
  const token = ref(getToken())
  const userInfo = ref(null)

  // 登录
  async function loginAction(loginData) {
    try {
      const res = await login(loginData)
      token.value = res.token
      userInfo.value = res.userInfo
      setToken(res.token)
      setUserInfo(res.userInfo)
      return res
    } catch (error) {
      throw error
    }
  }

  // 获取用户信息
  async function getUserInfoAction() {
    try {
      const res = await getUserInfo()
      userInfo.value = res
      setUserInfo(res)
      return res
    } catch (error) {
      throw error
    }
  }

  // 登出
  async function logoutAction() {
    try {
      await logout()
    } finally {
      token.value = null
      userInfo.value = null
      removeToken()
      removeUserInfo()
    }
  }

  return {
    token,
    userInfo,
    loginAction,
    getUserInfoAction,
    logoutAction
  }
}) 