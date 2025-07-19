# AuraWell MCP 环境启动脚本
# PowerShell版本，用于Windows环境

Write-Host "🚀 启动 AuraWell MCP 开发环境" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

# 检查是否在项目根目录
if (-not (Test-Path "aurawell") -or -not (Test-Path "requirements.txt")) {
    Write-Host "❌ 请在AuraWell项目根目录运行此脚本" -ForegroundColor Red
    exit 1
}

# 激活虚拟环境
Write-Host "📦 激活Python虚拟环境..." -ForegroundColor Yellow
if (Test-Path ".venv\Scripts\Activate.ps1") {
    & .venv\Scripts\Activate.ps1
    Write-Host "✅ 虚拟环境已激活" -ForegroundColor Green
} else {
    Write-Host "❌ 虚拟环境未找到，请先运行: python -m venv .venv" -ForegroundColor Red
    exit 1
}

# 检查环境变量
Write-Host "🔧 检查环境变量..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  .env文件未找到，使用env.example作为模板" -ForegroundColor Yellow
    if (Test-Path "env.example") {
        Copy-Item "env.example" ".env"
        Write-Host "📋 已创建.env文件，请配置API密钥" -ForegroundColor Cyan
    }
}

# 加载环境变量
if (Test-Path ".env") {
    Write-Host "📋 加载环境变量..." -ForegroundColor Yellow
    Get-Content ".env" | ForEach-Object {
        if ($_ -match "^([^#].*)=(.*)$") {
            Set-Item -Path "env:$($matches[1])" -Value $matches[2]
        }
    }
}

# 检查Node.js和npm
Write-Host "🔍 检查Node.js环境..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version
    $npmVersion = npm --version
    Write-Host "✅ Node.js: $nodeVersion" -ForegroundColor Green
    Write-Host "✅ npm: $npmVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ 请先安装Node.js和npm" -ForegroundColor Red
    exit 1
}

# 安装MCP包
Write-Host "📦 安装MCP服务器包..." -ForegroundColor Yellow
$mcpPackages = @(
    "@modelcontextprotocol/server-sqlite",
    "@modelcontextprotocol/server-brave-search", 
    "@modelcontextprotocol/server-memory",
    "@modelcontextprotocol/server-sequential-thinking",
    "@modelcontextprotocol/server-quickchart",
    "@modelcontextprotocol/server-calculator",
    "@modelcontextprotocol/server-notion"
)

foreach ($package in $mcpPackages) {
    Write-Host "📦 安装 $package..." -ForegroundColor Cyan
    try {
        npm install -g $package --silent
        Write-Host "✅ $package 安装成功" -ForegroundColor Green
    } catch {
        Write-Host "❌ $package 安装失败" -ForegroundColor Red
    }
}

# 检查数据库
Write-Host "🗄️  检查数据库..." -ForegroundColor Yellow
if (-not (Test-Path "aurawell.db")) {
    Write-Host "📋 创建空数据库文件..." -ForegroundColor Cyan
    # 创建空的SQLite数据库文件
    $null = New-Item -Path "aurawell.db" -ItemType File -Force
}

# 启动MCP服务器（后台运行）
Write-Host "🔥 启动MCP服务器..." -ForegroundColor Yellow

# 启动数据库服务器
Write-Host "📊 启动数据库服务器..." -ForegroundColor Cyan
Start-Job -Name "MCPDatabase" -ScriptBlock {
    npx -y @modelcontextprotocol/server-sqlite ./aurawell.db
} | Out-Null

# 如果有BRAVE_API_KEY，启动搜索服务器
if ($env:BRAVE_API_KEY) {
    Write-Host "🔍 启动搜索服务器..." -ForegroundColor Cyan
    Start-Job -Name "MCPBraveSearch" -ScriptBlock {
        npx -y @modelcontextprotocol/server-brave-search
    } | Out-Null
} else {
    Write-Host "⚠️  BRAVE_API_KEY未设置，跳过搜索服务器" -ForegroundColor Yellow
}

# 启动内存服务器
Write-Host "🧠 启动知识图谱服务器..." -ForegroundColor Cyan
Start-Job -Name "MCPMemory" -ScriptBlock {
    npx -y @modelcontextprotocol/server-memory
} | Out-Null

# 启动推理服务器
Write-Host "🤔 启动推理服务器..." -ForegroundColor Cyan
Start-Job -Name "MCPSequentialThinking" -ScriptBlock {
    npx -y @modelcontextprotocol/server-sequential-thinking
} | Out-Null

# 等待服务器启动
Start-Sleep -Seconds 3

# 检查服务器状态
Write-Host "🔍 检查服务器状态..." -ForegroundColor Yellow
$jobs = Get-Job
foreach ($job in $jobs) {
    if ($job.State -eq "Running") {
        Write-Host "✅ $($job.Name) 运行正常" -ForegroundColor Green
    } else {
        Write-Host "❌ $($job.Name) 启动失败" -ForegroundColor Red
    }
}

# 运行Python自动化脚本
Write-Host "🐍 运行Python MCP自动化脚本..." -ForegroundColor Yellow
try {
    python scripts/mcp_auto_setup.py
} catch {
    Write-Host "⚠️  Python自动化脚本运行失败，手动启动完成" -ForegroundColor Yellow
}

# 显示使用指南
Write-Host "`n🎉 MCP环境启动完成！" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green
Write-Host "📋 使用指南:" -ForegroundColor Cyan
Write-Host "  • 在Cursor中使用AI助手时，MCP工具会自动激活" -ForegroundColor White
Write-Host "  • 数据库工具: 查询和分析健康数据" -ForegroundColor White
Write-Host "  • 搜索工具: 获取最新健康研究信息" -ForegroundColor White
Write-Host "  • 内存工具: 构建用户健康知识图谱" -ForegroundColor White
Write-Host "  • 推理工具: 进行复杂健康问题分析" -ForegroundColor White
Write-Host "`n🛑 停止服务器: 运行 Stop-Job * 命令" -ForegroundColor Red
Write-Host "📊 查看服务器状态: 运行 Get-Job 命令" -ForegroundColor Cyan

# 保持脚本运行，等待用户输入
Write-Host "`n按任意键继续或Ctrl+C退出..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

Write-Host "🚀 环境准备就绪，开始使用AuraWell开发环境！" -ForegroundColor Green
