import axios from 'axios';
import { message } from 'ant-design-vue';
import { useAuthStore } from '../stores/auth';

const request = axios.create({
    baseURL: import.meta.env.VITE_APP_API_BASE_URL || '/api/v1',
    timeout: import.meta.env.VITE_API_TIMEOUT || 60000, // 增加到60秒，适应AI处理时间
    headers: {
        'Content-Type': 'application/json; charset=utf-8',
        'Accept': 'application/json'
        // 移除 Accept-Charset，浏览器不允许设置此头
    }
});

// 🔧 统一请求拦截器 - 简化认证逻辑
request.interceptors.request.use(
    config => {
        // 登录和注册请求不需要认证头
        const isAuthRequest = config.url?.includes('/auth/login') || config.url?.includes('/auth/register');

        if (!isAuthRequest) {
            const authStore = useAuthStore();
            const authHeader = authStore.getAuthHeader();

            if (authHeader) {
                config.headers['Authorization'] = authHeader;
                console.log('🔐 使用存储的认证token');
            } else if (import.meta.env.DEV || import.meta.env.VITE_APP_ENV === 'development') {
                // 开发环境：先尝试自动登录获取真实token
                console.warn('⚠️ 缺少认证token，需要先登录');
                // 不设置无效的dev-test-token，让请求失败并触发自动登录
            }
        }

        // 确保请求数据正确编码
        if (config.data && typeof config.data === 'object') {
            // 确保Content-Type包含charset
            config.headers['Content-Type'] = 'application/json; charset=utf-8';

            // 手动序列化JSON以确保UTF-8编码
            try {
                const jsonString = JSON.stringify(config.data);
                // 验证JSON字符串是否包含正确的中文字符
                console.log('🔤 JSON序列化结果:', jsonString);
                config.data = jsonString;

                // 明确设置transformRequest为空，避免axios再次处理
                config.transformRequest = [];
            } catch (error) {
                console.error('❌ JSON序列化失败:', error);
            }
        }

        // 添加请求日志
        console.log(`📤 发送请求: ${config.method?.toUpperCase()} ${config.url}`, {
            headers: config.headers,
            data: config.data
        });

        return config;
    },
    error => {
        console.error('请求错误：', error);
        return Promise.reject(error);
    }
);

// 🔧 统一响应拦截器 - 优化错误处理
request.interceptors.response.use(
    response => {
        const res = response.data;

        // 添加响应日志
        console.log(`📥 收到响应: ${response.status} ${response.config?.url}`, res);

        // 兼容不同的响应格式
        if (res.status === 'success' || res.success === true || response.status === 200) {
            return res;
        } else {
            const errorMessage = res.message || res.error || '请求失败';
            message.error(errorMessage);
            return Promise.reject(new Error(errorMessage));
        }
    },
    async error => {
        console.error('响应错误：', error);
        console.error('错误详情：', {
            message: error.message,
            code: error.code,
            config: {
                url: error.config?.url,
                method: error.config?.method,
                headers: error.config?.headers,
                data: error.config?.data
            },
            response: error.response ? {
                status: error.response.status,
                statusText: error.response.statusText,
                data: error.response.data,
                headers: error.response.headers
            } : null,
            request: error.request ? 'Request was made but no response received' : null
        });

        if (error.response) {
            const { status, data } = error.response;
            const errorMessage = data?.message || data?.detail || '请求失败';

            switch (status) {
                case 400:
                    message.error(errorMessage || '请求参数错误');
                    break;

                case 401: {
                    // 🔧 统一401错误处理 - 防止认证循环
                    console.warn('🔐 认证失败，处理401错误');

                    const currentPath = window.location.pathname;
                    if (currentPath === '/login') {
                        console.warn('⚠️ 已在登录页面，跳过重定向防止循环');
                        break;
                    }

                    const authStore = useAuthStore();

                    // 清除认证信息
                    authStore.clearToken();

                    // 显示错误消息
                    message.error(errorMessage || '认证失效，请重新登录');

                    // 延迟跳转到登录页
                    setTimeout(() => {
                        window.location.href = '/login';
                    }, 100);
                    break;
                }
                case 403:
                    message.error('拒绝访问');
                    break;
                case 404:
                    message.error('请求的资源不存在');
                    break;
                case 422: {
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
                }
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