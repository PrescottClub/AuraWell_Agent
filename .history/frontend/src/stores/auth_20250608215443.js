import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('access_token') || '')
  const tokenType = ref(localStorage.getItem('token_type') || '')
  const expiresIn = ref(localStorage.getItem('expires_in') || '')

  function setToken(newToken, newTokenType, newExpiresIn) {
    token.value = newToken
    tokenType.value = newTokenType
    expiresIn.value = newExpiresIn
    
    // 保存到localStorage
    localStorage.setItem('access_token', newToken)
    localStorage.setItem('token_type', newTokenType)
    localStorage.setItem('expires_in', newExpiresIn)
  }

  function clearToken() {
    token.value = ''
    tokenType.value = ''
    expiresIn.value = ''
    
    // 清除localStorage
    localStorage.removeItem('access_token')
    localStorage.removeItem('token_type')
    localStorage.removeItem('expires_in')
    localStorage.removeItem('isLoggedIn')
  }

  function getAuthHeader() {
    return token.value ? `${tokenType.value} ${token.value}` : ''
  }

  return {
    token,
    tokenType,
    expiresIn,
    setToken,
    clearToken,
    getAuthHeader
  }
}) 