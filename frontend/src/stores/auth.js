import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { UserAPI } from '../api/user';

export const useAuthStore = defineStore('auth', () => {
  // 🔧 统一认证状态管理
  const token = ref(localStorage.getItem('access_token') || '');
  const tokenType = ref(localStorage.getItem('token_type') || 'Bearer');
  const expiresIn = ref(localStorage.getItem('expires_in') || '');
  const expiresAt = ref(localStorage.getItem('expires_at') || '');
  const isValidating = ref(false);
  const lastValidation = ref(0);

  // 🔧 计算属性：认证状态
  const isAuthenticated = computed(() => {
    return !!token.value && !isTokenExpired.value;
  });

  const isTokenExpired = computed(() => {
    if (!expiresAt.value) return false;
    return Date.now() > parseInt(expiresAt.value);
  });

  const timeUntilExpiry = computed(() => {
    if (!expiresAt.value) return 0;
    return Math.max(0, parseInt(expiresAt.value) - Date.now());
  });

  // 🔧 统一Token设置方法
  function setToken(newToken, newTokenType = 'Bearer', newExpiresIn = 3600) {
    token.value = newToken;
    tokenType.value = newTokenType;
    expiresIn.value = newExpiresIn;

    // 计算过期时间戳
    const expiresAtTimestamp = Date.now() + newExpiresIn * 1000;
    expiresAt.value = expiresAtTimestamp.toString();

    // 保存到localStorage
    localStorage.setItem('access_token', newToken);
    localStorage.setItem('token_type', newTokenType);
    localStorage.setItem('expires_in', newExpiresIn.toString());
    localStorage.setItem('expires_at', expiresAtTimestamp.toString());
    localStorage.setItem('isLoggedIn', 'true');

    console.log(
      '✅ Token已设置，过期时间:',
      new Date(expiresAtTimestamp).toLocaleString()
    );
  }

  // 🔧 统一Token清除方法
  function clearToken() {
    token.value = '';
    tokenType.value = 'Bearer';
    expiresIn.value = '';
    expiresAt.value = '';

    // 清除localStorage
    localStorage.removeItem('access_token');
    localStorage.removeItem('token_type');
    localStorage.removeItem('expires_in');
    localStorage.removeItem('expires_at');
    localStorage.removeItem('isLoggedIn');

    console.log('🔄 认证信息已清除');
  }

  // 🔧 统一认证头获取方法
  function getAuthHeader() {
    if (!token.value) return '';
    return `${tokenType.value} ${token.value}`;
  }

  // 🔧 核心功能：Token验证 - 优化防重复验证
  async function validateToken() {
    // 防止重复验证（10秒内只验证一次，增加时间窗口）
    const now = Date.now();
    if (isValidating.value || now - lastValidation.value < 10000) {
      console.log('🔄 Token验证中或刚验证过，跳过本次验证');
      return isAuthenticated.value;
    }

    if (!token.value) {
      console.log('🔍 无Token，需要登录');
      return false;
    }

    if (isTokenExpired.value) {
      console.log('⏰ Token已过期，清除认证信息');
      clearToken();
      return false;
    }

    try {
      isValidating.value = true;
      lastValidation.value = now;

      console.log('🔍 验证Token有效性...');

      // 🔧 优化：增加验证超时控制
      const timeoutPromise = new Promise((_, reject) =>
        setTimeout(() => reject(new Error('Token验证超时')), 5000)
      );

      const validationPromise = UserAPI.validateCurrentToken();
      const isValid = await Promise.race([validationPromise, timeoutPromise]);

      if (!isValid) {
        console.warn('⚠️ Token验证失败，清除认证信息');
        clearToken();
        return false;
      }

      console.log('✅ Token验证成功');
      return true;
    } catch (error) {
      console.error('❌ Token验证异常:', error.message);
      // 🔧 优化：网络错误时不清除Token，超时或认证错误才清除
      if (
        error.message.includes('Token验证超时') ||
        error.message.includes('401')
      ) {
        clearToken();
      }
      return false;
    } finally {
      isValidating.value = false;
    }
  }

  // 🔧 自动登录功能（开发环境）
  async function performAutoLogin() {
    try {
      console.log('🔄 执行自动登录...');

      const response = await UserAPI.login({
        username: 'test_user',
        password: 'test_password',
      });

      if (response.success && response.data) {
        setToken(
          response.data.access_token,
          response.data.token_type || 'Bearer',
          response.data.expires_in || 3600
        );

        console.log('✅ 自动登录成功');
        return true;
      } else {
        throw new Error(response.message || '登录失败');
      }
    } catch (error) {
      console.error('❌ 自动登录失败:', error);
      return false;
    }
  }

  // 🔧 确保认证状态（核心方法）- 优化初始化逻辑
  async function ensureAuthenticated() {
    // 如果已经认证且Token未过期，直接返回（避免重复检查）
    if (isAuthenticated.value && Date.now() - lastValidation.value < 30000) {
      console.log('✅ 认证状态有效，跳过验证');
      return true;
    }

    // 防止并发调用导致循环 - 增强版本
    if (isValidating.value) {
      console.log('🔄 认证验证中，等待结果...');
      // 等待当前验证完成，最多等待10秒
      let waitCount = 0;
      while (isValidating.value && waitCount < 100) {
        await new Promise(resolve => setTimeout(resolve, 100));
        waitCount++;
      }

      // 如果等待超时，强制重置验证状态
      if (waitCount >= 100) {
        console.warn('⚠️ 认证验证超时，强制重置状态');
        isValidating.value = false;
      }

      return isAuthenticated.value;
    }

    // 尝试验证现有Token
    if (await validateToken()) {
      return true;
    }

    // 🔧 只在开发环境且明确需要时才自动登录
    if (
      (import.meta.env.DEV || import.meta.env.VITE_APP_ENV === 'development') &&
      !window.location.pathname.includes('/login') &&
      !window.location.pathname.includes('/register')
    ) {
      console.log('🔄 开发环境尝试自动登录...');
      const autoLoginSuccess = await performAutoLogin();
      if (autoLoginSuccess) {
        return true;
      }
    }

    // 生产环境或自动登录失败需要手动登录
    console.log('🔐 需要手动登录');
    return false;
  }

  // 🔧 Token自动刷新（预留接口）
  async function refreshToken() {
    // TODO: 实现Token刷新逻辑
    console.log('🔄 Token刷新功能待实现');
    return false;
  }

  // 🔧 登出方法
  async function logout() {
    try {
      // 调用后端登出API
      await UserAPI.logout();
    } catch (error) {
      console.warn('登出API调用失败:', error);
    } finally {
      // 无论API调用是否成功，都清除本地认证信息
      clearToken();
    }
  }

  return {
    // 状态
    token,
    tokenType,
    expiresIn,
    expiresAt,
    isValidating,

    // 计算属性
    isAuthenticated,
    isTokenExpired,
    timeUntilExpiry,

    // 方法
    setToken,
    clearToken,
    getAuthHeader,
    validateToken,
    performAutoLogin,
    ensureAuthenticated,
    refreshToken,
    logout,
  };
});
