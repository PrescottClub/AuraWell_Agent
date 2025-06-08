import { MockMethod } from 'vite-plugin-mock';
import Mock from 'mockjs';

// 生成用户列表数据
const userList = Mock.mock({
    'list|10': [{
        'id|+1': 1,
        'username': '@cname',
        'email': '@email',
        'avatar': '@image("200x200")',
        'role': '@pick(["admin", "user"])',
        'status|1': ['active', 'inactive'],
        'createTime': '@datetime',
        'lastLoginTime': '@datetime'
    }]
}).list;

// 生成统计数据
const statistics = Mock.mock({
    'userCount': '@integer(1000, 9999)',
    'todayConversations': '@integer(100, 999)',
    'averageResponseTime': '@float(0.1, 2, 1, 1)',
    'satisfactionRate': '@integer(90, 99)'
});

const mockUserApis: MockMethod[] = [
    // 登录接口
    {
        url: '/api/auth/login',
        method: 'post',
        response: ({ body }) => {
            const { username, password } = body;
            if (username === 'admin' && password === '123456') {
                return {
                    code: 200,
                    data: {
                        token: Mock.Random.guid(),
                        userInfo: {
                            id: 1,
                            username: 'admin',
                            role: 'admin',
                            avatar: Mock.Random.image('200x200')
                        }
                    },
                    message: '登录成功'
                };
            }
            return {
                code: 401,
                message: '用户名或密码错误'
            };
        }
    },

    // 获取用户信息
    {
        url: '/api/user/info',
        method: 'get',
        response: () => {
            return {
                code: 200,
                data: {
                    id: 1,
                    username: 'admin',
                    role: 'admin',
                    avatar: Mock.Random.image('200x200'),
                    permissions: ['dashboard', 'users', 'settings']
                },
                message: '获取成功'
            };
        }
    },

    // 获取用户列表
    {
        url: '/api/user/list',
        method: 'get',
        response: ({ query }) => {
            const { page = 1, pageSize = 10 } = query;
            const start = (page - 1) * pageSize;
            const end = start + pageSize;
            const list = userList.slice(start, end);

            return {
                code: 200,
                data: {
                    list,
                    total: userList.length,
                    page: Number(page),
                    pageSize: Number(pageSize)
                },
                message: '获取成功'
            };
        }
    },

    // 更新用户信息
    {
        url: '/api/user/update',
        method: 'put',
        response: ({ body }) => {
            return {
                code: 200,
                data: body,
                message: '更新成功'
            };
        }
    },

    // 删除用户
    {
        url: '/api/user/:id',
        method: 'delete',
        response: ({ params }) => {
            return {
                code: 200,
                data: null,
                message: '删除成功'
            };
        }
    },

    // 获取统计数据
    {
        url: '/api/statistics',
        method: 'get',
        response: () => {
            return {
                code: 200,
                data: statistics,
                message: '获取成功'
            };
        }
    }
];

export default mockUserApis; 