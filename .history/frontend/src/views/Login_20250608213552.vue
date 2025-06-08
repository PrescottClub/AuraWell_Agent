<template>
    <div class="login-container">
        <div class="login-form">
            <h2 class="login-title">登录</h2>
            <a-form :model="formState" name="login" @finish="onFinish" @finishFailed="onFinishFailed"
                autocomplete="off">
                <a-form-item name="username" :rules="[
                    { required: true, message: '请输入用户名!' },
                    { min: 3, message: '用户名至少3个字符!' }
                ]">
                    <a-input v-model:value="formState.username" placeholder="用户名">
                        <template #prefix>
                            <UserOutlined />
                        </template>
                    </a-input>
                </a-form-item>

                <a-form-item name="password" :rules="[
                    { required: true, message: '请输入密码!' },
                    { min: 6, message: '密码至少6个字符!' }
                ]">
                    <a-input-password v-model:value="formState.password" placeholder="密码">
                        <template #prefix>
                            <LockOutlined />
                        </template>
                    </a-input-password>
                </a-form-item>

                <a-form-item>
                    <a-checkbox v-model:checked="formState.remember">记住我</a-checkbox>
                    <a class="forgot-password" href="">忘记密码?</a>
                </a-form-item>

                <a-form-item>
                    <a-button type="primary" html-type="submit" class="login-button" :loading="loading">
                        登录
                    </a-button>
                </a-form-item>

                <div class="register-link">
                    <span>还没有账号? </span>
                    <a href="">立即注册</a>
                </div>
            </a-form>
        </div>
    </div>
</template>

<script setup>
import { reactive, ref } from 'vue';
import { UserOutlined, LockOutlined } from '@ant-design/icons-vue';
import { message } from 'ant-design-vue';
import { useRouter } from 'vue-router';
import axios from 'axios';

const router = useRouter();
const loading = ref(false);
const formState = reactive({
    username: '',
    password: '',
    remember: true,
});

const onFinish = async (values) => {
    try {
        loading.value = true;
        const response = await axios.post('/api/v1/auth/login', {
            username: values.username,
            password: values.password
        });

        if (response.data.status === 'success') {
            // 保存token到localStorage
            localStorage.setItem('access_token', response.data.access_token);
            localStorage.setItem('token_type', response.data.token_type);
            localStorage.setItem('expires_in', response.data.expires_in);
            localStorage.setItem('isLoggedIn', 'true');
            
            message.success('登录成功！');
            router.push('/admin');
        } else {
            message.error(response.data.message || '登录失败');
        }
    } catch (error) {
        message.error('登录失败：' + (error.response?.data?.message || error.message || '未知错误'));
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
    background-color: #f0f2f5;
}

.login-form {
    background: white;
    padding: 32px;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    width: 100%;
    max-width: 400px;
}

.login-title {
    font-size: 24px;
    font-weight: bold;
    text-align: center;
    margin-bottom: 24px;
}

.login-button {
    width: 100%;
}

.forgot-password {
    float: right;
}

.register-link {
    text-align: center;
    margin-top: 16px;
}

.ant-form-item {
    margin-bottom: 24px;
}
</style>