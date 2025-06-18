#!/bin/bash

# 测试登录流程脚本
# 验证前后端登录接口的完整性

API_BASE_URL="http://localhost:8000/api/v1"

echo "🚀 开始登录流程测试"
echo "=================================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

success_count=0
failure_count=0

# 测试函数
test_login() {
    local test_name="$1"
    local username="$2"
    local password="$3"
    local expected_status="$4"
    local should_succeed="$5"
    
    echo -e "\n🧪 测试: ${BLUE}$test_name${NC}"
    echo "   用户名: $username"
    echo "   密码: $password"
    
    # 发送登录请求
    response=$(curl -s -w "\n%{http_code}" -X POST "$API_BASE_URL/auth/login" \
        -H "Content-Type: application/json" \
        -d "{\"username\":\"$username\",\"password\":\"$password\"}")
    
    # 分离响应体和状态码
    http_code=$(echo "$response" | tail -n1)
    response_body=$(echo "$response" | head -n -1)
    
    echo "   状态码: $http_code"
    
    if [ "$should_succeed" = "true" ]; then
        if [ "$http_code" = "200" ]; then
            echo -e "   ${GREEN}✅ 登录成功！${NC}"
            # 提取token
            token=$(echo "$response_body" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
            if [ -n "$token" ]; then
                echo "   🎉 Token: ${token:0:20}..."
                echo "$token" > /tmp/test_token.txt
            fi
            ((success_count++))
        else
            echo -e "   ${RED}❌ 期望成功但失败了${NC}"
            echo "   响应: $response_body"
            ((failure_count++))
        fi
    else
        if [ "$http_code" = "$expected_status" ]; then
            echo -e "   ${GREEN}✅ 按预期失败${NC}"
            ((success_count++))
        else
            echo -e "   ${YELLOW}⚠️  失败但状态码不匹配 (期望: $expected_status, 实际: $http_code)${NC}"
            ((failure_count++))
        fi
        echo "   响应: $response_body"
    fi
}

# 测试受保护的端点
test_protected_endpoint() {
    echo -e "\n🔐 测试受保护的端点"
    
    if [ -f "/tmp/test_token.txt" ]; then
        token=$(cat /tmp/test_token.txt)
        
        response=$(curl -s -w "\n%{http_code}" -X GET "$API_BASE_URL/health-plan/plans" \
            -H "Authorization: Bearer $token")
        
        http_code=$(echo "$response" | tail -n1)
        response_body=$(echo "$response" | head -n -1)
        
        echo "   状态码: $http_code"
        
        if [ "$http_code" = "200" ]; then
            echo -e "   ${GREEN}✅ 受保护端点访问成功${NC}"
            ((success_count++))
        else
            echo -e "   ${RED}❌ 受保护端点访问失败${NC}"
            echo "   响应: $response_body"
            ((failure_count++))
        fi
    else
        echo -e "   ${RED}❌ 没有有效的token${NC}"
        ((failure_count++))
    fi
}

# 检查服务器状态
check_server() {
    echo "🔍 检查服务器状态..."
    
    response=$(curl -s -w "%{http_code}" -X GET "http://localhost:8000/" -o /dev/null)
    
    if [ "$response" = "200" ] || [ "$response" = "404" ]; then
        echo -e "${GREEN}✅ 后端服务器运行正常${NC}"
        return 0
    else
        echo -e "${RED}❌ 后端服务器未运行或无法访问${NC}"
        echo "   请确保后端服务在 http://localhost:8000 运行"
        echo ""
        echo "💡 启动后端服务器的命令:"
        echo "   cd /path/to/project && python -m aurawell.main"
        return 1
    fi
}

# 主测试流程
main() {
    # 检查服务器
    if ! check_server; then
        exit 1
    fi
    
    # 清理临时文件
    rm -f /tmp/test_token.txt
    
    # 运行测试用例
    test_login "正确的登录凭据" "test_user" "test_password" "200" "true"
    test_login "错误的用户名" "wrong_user" "test_password" "401" "false"
    test_login "错误的密码" "test_user" "wrong_password" "401" "false"
    test_login "用户名太短" "ab" "test_password" "422" "false"
    test_login "密码太短" "test_user" "123" "422" "false"
    test_login "演示用户登录" "demo_user" "demo_password" "200" "true"
    
    # 测试受保护的端点
    test_protected_endpoint
    
    # 输出测试结果
    echo ""
    echo "=================================================="
    echo "📊 测试结果汇总"
    echo -e "${GREEN}✅ 成功: $success_count${NC}"
    echo -e "${RED}❌ 失败: $failure_count${NC}"
    
    total=$((success_count + failure_count))
    if [ $total -gt 0 ]; then
        success_rate=$(echo "scale=1; $success_count * 100 / $total" | bc -l)
        echo "📈 成功率: ${success_rate}%"
    fi
    
    if [ $failure_count -eq 0 ]; then
        echo -e "\n${GREEN}🎉 所有测试通过！登录流程工作正常。${NC}"
    else
        echo -e "\n${YELLOW}⚠️  部分测试失败，请检查问题。${NC}"
    fi
    
    # 清理临时文件
    rm -f /tmp/test_token.txt
}

# 运行主函数
main
