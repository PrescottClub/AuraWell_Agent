# MCP服务器安装和配置脚本
# 适用于Windows系统和AuraWell项目

Write-Host "开始安装MCP服务器..." -ForegroundColor Green

# 检查Node.js是否已安装
try {
    $nodeVersion = node --version
    Write-Host "检测到Node.js版本: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "错误: 未检测到Node.js，请先安装Node.js" -ForegroundColor Red
    exit 1
}

# 检查npx是否可用
try {
    npx --version | Out-Null
    Write-Host "npx可用" -ForegroundColor Green
} catch {
    Write-Host "错误: npx不可用，请检查Node.js安装" -ForegroundColor Red
    exit 1
}

# 获取当前项目路径
$projectPath = (Get-Location).Path
Write-Host "当前项目路径: $projectPath" -ForegroundColor Cyan

# 获取用户主目录
$userHome = $env:USERPROFILE
$cursorConfigPath = "$userHome\AppData\Roaming\Cursor\User\globalStorage\mcp.json"

# 如果配置目录不存在，创建它
$configDir = Split-Path $cursorConfigPath -Parent
if (-not (Test-Path $configDir)) {
    New-Item -ItemType Directory -Path $configDir -Force
    Write-Host "创建配置目录: $configDir" -ForegroundColor Yellow
}

# 创建MCP配置内容
$mcpConfig = @{
    mcpServers = @{
        "TalkToFigma" = @{
            command = "bunx"
            args = @(
                "cursor-talk-to-figma-mcp@latest",
                "--server=vps.sonnylab.com"
            )
        }
        "filesystem" = @{
            command = "npx"
            args = @(
                "-y",
                "@modelcontextprotocol/server-filesystem",
                $projectPath
            )
        }
        "git" = @{
            command = "npx"
            args = @(
                "-y",
                "@modelcontextprotocol/server-git",
                "--repository",
                $projectPath
            )
        }
        "sqlite" = @{
            command = "npx"
            args = @(
                "-y",
                "@modelcontextprotocol/server-sqlite",
                "$projectPath\aurawell.db"
            )
        }
        "duckdb" = @{
            command = "npx"
            args = @(
                "-y",
                "mcp-server-duckdb",
                "--db-path",
                "$projectPath\data\analytics.db"
            )
        }
        "database-server" = @{
            command = "npx"
            args = @(
                "-y",
                "@executeautomation/database-server",
                "$projectPath\aurawell.db"
            )
        }
        "fetch" = @{
            command = "npx"
            args = @(
                "-y",
                "@modelcontextprotocol/server-fetch"
            )
        }
        "memory" = @{
            command = "npx"
            args = @(
                "-y",
                "@modelcontextprotocol/server-memory"
            )
        }
    }
}

# 将配置转换为JSON并写入文件
$jsonConfig = $mcpConfig | ConvertTo-Json -Depth 10
Set-Content -Path $cursorConfigPath -Value $jsonConfig -Encoding UTF8

Write-Host "MCP配置已写入: $cursorConfigPath" -ForegroundColor Green

# 预安装一些常用的MCP服务器包
Write-Host "开始预安装MCP服务器包..." -ForegroundColor Yellow

$packages = @(
    "@modelcontextprotocol/server-filesystem",
    "@modelcontextprotocol/server-git", 
    "@modelcontextprotocol/server-sqlite",
    "mcp-server-duckdb",
    "@executeautomation/database-server",
    "@modelcontextprotocol/server-fetch",
    "@modelcontextprotocol/server-memory"
)

foreach ($package in $packages) {
    Write-Host "安装包: $package" -ForegroundColor Cyan
    try {
        npx -y $package --help | Out-Null
        Write-Host "✓ $package 安装成功" -ForegroundColor Green
    } catch {
        Write-Host "⚠ $package 安装可能失败，使用时会自动下载" -ForegroundColor Yellow
    }
}

# 创建数据目录
$dataDir = "$projectPath\data"
if (-not (Test-Path $dataDir)) {
    New-Item -ItemType Directory -Path $dataDir -Force
    Write-Host "创建数据目录: $dataDir" -ForegroundColor Yellow
}

Write-Host "`n安装完成！" -ForegroundColor Green
Write-Host "配置文件位置: $cursorConfigPath" -ForegroundColor Cyan
Write-Host "请重启Cursor以加载新的MCP配置" -ForegroundColor Yellow

Write-Host "`n已配置的MCP服务器:" -ForegroundColor Cyan
Write-Host "1. TalkToFigma - Figma设计工具集成" -ForegroundColor White
Write-Host "2. filesystem - 文件系统操作" -ForegroundColor White  
Write-Host "3. git - Git版本控制" -ForegroundColor White
Write-Host "4. sqlite - SQLite数据库访问" -ForegroundColor White
Write-Host "5. duckdb - DuckDB分析数据库" -ForegroundColor White
Write-Host "6. database-server - 多数据库支持" -ForegroundColor White
Write-Host "7. fetch - 网页内容获取" -ForegroundColor White
Write-Host "8. memory - 持久化记忆存储" -ForegroundColor White

Write-Host "`n注意事项:" -ForegroundColor Yellow
Write-Host "- 某些服务需要API密钥，请在配置中设置相应的环境变量" -ForegroundColor White
Write-Host "- GitHub服务需要Personal Access Token" -ForegroundColor White  
Write-Host "- 搜索服务需要对应的API密钥" -ForegroundColor White 