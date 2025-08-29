<template>
  <div class="register-container">
    <div class="register-card">
      <div class="register-header">
        <div class="logo-section">
          <div class="logo-icon">🌟</div>
          <h1>加入 AuraWell</h1>
          <p>开始您的健康管理之旅</p>
        </div>
      </div>

      <a-form
        :model="formData"
        :rules="rules"
        @finish="handleRegister"
        layout="vertical"
        class="register-form"
      >
        <!-- 基本信息 -->
        <div class="form-section">
          <h3>基本信息</h3>

          <a-form-item label="用户名" name="username">
            <a-input
              v-model="formData.username"
              placeholder="请输入用户名"
              size="large"
            />
          </a-form-item>

          <a-form-item label="邮箱" name="email">
            <a-input
              v-model="formData.email"
              placeholder="请输入邮箱地址"
              size="large"
            />
          </a-form-item>

          <a-form-item label="密码" name="password">
            <a-input-password
              v-model="formData.password"
              placeholder="请输入密码"
              size="large"
            />
          </a-form-item>

          <a-form-item label="确认密码" name="confirmPassword">
            <a-input-password
              v-model="formData.confirmPassword"
              placeholder="请再次输入密码"
              size="large"
            />
          </a-form-item>
        </div>

        <!-- 健康信息 -->
        <div class="form-section">
          <h3>健康信息</h3>

          <a-row :gutter="16">
            <a-col :span="12">
              <a-form-item label="年龄" name="age">
                <a-input-number
                  v-model="formData.age"
                  placeholder="请输入年龄"
                  :min="1"
                  :max="120"
                  size="large"
                  style="width: 100%"
                />
              </a-form-item>
            </a-col>
            <a-col :span="12">
              <a-form-item label="性别" name="gender">
                <a-select
                  v-model="formData.gender"
                  placeholder="请选择性别"
                  size="large"
                >
                  <a-select-option value="male">男</a-select-option>
                  <a-select-option value="female">女</a-select-option>
                </a-select>
              </a-form-item>
            </a-col>
          </a-row>

          <a-row :gutter="16">
            <a-col :span="12">
              <a-form-item label="身高 (cm)" name="height">
                <a-input-number
                  v-model="formData.height"
                  placeholder="请输入身高"
                  :min="100"
                  :max="250"
                  size="large"
                  style="width: 100%"
                />
              </a-form-item>
            </a-col>
            <a-col :span="12">
              <a-form-item label="体重 (kg)" name="weight">
                <a-input-number
                  v-model="formData.weight"
                  placeholder="请输入体重"
                  :min="30"
                  :max="300"
                  :precision="1"
                  size="large"
                  style="width: 100%"
                />
              </a-form-item>
            </a-col>
          </a-row>

          <a-form-item label="活动水平" name="activity_level">
            <a-select
              v-model="formData.activity_level"
              placeholder="请选择您的日常活动水平"
              size="large"
            >
              <a-select-option value="sedentary">久坐不动</a-select-option>
              <a-select-option value="light">轻度活动</a-select-option>
              <a-select-option value="moderate">中度活动</a-select-option>
              <a-select-option value="active">积极活动</a-select-option>
              <a-select-option value="very_active">非常活跃</a-select-option>
            </a-select>
          </a-form-item>
        </div>

        <!-- 提交按钮 -->
        <a-form-item>
          <a-button
            type="primary"
            html-type="submit"
            size="large"
            :loading="loading"
            block
          >
            注册账户
          </a-button>
        </a-form-item>

        <div class="login-link">
          已有账户？
          <router-link to="/login">立即登录</router-link>
        </div>
      </a-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { message } from 'ant-design-vue';
import { UserAPI } from '../api/user.js';

const router = useRouter();
const loading = ref(false);

const formData = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  age: null,
  gender: '',
  height: null,
  weight: null,
  activity_level: '',
});

const rules = {
  username: [
    { required: true, message: '请输入用户名' },
    { min: 3, max: 20, message: '用户名长度应在3-20个字符之间' },
  ],
  email: [
    { required: true, message: '请输入邮箱地址' },
    { type: 'email', message: '请输入有效的邮箱地址' },
  ],
  password: [
    { required: true, message: '请输入密码' },
    { min: 6, message: '密码长度至少6个字符' },
  ],
  confirmPassword: [
    { required: true, message: '请确认密码' },
    {
      validator: (rule, value) => {
        if (value !== formData.password) {
          return Promise.reject('两次输入的密码不一致');
        }
        return Promise.resolve();
      },
    },
  ],
  age: [{ required: true, message: '请输入年龄' }],
  gender: [{ required: true, message: '请选择性别' }],
  height: [{ required: true, message: '请输入身高' }],
  weight: [{ required: true, message: '请输入体重' }],
  activity_level: [{ required: true, message: '请选择活动水平' }],
};

const handleRegister = async () => {
  loading.value = true;
  try {
    const registerData = {
      username: formData.username,
      email: formData.email,
      password: formData.password,
      health_data: {
        age: formData.age,
        gender: formData.gender,
        height: formData.height,
        weight: formData.weight,
        activity_level: formData.activity_level,
      },
    };

    await UserAPI.register(registerData);
    message.success('注册成功！请登录您的账户');
    router.push('/login');
  } catch (error) {
    message.error(error.response?.data?.detail || '注册失败，请重试');
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-background);
  padding: 20px;
}

.register-card {
  background: var(--color-background-elevated);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.06);
  border: 1px solid var(--color-border-light);
  padding: 40px;
  width: 100%;
  max-width: 600px;
}

.register-header {
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
  background: var(--color-health);
  background: linear-gradient(
    135deg,
    var(--color-health) 0%,
    var(--color-primary) 100%
  );
  border-radius: 50%;
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%,
  100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}

.register-header h1 {
  font-size: 28px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 8px;
  background: linear-gradient(
    135deg,
    var(--color-health) 0%,
    var(--color-primary) 100%
  );
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.register-header p {
  color: var(--color-text-secondary);
  font-size: 16px;
}

.form-section {
  margin-bottom: 24px;
}

.form-section h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 2px solid var(--color-border-light);
  position: relative;
}

.form-section h3::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 40px;
  height: 2px;
  background: linear-gradient(
    135deg,
    var(--color-health) 0%,
    var(--color-primary) 100%
  );
}

.login-link {
  text-align: center;
  margin-top: 16px;
  color: var(--color-text-secondary);
}

.login-link a {
  color: var(--color-health);
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s ease;
}

.login-link a:hover {
  color: var(--color-primary);
}

/* Ant Design 组件主题覆盖 */
:deep(.ant-btn-primary) {
  background: linear-gradient(
    135deg,
    var(--color-health) 0%,
    var(--color-primary) 100%
  );
  border: none;
  border-radius: 8px;
  font-weight: 500;
  height: 40px;
  transition: all 0.3s ease;
}

:deep(.ant-btn-primary:hover) {
  background: linear-gradient(
    135deg,
    var(--color-primary) 0%,
    var(--color-health) 100%
  );
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(45, 125, 50, 0.2);
}

:deep(.ant-input) {
  border-radius: 8px;
  border: 1px solid var(--color-border-light);
  background: var(--color-background);
  transition: all 0.2s ease;
}

:deep(.ant-input:hover) {
  border-color: var(--color-health);
}

:deep(.ant-input:focus) {
  border-color: var(--color-health);
  box-shadow: 0 0 0 2px rgba(45, 125, 50, 0.1);
}

:deep(.ant-select) {
  border-radius: 8px;
}

:deep(.ant-select .ant-select-selector) {
  border: 1px solid var(--color-border-light);
  border-radius: 8px;
  background: var(--color-background);
  transition: all 0.2s ease;
}

:deep(.ant-select:hover .ant-select-selector) {
  border-color: var(--color-health);
}

:deep(.ant-select.ant-select-focused .ant-select-selector) {
  border-color: var(--color-health);
  box-shadow: 0 0 0 2px rgba(45, 125, 50, 0.1);
}
</style>
