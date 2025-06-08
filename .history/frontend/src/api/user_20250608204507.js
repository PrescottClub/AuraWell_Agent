import request from '@/utils/request';

// 用户登录
export function login(data) {
    return request({
        url: '/auth/login',
        method: 'post',
        data
    });
}

// 获取用户信息
export function getUserInfo() {
    return request({
        url: '/user/info',
        method: 'get'
    });
}

// 获取用户列表
export function getUserList(params) {
    return request({
        url: '/user/list',
        method: 'get',
        params
    });
}

// 更新用户信息
export function updateUser(data) {
    return request({
        url: '/user/update',
        method: 'put',
        data
    });
}

// 删除用户
export function deleteUser(id) {
    return request({
        url: `/user/${id}`,
        method: 'delete'
    });
} 