const TOKEN_KEY = 'aurawell_token'
const USER_INFO_KEY = 'aurawell_user_info'

// Token 相关操作
export const getToken = () => {
  return localStorage.getItem(TOKEN_KEY)
}

export const setToken = (token) => {
  localStorage.setItem(TOKEN_KEY, token)
}

export const removeToken = () => {
  localStorage.removeItem(TOKEN_KEY)
}

export const hasToken = () => {
  return !!getToken()
}

// 用户信息相关操作
export const getUserInfo = () => {
  const userInfo = localStorage.getItem(USER_INFO_KEY)
  return userInfo ? JSON.parse(userInfo) : null
}

export const setUserInfo = (userInfo) => {
  localStorage.setItem(USER_INFO_KEY, JSON.stringify(userInfo))
}

export const removeUserInfo = () => {
  localStorage.removeItem(USER_INFO_KEY)
}

// 清除所有认证信息
export const clearAuth = () => {
  removeToken()
  removeUserInfo()
} 