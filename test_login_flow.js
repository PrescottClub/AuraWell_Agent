/**
 * 测试登录流程
 * 验证前后端登录接口的完整性
 */

const axios = require('axios');

const API_BASE_URL = 'http://localhost:8000/api/v1';

// 测试用例
const testCases = [
    {
        name: '正确的登录凭据',
        username: 'test_user',
        password: 'test_password',
        expectedStatus: 200,
        shouldSucceed: true
    },
    {
        name: '错误的用户名',
        username: 'wrong_user',
        password: 'test_password',
        expectedStatus: 401,
        shouldSucceed: false
    },
    {
        name: '错误的密码',
        username: 'test_user',
        password: 'wrong_password',
        expectedStatus: 401,
        shouldSucceed: false
    },
    {
        name: '用户名太短',
        username: 'ab',
        password: 'test_password',
        expectedStatus: 422,
        shouldSucceed: false
    },
    {
        name: '密码太短',
        username: 'test_user',
        password: '123',
        expectedStatus: 422,
        shouldSucceed: false
    },
    {
        name: '演示用户登录',
        username: 'demo_user',
        password: 'demo_password',
        expectedStatus: 200,
        shouldSucceed: true
    }
];

async function testLogin(testCase) {
    console.log(`\n🧪 测试: ${testCase.name}`);
    console.log(`   用户名: ${testCase.username}`);
    console.log(`   密码: ${testCase.password}`);
    
    try {
        const response = await axios.post(`${API_BASE_URL}/auth/login`, {
            username: testCase.username,
            password: testCase.password
        });
        
        console.log(`   ✅ 状态码: ${response.status}`);
        console.log(`   📝 响应: ${response.data.message}`);
        
        if (testCase.shouldSucceed) {
            if (response.data.success && response.data.data.access_token) {
                console.log(`   🎉 登录成功！Token: ${response.data.data.access_token.substring(0, 20)}...`);
                return { success: true, token: response.data.data.access_token };
            } else {
                console.log(`   ❌ 期望成功但响应格式不正确`);
                return { success: false, error: '响应格式错误' };
            }
        } else {
            console.log(`   ❌ 期望失败但请求成功了`);
            return { success: false, error: '期望失败但成功了' };
        }
        
    } catch (error) {
        const status = error.response?.status;
        const message = error.response?.data?.message || error.message;
        
        console.log(`   ❌ 状态码: ${status}`);
        console.log(`   📝 错误: ${message}`);
        
        if (!testCase.shouldSucceed && status === testCase.expectedStatus) {
            console.log(`   ✅ 按预期失败`);
            return { success: true, expectedFailure: true };
        } else if (testCase.shouldSucceed) {
            console.log(`   ❌ 期望成功但失败了`);
            return { success: false, error: message };
        } else {
            console.log(`   ⚠️  失败但状态码不匹配 (期望: ${testCase.expectedStatus}, 实际: ${status})`);
            return { success: false, error: `状态码不匹配` };
        }
    }
}

async function testProtectedEndpoint(token) {
    console.log(`\n🔐 测试受保护的端点`);
    
    try {
        const response = await axios.get(`${API_BASE_URL}/health-plan/plans`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        console.log(`   ✅ 状态码: ${response.status}`);
        console.log(`   📝 响应: ${response.data.message}`);
        return { success: true };
        
    } catch (error) {
        const status = error.response?.status;
        const message = error.response?.data?.message || error.message;
        
        console.log(`   ❌ 状态码: ${status}`);
        console.log(`   📝 错误: ${message}`);
        return { success: false, error: message };
    }
}

async function runAllTests() {
    console.log('🚀 开始登录流程测试');
    console.log('='.repeat(50));
    
    let successCount = 0;
    let failureCount = 0;
    let validToken = null;
    
    // 运行所有登录测试
    for (const testCase of testCases) {
        const result = await testLogin(testCase);
        
        if (result.success) {
            successCount++;
            if (result.token) {
                validToken = result.token;
            }
        } else {
            failureCount++;
        }
        
        // 添加延迟避免请求过快
        await new Promise(resolve => setTimeout(resolve, 500));
    }
    
    // 测试受保护的端点
    if (validToken) {
        const protectedResult = await testProtectedEndpoint(validToken);
        if (protectedResult.success) {
            successCount++;
        } else {
            failureCount++;
        }
    }
    
    // 输出测试结果
    console.log('\n' + '='.repeat(50));
    console.log('📊 测试结果汇总');
    console.log(`✅ 成功: ${successCount}`);
    console.log(`❌ 失败: ${failureCount}`);
    console.log(`📈 成功率: ${((successCount / (successCount + failureCount)) * 100).toFixed(1)}%`);
    
    if (failureCount === 0) {
        console.log('\n🎉 所有测试通过！登录流程工作正常。');
    } else {
        console.log('\n⚠️  部分测试失败，请检查问题。');
    }
}

// 检查服务器是否运行
async function checkServerStatus() {
    console.log('🔍 检查服务器状态...');
    
    try {
        const response = await axios.get(`${API_BASE_URL.replace('/api/v1', '')}/`);
        console.log('✅ 后端服务器运行正常');
        return true;
    } catch (error) {
        console.log('❌ 后端服务器未运行或无法访问');
        console.log('   请确保后端服务在 http://localhost:8000 运行');
        return false;
    }
}

// 主函数
async function main() {
    const serverRunning = await checkServerStatus();
    
    if (!serverRunning) {
        console.log('\n💡 启动后端服务器的命令:');
        console.log('   cd /path/to/project && python -m aurawell.main');
        process.exit(1);
    }
    
    await runAllTests();
}

// 运行测试
if (require.main === module) {
    main().catch(error => {
        console.error('测试运行失败:', error.message);
        process.exit(1);
    });
}

module.exports = {
    testLogin,
    testProtectedEndpoint,
    runAllTests
};
