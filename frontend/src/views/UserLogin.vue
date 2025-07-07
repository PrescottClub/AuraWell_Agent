<template>
  <div class="flex items-center justify-center min-h-screen bg-background p-4">
    <div class="w-full max-w-md">
      <!-- 登录头部 -->
      <div class="text-center mb-8">
        <div class="inline-block p-3 bg-secondary rounded-xl mb-4">
          <svg class="w-8 h-8 text-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" />
          </svg>
        </div>
        <h1 class="text-2xl font-bold text-text-primary">欢迎回来</h1>
        <p class="text-text-secondary mt-1">登录您的 AuraWell 账户以继续</p>
      </div>

      <!-- 登录表单 -->
      <div class="bg-background-alt border border-border rounded-2xl p-8">
        <a-form
          :model="formState"
          name="login"
          @finish="onFinish"
          layout="vertical"
          class="space-y-6"
          autocomplete="off"
        >
          <a-form-item
            label="用户名"
            name="username"
            :rules="[{ required: true, message: '请输入用户名!' }]"
            class="!mb-0"
          >
            <a-input
              v-model:value="formState.username"
              placeholder="例如 test_user"
              size="large"
              class="themed-input"
            >
              <template #prefix>
                <UserOutlined class="input-icon" />
              </template>
            </a-input>
          </a-form-item>

          <a-form-item
            label="密码"
            name="password"
            :rules="[{ required: true, message: '请输入密码!' }]"
            class="!mb-0"
          >
            <a-input-password
              v-model:value="formState.password"
              placeholder="例如 test_password"
              size="large"
              class="themed-input"
            >
              <template #prefix>
                <LockOutlined class="input-icon" />
              </template>
            </a-input-password>
          </a-form-item>

          <div class="flex items-center justify-between">
            <a-checkbox v-model:checked="formState.remember" class="text-text-secondary">
              记住我
            </a-checkbox>
            <a class="text-sm font-medium text-primary hover:text-primary-hover" href="#" @click.prevent>忘记密码?</a>
          </div>

          <a-form-item class="!mb-0">
            <button
              type="submit"
              :disabled="loading"
              class="w-full text-white bg-primary hover:bg-primary-hover focus:ring-4 focus:ring-primary/30 font-semibold rounded-lg text-sm px-5 py-3 text-center transition-colors duration-200 disabled:opacity-50"
            >
              <span v-if="!loading">登录</span>
              <span v-else>登录中...</span>
            </button>
          </a-form-item>
        </a-form>
      </div>

      <!-- 注册链接 -->
      <div class="text-center mt-6">
          <p class="text-sm text-text-secondary">
            还没有账号？
            <router-link to="/register" class="font-semibold text-primary hover:text-primary-hover">
              立即注册
            </router-link>
          </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue';
import { UserOutlined, LockOutlined } from '@ant-design/icons-vue';
import { message } from 'ant-design-vue';
import { useRouter, useRoute } from 'vue-router';
import { UserAPI } from '../api/user';

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

        // 使用Mock API进行登录
        const response = await UserAPI.login({
            username: values.username,
            password: values.password
        });

        // 检查响应格式并保存token和用户信息
        if (response.success && response.data) {
            authStore.setToken(
                response.data.access_token,
                response.data.token_type,
                response.data.expires_in
            );
            localStorage.setItem('isLoggedIn', 'true');

            // 设置用户信息
            if (response.data.user) {
                userStore.setUser(response.data.user);
            }

            message.success('登录成功！');

            // 重定向到原来要访问的页面，或者默认到首页
            const redirectPath = route.query.redirect || '/';
            router.push(redirectPath);
        } else {
            throw new Error(response.message || '登录失败');
        }
    } catch (error) {
        console.error('登录失败：', error);
        message.error(error.message || '登录失败，请检查用户名和密码');
    } finally {
        loading.value = false;
    }
};

const onFinishFailed = (errorInfo) => {
    console.log('Failed:', errorInfo);
    message.error('请检查输入信息！');
};
</script>

<style>
/* 将Antd组件与Tailwind主题融合 */
.themed-input .ant-input,
.themed-input .ant-input-password {
  background-color: transparent !important;
  border-color: #dadce0 !important; /* theme.border.DEFAULT */
  color: #202124 !important; /* theme.text.primary */
}

.themed-input .ant-input:focus,
.themed-input .ant-input-password:focus,
.themed-input .ant-input-affix-wrapper:focus-within {
  border-color: #1a73e8 !important; /* theme.primary.DEFAULT */
  box-shadow: 0 0 0 2px rgba(26, 115, 232, 0.2) !important;
}

.themed-input .ant-input::placeholder {
  color: #80868b; /* theme.text.disabled */
}

.themed-input .input-icon {
  color: #5f6368; /* theme.text.secondary */
}

/* Form Label styling */
.ant-form-item-label > label {
  color: #202124 !important; /* theme.text.primary */
  font-weight: 500 !important;
}

/* Checkbox styling */
.ant-checkbox-wrapper {
  color: #5f6368; /* theme.text.secondary */
}
.ant-checkbox-checked .ant-checkbox-inner {
  background-color: #1a73e8 !important; /* theme.primary.DEFAULT */
  border-color: #1a73e8 !important;
}
</style>