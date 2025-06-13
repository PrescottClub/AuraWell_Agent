import axios from 'axios';
import { message } from 'ant-design-vue';
import { useAuthStore } from '../stores/auth';

const request = axios.create({
    baseURL: import.meta.env.VITE_APP_API_BASE_URL || '/api/v1',
    timeout: import.meta.env.VITE_API_TIMEOUT || 15000
});

// 请求拦截器
request.interceptors.request.use(
    config => {
        // 登录和注册请求不需要认证头
        const isAuthRequest = config.url?.includes('/auth/login') || config.url?.includes('/auth/register');

        if (!isAuthRequest) {
            const authStore = useAuthStore();
            const authHeader = authStore.getAuthHeader();
            if (authHeader) {
                config.headers['Authorization'] = authHeader;
            } else if (import.meta.env.VITE_APP_ENV === 'development' || import.meta.env.DEV) {
                // 开发环境：如果没有token，尝试从localStorage获取或使用测试token
                const devToken = localStorage.getItem('dev_auth_token') || 'Bearer dev-test-token';
                config.headers['Authorization'] = devToken;
                console.warn('使用开发环境测试token，生产环境请确保正确的认证流程');
            }
        }
        return config;
    },
    error => {
        console.error('请求错误：', error);
        return Promise.reject(error);
    }
);

// 响应拦截器
request.interceptors.response.use(
    response => {
        const res = response.data;
        
        if (res.status === 'success') {
            return res;
        } else {
            message.error(res.message || '请求失败');
            return Promise.reject(new Error(res.message || '请求失败'));
        }
    },
    error => {
        console.error('响应错误：', error);
        
        if (error.response) {
            switch (error.response.status) {
                case 400:
                    message.error(error.response.data?.message || '请求参数错误');
                    break;
                case 401:
                    message.error(error.response.data?.message || '未授权，请重新登录');
                    const authStore = useAuthStore();
                    authStore.clearToken();
                    window.location.href = '/login';
                    break;
                case 403:
                    message.error('拒绝访问');
                    break;
                case 404:
                    message.error('请求的资源不存在');
                    break;
                case 422:
                    // 处理验证错误
                    const validationErrors = error.response.data?.detail;
                    if (validationErrors && Array.isArray(validationErrors)) {
                        const errorMessages = validationErrors.map(err => {
                            const field = err.loc ? err.loc.join('.') : '字段';
                            return `${field}: ${err.msg}`;
                        }).join('; ');
                        message.error(`输入验证失败: ${errorMessages}`);
                    } else if (error.response.data?.message) {
                        message.error(`验证错误: ${error.response.data.message}`);
                    } else {
                        message.error('输入数据格式错误，请检查您的输入');
                    }
                    break;
                case 500:
                    message.error('服务器错误');
                    break;
                default:
                    message.error(`请求失败: ${error.response.status}`);
            }
        } else if (error.request) {
            message.error('网络错误，请检查您的网络连接');
        } else {
            message.error('请求配置错误');
        }
        
        return Promise.reject(error);
    }
);

export default request; 