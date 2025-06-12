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
        const authStore = useAuthStore();
        const authHeader = authStore.getAuthHeader();
        if (authHeader) {
            config.headers['Authorization'] = authHeader;
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
                case 401:
                    message.error('未授权，请重新登录');
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