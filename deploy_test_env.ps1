# AuraWell 测试环境部署脚本
# 创建完整的虚拟环境并启动服务

Write-Host "🚀 开始部署AuraWell测试环境..." -ForegroundColor Green

# 1. 创建虚拟环境
Write-Host "📦 创建虚拟环境..." -ForegroundColor Yellow
if (Test-Path "aurawell_test_env") {
    Write-Host "删除现有虚拟环境..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force "aurawell_test_env"
}
python -m venv aurawell_test_env

# 2. 激活虚拟环境并安装依赖
Write-Host "📚 安装依赖包..." -ForegroundColor Yellow
& ".\aurawell_test_env\Scripts\Activate.ps1"
pip install --upgrade pip
pip install -r requirements.txt

# 3. 检查环境变量
Write-Host "🔧 检查环境变量..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Write-Host "❌ .env文件不存在！请确保.env文件存在。" -ForegroundColor Red
    exit 1
}

# 4. 创建数据库
Write-Host "🗄️ 初始化数据库..." -ForegroundColor Yellow
python -c "
from src.aurawell.database.connection import DatabaseManager
import asyncio

async def init_db():
    db_manager = DatabaseManager()
    await db_manager.initialize()
    print('数据库初始化完成')
    await db_manager.close()

asyncio.run(init_db())
"

# 5. 启动服务器
Write-Host "🌟 启动AuraWell服务器..." -ForegroundColor Green
Write-Host "服务器将在 http://localhost:8000 启动" -ForegroundColor Cyan
Write-Host "API文档: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "按 Ctrl+C 停止服务器" -ForegroundColor Yellow

python -m uvicorn src.aurawell.interfaces.api_interface:app --host 0.0.0.0 --port 8000 --reload
