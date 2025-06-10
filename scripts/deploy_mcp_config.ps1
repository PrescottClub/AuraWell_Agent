# AuraWell MCP配置部署脚本
# 一键将优化的MCP配置部署到Cursor

Write-Host "🚀 AuraWell MCP配置部署工具" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

# 检查是否在正确的项目目录
if (-not (Test-Path "mcp_production_config.json")) {
    Write-Host "❌ 请确保在AuraWell项目根目录运行此脚本" -ForegroundColor Red
    exit 1
}

# 用户的Cursor MCP配置路径
$cursorMcpPath = "C:\Users\11146\.cursor\mcp.json"

# 备份现有配置
Write-Host "📋 备份现有MCP配置..." -ForegroundColor Yellow
if (Test-Path $cursorMcpPath) {
    $backupPath = "C:\Users\11146\.cursor\mcp.json.backup.$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    Copy-Item $cursorMcpPath $backupPath
    Write-Host "✅ 备份已保存到: $backupPath" -ForegroundColor Green
} else {
    Write-Host "ℹ️  未找到现有配置文件，将创建新的" -ForegroundColor Cyan
}

# 读取生产配置
Write-Host "📦 读取优化后的MCP配置..." -ForegroundColor Yellow
$mcpConfig = Get-Content "mcp_production_config.json" -Raw

# 检查必要的环境变量
Write-Host "🔧 检查环境配置..." -ForegroundColor Yellow
$braveApiKey = $env:BRAVE_API_KEY
if (-not $braveApiKey) {
    Write-Host "⚠️  BRAVE_API_KEY环境变量未设置" -ForegroundColor Yellow
    Write-Host "请设置您的Brave Search API密钥:" -ForegroundColor Cyan
    $braveApiKey = Read-Host "输入BRAVE_API_KEY (回车跳过)"
    
    if ($braveApiKey) {
        # 更新配置中的API密钥
        $mcpConfig = $mcpConfig -replace '"your_brave_api_key_here"', "`"$braveApiKey`""
        Write-Host "✅ 已更新Brave API密钥" -ForegroundColor Green
    } else {
        Write-Host "⚠️  跳过Brave Search配置，您可以稍后手动设置" -ForegroundColor Yellow
    }
}

# 确保Cursor目录存在
$cursorDir = Split-Path $cursorMcpPath -Parent
if (-not (Test-Path $cursorDir)) {
    Write-Host "📁 创建Cursor配置目录..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $cursorDir -Force | Out-Null
}

# 部署新配置
Write-Host "🔥 部署新的MCP配置..." -ForegroundColor Yellow
try {
    $mcpConfig | Out-File -FilePath $cursorMcpPath -Encoding UTF8
    Write-Host "✅ MCP配置已成功部署!" -ForegroundColor Green
} catch {
    Write-Host "❌ 部署失败: $_" -ForegroundColor Red
    exit 1
}

# 显示配置的工具列表
Write-Host "`n🛠️  已配置的MCP工具:" -ForegroundColor Cyan
Write-Host "  • figma          - UI设计协作" -ForegroundColor White
Write-Host "  • notion         - 笔记和知识管理" -ForegroundColor White  
Write-Host "  • github         - 代码仓库管理 (已配置Token)" -ForegroundColor White
Write-Host "  • sequential-thinking - 多步骤推理分析" -ForegroundColor White
Write-Host "  • quickchart     - 数据可视化图表" -ForegroundColor White
Write-Host "  • calculator     - 数学计算器" -ForegroundColor White
Write-Host "  • run-python     - Python代码执行" -ForegroundColor White
Write-Host "  • fetch          - 网页内容抓取" -ForegroundColor White
Write-Host "  • time           - 时间和日程管理" -ForegroundColor White
Write-Host "  • memory         - 知识图谱存储" -ForegroundColor White
Write-Host "  • database-sqlite - SQLite数据库操作" -ForegroundColor White
Write-Host "  • brave-search   - 网络搜索引擎" -ForegroundColor White
Write-Host "  • weather        - 天气信息查询" -ForegroundColor White
Write-Host "  • filesystem     - 文件系统操作" -ForegroundColor White

# 安装必要的包
Write-Host "`n📦 安装MCP服务器包..." -ForegroundColor Yellow
$packages = @(
    "@github/github-mcp-server",
    "@modelcontextprotocol/server-sequential-thinking",
    "@gongrzhe/quickchart-mcp-server", 
    "@pydantic-ai/mcp-run-python",
    "@modelcontextprotocol/server-memory",
    "@modelcontextprotocol/server-sqlite",
    "@modelcontextprotocol/server-brave-search",
    "@modelcontextprotocol/server-weather",
    "@modelcontextprotocol/server-filesystem"
)

$pythonPackages = @(
    "mcp_server_calculator",
    "mcp_server_fetch", 
    "mcp_server_time"
)

# 安装npm包
foreach ($package in $packages) {
    Write-Host "📦 安装 $package..." -ForegroundColor Cyan
    try {
        npm install -g $package --silent
        Write-Host "✅ $package" -ForegroundColor Green
    } catch {
        Write-Host "❌ $package 安装失败" -ForegroundColor Red
    }
}

# 安装Python包
Write-Host "`n🐍 安装Python MCP包..." -ForegroundColor Yellow
foreach ($package in $pythonPackages) {
    Write-Host "📦 安装 $package..." -ForegroundColor Cyan
    try {
        pip install $package --quiet
        Write-Host "✅ $package" -ForegroundColor Green
    } catch {
        Write-Host "❌ $package 安装失败" -ForegroundColor Red
    }
}

Write-Host "`n🎉 MCP配置部署完成!" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green
Write-Host "📋 下一步操作:" -ForegroundColor Cyan
Write-Host "  1. 重启Cursor编辑器" -ForegroundColor White
Write-Host "  2. 在聊天中测试MCP工具 (如: '分析健康数据')" -ForegroundColor White
Write-Host "  3. 如需要，设置BRAVE_API_KEY环境变量" -ForegroundColor White
Write-Host "`n🔧 配置文件位置: $cursorMcpPath" -ForegroundColor Gray

Write-Host "`n按任意键结束..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 