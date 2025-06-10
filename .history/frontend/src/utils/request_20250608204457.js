import axios from 'axios';
import { message } from 'ant-design-vue';

// 创建 axios 实例
const request = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || '/api', // 从环境变量获取 API 基础路径
    timeout: 15000, // 请求超时时间
    headers: {
        'Content-Type': 'application/json',
    }
});

// 请求拦截器
request.interceptors.request.use(
    config => {
        // 从 localStorage 获取 token
        const token = localStorage.getItem('token');
        if (token) {
            config.headers['Authorization'] = `Bearer ${token}`;
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
        
        // 这里可以根据后端的响应结构进行调整
        if (res.code && res.code !== 200) {
            message.error(res.message || '请求失败');
            return Promise.reject(new Error(res.message || '请求失败'));
        }
        
        return res;
    },
    error => {
        console.error('响应错误：', error);
        
        // 处理 HTTP 错误状态
        if (error.response) {
            switch (error.response.status) {
                case 401:
                    message.error('未授权，请重新登录');
                    // 可以在这里处理登出逻辑
                    localStorage.removeItem('token');
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