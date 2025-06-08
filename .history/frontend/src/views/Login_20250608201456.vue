<template>
    <div class="login-container">
        <a-card class="login-card" title="AuraWell 管理系统">
            <a-form :model="formState" name="login" @finish="handleFinish" autocomplete="off">
                <a-form-item name="username" :rules="[{ required: true, message: '请输入用户名' }]">
                    <a-input v-model:value="formState.username" placeholder="用户名">
                        <template #prefix>
                            <UserOutlined />
                        </template>
                    </a-input>
                </a-form-item>

                <a-form-item name="password" :rules="[{ required: true, message: '请输入密码' }]">
                    <a-input-password v-model:value="formState.password" placeholder="密码">
                        <template #prefix>
                            <LockOutlined />
                        </template>
                    </a-input-password>
                </a-form-item>

                <a-form-item>
                    <a-button type="primary" html-type="submit" :loading="loading" block>
                        登录
                    </a-button>
                </a-form-item>
            </a-form>
        </a-card>
    </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { message } from 'ant-design-vue'
import { UserOutlined, LockOutlined } from '@ant-design/icons-vue'
import { login } from '../api/user'
import { setToken, setUserInfo } from '../utils/auth'

const router = useRouter()
const route = useRoute()
const loading = ref(false)

const formState = reactive({
    username: '',
    password: ''
})

const handleFinish = async (values) => {
    try {
        loading.value = true
        const res = await login(values)

        // 保存 token 和用户信息
        setToken(res.token)
        setUserInfo(res.userInfo)

        message.success('登录成功')

        // 跳转到之前的页面或默认页面
        const redirect = route.query.redirect || '/admin'
        router.push(redirect)
    } catch (error) {
        console.error('登录失败:', error)
    } finally {
        loading.value = false
    }
}
</script>

<style scoped>
.login-container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    background-color: #f0f2f5;
}

.login-card {
    width: 100%;
    max-width: 400px;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.login-card :deep(.ant-card-head-title) {
    text-align: center;
    font-size: 24px;
    font-weight: 500;
}
</style>