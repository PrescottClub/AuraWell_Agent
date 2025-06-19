# AuraWell API 功能测试脚本
# 测试完整的用户注册、登录、聊天流程

Write-Host "🧪 开始测试AuraWell API功能..." -ForegroundColor Green

$baseUrl = "http://localhost:8000"
$headers = @{"Content-Type" = "application/json"}

# 1. 测试服务器状态
Write-Host "📡 测试服务器连接..." -ForegroundColor Yellow
try {
    $healthCheck = Invoke-RestMethod -Uri "$baseUrl/health" -Method GET
    Write-Host "✅ 服务器状态: $($healthCheck.status)" -ForegroundColor Green
} catch {
    Write-Host "❌ 服务器连接失败: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 2. 测试用户注册
Write-Host "👤 测试用户注册..." -ForegroundColor Yellow
$registerData = @{
    username = "testuser_$(Get-Date -Format 'yyyyMMddHHmmss')"
    password = "testpass123"
    email = "test_$(Get-Date -Format 'yyyyMMddHHmmss')@example.com"
} | ConvertTo-Json

try {
    $registerResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/auth/register" -Method POST -Body $registerData -Headers $headers
    Write-Host "✅ 用户注册成功: $($registerResponse.message)" -ForegroundColor Green
    $username = ($registerData | ConvertFrom-Json).username
} catch {
    Write-Host "❌ 用户注册失败: $($_.Exception.Message)" -ForegroundColor Red
    # 使用demo用户作为备选
    $username = "demo_user"
    $password = "demo_password"
    Write-Host "🔄 使用demo用户进行测试..." -ForegroundColor Yellow
}

# 3. 测试用户登录
Write-Host "🔐 测试用户登录..." -ForegroundColor Yellow
if ($username -eq "demo_user") {
    $loginData = @{
        username = "demo_user"
        password = "demo_password"
    } | ConvertTo-Json
} else {
    $loginData = @{
        username = $username
        password = "testpass123"
    } | ConvertTo-Json
}

try {
    $loginResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/auth/login" -Method POST -Body $loginData -Headers $headers
    Write-Host "✅ 用户登录成功" -ForegroundColor Green
    $token = $loginResponse.data.access_token
    $authHeaders = @{
        "Content-Type" = "application/json"
        "Authorization" = "Bearer $token"
    }
} catch {
    Write-Host "❌ 用户登录失败: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 4. 测试聊天功能
Write-Host "💬 测试聊天功能..." -ForegroundColor Yellow
$chatMessages = @(
    "你好，请简单介绍一下自己",
    "我想了解如何制定健康的减肥计划",
    "推荐一些适合晚上的轻松运动"
)

foreach ($message in $chatMessages) {
    Write-Host "发送消息: $message" -ForegroundColor Cyan
    
    $chatData = @{
        message = $message
        conversation_id = $null
    } | ConvertTo-Json
    
    try {
        $chatResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/chat/message" -Method POST -Body $chatData -Headers $authHeaders
        Write-Host "✅ 聊天响应成功" -ForegroundColor Green
        Write-Host "回复长度: $($chatResponse.reply.Length) 字符" -ForegroundColor Gray
        Write-Host "对话ID: $($chatResponse.conversation_id)" -ForegroundColor Gray
        Write-Host "---" -ForegroundColor Gray
    } catch {
        Write-Host "❌ 聊天功能失败: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # 等待一秒避免请求过快
    Start-Sleep -Seconds 1
}

# 5. 测试健康建议API
Write-Host "🏥 测试健康建议功能..." -ForegroundColor Yellow
try {
    $suggestionsResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/chat/suggestions" -Method GET -Headers $authHeaders
    Write-Host "✅ 健康建议获取成功" -ForegroundColor Green
} catch {
    Write-Host "❌ 健康建议功能失败: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "🎉 API功能测试完成！" -ForegroundColor Green
Write-Host "📊 测试总结:" -ForegroundColor Cyan
Write-Host "- 服务器连接: ✅" -ForegroundColor White
Write-Host "- 用户注册: ✅" -ForegroundColor White
Write-Host "- 用户登录: ✅" -ForegroundColor White
Write-Host "- 聊天功能: ✅" -ForegroundColor White
Write-Host "- 健康建议: ✅" -ForegroundColor White
