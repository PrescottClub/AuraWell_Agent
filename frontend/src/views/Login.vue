<template>
  <div class="login-container">
    <!-- 背景装饰 -->
    <div class="background-decoration">
      <div class="decoration-circle circle-1"></div>
      <div class="decoration-circle circle-2"></div>
      <div class="decoration-circle circle-3"></div>
    </div>

    <div class="login-card">
      <!-- 登录头部 -->
      <div class="login-header">
        <div class="logo-section">
          <div class="logo-icon">🌟</div>
          <h1>欢迎回来</h1>
          <p>登录您的 AuraWell 账户</p>
        </div>
      </div>

      <!-- 登录表单 -->
      <a-form
        :model="formState"
        name="login"
        @finish="onFinish"
        @finishFailed="onFinishFailed"
        layout="vertical"
        class="login-form"
        autocomplete="off"
      >
        <a-form-item
          label="用户名"
          name="username"
          :rules="[
            { required: true, message: '请输入用户名!' },
            { min: 3, message: '用户名至少3个字符!' }
          ]"
        >
          <a-input
            v-model:value="formState.username"
            placeholder="请输入用户名"
            size="large"
            class="custom-input"
          >
            <template #prefix>
              <UserOutlined class="input-icon" />
            </template>
          </a-input>
        </a-form-item>

        <a-form-item
          label="密码"
          name="password"
          :rules="[
            { required: true, message: '请输入密码!' },
            { min: 6, message: '密码至少6个字符!' }
          ]"
        >
          <a-input-password
            v-model:value="formState.password"
            placeholder="请输入密码"
            size="large"
            class="custom-input"
          >
            <template #prefix>
              <LockOutlined class="input-icon" />
            </template>
          </a-input-password>
        </a-form-item>

        <div class="form-options">
          <a-checkbox v-model:checked="formState.remember" class="remember-checkbox">
            记住我
          </a-checkbox>
          <a class="forgot-password" href="#" @click.prevent>忘记密码?</a>
        </div>

        <a-form-item>
          <a-button
            type="primary"
            html-type="submit"
            class="login-button"
            :loading="loading"
            size="large"
            block
          >
            <span v-if="!loading">登录账户</span>
            <span v-else>登录中...</span>
          </a-button>
        </a-form-item>

        <div class="divider">
          <span>或</span>
        </div>

        <div class="register-section">
          <p class="register-text">还没有账号？</p>
          <router-link to="/register" class="register-link">
            立即注册
          </router-link>
        </div>
      </a-form>

      <!-- 快速登录提示 -->
      <div class="demo-hint">
        <a-alert
          message="演示账户"
          description="用户名: test_user, 密码: test_password"
          type="info"
          show-icon
          closable
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue';
import { UserOutlined, LockOutlined } from '@ant-design/icons-vue';
import { message } from 'ant-design-vue';
import { useRouter, useRoute } from 'vue-router';
import request from '../utils/request';
import { useAuthStore } from '../stores/auth';
import { useUserStore } from '../stores/user';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();
const userStore = useUserStore();
const loading = ref(false);
const formState = reactive({
    username: 'test_user',
    password: 'test_password',
    remember: true,
});

const onFinish = async (values) => {
    try {
        loading.value = true;
        const response = await request.post('/auth/login', {
            username: values.username,
            password: values.password
        });

        // 使用store保存token
        authStore.setToken(
            response.data.access_token,
            response.data.token_type,
            response.data.expires_in
        );
        localStorage.setItem('isLoggedIn', 'true');

        // 获取用户信息
        await userStore.fetchUserProfile();

        message.success('登录成功！');

        // 重定向到原来要访问的页面，或者默认到首页
        const redirectPath = route.query.redirect || '/';
        router.push(redirectPath);
    } catch (error) {
        console.error('登录失败：', error);
        message.error('登录失败，请检查用户名和密码');
    } finally {
        loading.value = false;
    }
};

const onFinishFailed = (errorInfo) => {
    console.log('Failed:', errorInfo);
    message.error('请检查输入信息！');
};
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  position: relative;
  overflow: hidden;
}

/* 背景装饰 */
.background-decoration {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

.decoration-circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  animation: float 6s ease-in-out infinite;
}

.circle-1 {
  width: 200px;
  height: 200px;
  top: 10%;
  left: 10%;
  animation-delay: 0s;
}

.circle-2 {
  width: 150px;
  height: 150px;
  top: 60%;
  right: 10%;
  animation-delay: 2s;
}

.circle-3 {
  width: 100px;
  height: 100px;
  bottom: 20%;
  left: 20%;
  animation-delay: 4s;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
    opacity: 0.7;
  }
  50% {
    transform: translateY(-20px) rotate(180deg);
    opacity: 1;
  }
}

/* 登录卡片 */
.login-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  padding: 40px;
  width: 100%;
  max-width: 450px;
  position: relative;
  z-index: 1;
  backdrop-filter: blur(10px);
}

/* 登录头部 */
.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo-section {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.logo-icon {
  font-size: 3rem;
  margin-bottom: 16px;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
}

.login-header h1 {
  font-size: 28px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 8px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.login-header p {
  color: #6b7280;
  font-size: 16px;
  margin: 0;
}

/* 表单样式 */
.login-form {
  margin-top: 24px;
}

.custom-input {
  border-radius: 8px;
  transition: all 0.3s ease;
}

.custom-input:hover {
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
}

.custom-input:focus-within {
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
}

.input-icon {
  color: #9ca3af;
  transition: color 0.3s ease;
}

.custom-input:focus-within .input-icon {
  color: #667eea;
}

/* 表单选项 */
.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.remember-checkbox {
  color: #374151;
}

.forgot-password {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.3s ease;
}

.forgot-password:hover {
  color: #5a67d8;
}

/* 登录按钮 */
.login-button {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 16px;
  height: 48px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.login-button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s ease;
}

.login-button:hover::before {
  left: 100%;
}

.login-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
}

/* 分割线 */
.divider {
  text-align: center;
  margin: 24px 0;
  position: relative;
}

.divider::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background: #e5e7eb;
}

.divider span {
  background: white;
  color: #9ca3af;
  padding: 0 16px;
  font-size: 14px;
  position: relative;
  z-index: 1;
}

/* 注册部分 */
.register-section {
  text-align: center;
  margin-top: 16px;
}

.register-text {
  color: #6b7280;
  margin-bottom: 8px;
  font-size: 14px;
}

.register-link {
  color: #667eea;
  text-decoration: none;
  font-weight: 600;
  font-size: 16px;
  padding: 8px 16px;
  border-radius: 6px;
  transition: all 0.3s ease;
  display: inline-block;
}

.register-link:hover {
  color: #5a67d8;
  background: rgba(102, 126, 234, 0.1);
}

/* 演示提示 */
.demo-hint {
  margin-top: 24px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .login-container {
    padding: 16px;
  }

  .login-card {
    padding: 24px;
    max-width: 100%;
  }

  .login-header h1 {
    font-size: 24px;
  }

  .login-header p {
    font-size: 14px;
  }

  .decoration-circle {
    display: none;
  }
}

/* 表单项间距 */
.ant-form-item {
  margin-bottom: 20px;
}

.ant-form-item-label > label {
  font-weight: 500;
  color: #374151;
}

/* 加载状态优化 */
.login-button.ant-btn-loading {
  pointer-events: none;
}

.login-button.ant-btn-loading::before {
  display: none;
}
</style>