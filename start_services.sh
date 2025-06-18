#!/bin/bash

# AuraWell 服务启动脚本
# 用于快速启动前后端服务

set -e

echo "🚀 启动 AuraWell 健康管理系统"
echo "=================================="

# 检查是否在项目根目录
if [ ! -f "run_api_server.py" ] || [ ! -d "frontend" ]; then
    echo "❌ 错误: 请在项目根目录运行此脚本"
    exit 1
fi

# 检查Python环境
if ! command -v python &> /dev/null; then
    echo "❌ 错误: 未找到Python环境"
    exit 1
fi

# 检查Node.js环境
if ! command -v npm &> /dev/null; then
    echo "❌ 错误: 未找到Node.js/npm环境"
    exit 1
fi

# 检查数据库
echo "🔍 检查数据库状态..."
if [ ! -f "aurawell.db" ]; then
    echo "📊 初始化数据库..."
    python init_database.py
else
    echo "✅ 数据库已存在"
fi

# 检查端口占用
check_port() {
    local port=$1
    local service=$2
    
    if lsof -i :$port &> /dev/null; then
        echo "⚠️  端口 $port 已被占用 ($service)"
        echo "   请手动停止占用进程或使用其他端口"
        return 1
    fi
    return 0
}

# 检查前端依赖
echo "📦 检查前端依赖..."
if [ ! -d "frontend/node_modules" ]; then
    echo "📥 安装前端依赖..."
    cd frontend
    npm install
    cd ..
else
    echo "✅ 前端依赖已安装"
fi

# 启动后端服务
echo ""
echo "🖥️  启动后端API服务..."

# 寻找可用端口
BACKEND_PORT=8001
while lsof -i :$BACKEND_PORT &> /dev/null; do
    echo "   端口 $BACKEND_PORT 已占用，尝试 $((BACKEND_PORT + 1))"
    BACKEND_PORT=$((BACKEND_PORT + 1))
done

echo "   使用端口: $BACKEND_PORT"

# 启动后端 (后台运行)
API_PORT=$BACKEND_PORT python run_api_server.py &
BACKEND_PID=$!

# 等待后端启动
echo "   等待后端服务启动..."
sleep 3

# 检查后端是否启动成功
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "❌ 后端服务启动失败"
    exit 1
fi

echo "✅ 后端服务已启动 (PID: $BACKEND_PID, 端口: $BACKEND_PORT)"

# 启动前端服务
echo ""
echo "🌐 启动前端服务..."

# 寻找可用端口
FRONTEND_PORT=5173
while lsof -i :$FRONTEND_PORT &> /dev/null; do
    echo "   端口 $FRONTEND_PORT 已占用，尝试 $((FRONTEND_PORT + 1))"
    FRONTEND_PORT=$((FRONTEND_PORT + 1))
done

echo "   使用端口: $FRONTEND_PORT"

# 启动前端 (后台运行)
cd frontend
PORT=$FRONTEND_PORT npm run dev &
FRONTEND_PID=$!
cd ..

# 等待前端启动
echo "   等待前端服务启动..."
sleep 5

# 检查前端是否启动成功
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo "❌ 前端服务启动失败"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo "✅ 前端服务已启动 (PID: $FRONTEND_PID, 端口: $FRONTEND_PORT)"

# 运行服务检查
echo ""
echo "🔍 运行服务状态检查..."
sleep 2
python check_services.py

# 显示服务信息
echo ""
echo "🎉 AuraWell 服务启动完成！"
echo "=================================="
echo "📱 前端界面: http://localhost:$FRONTEND_PORT/"
echo "🔧 后端API: http://127.0.0.1:$BACKEND_PORT/"
echo "📚 API文档: http://127.0.0.1:$BACKEND_PORT/docs"
echo ""
echo "🛑 停止服务:"
echo "   后端PID: $BACKEND_PID"
echo "   前端PID: $FRONTEND_PID"
echo "   停止命令: kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "💡 提示:"
echo "   - 使用 Ctrl+C 停止此脚本"
echo "   - 使用 python check_services.py 检查服务状态"
echo "   - 使用 python database_manager.py status 检查数据库"

# 保存PID到文件
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid

# 等待用户中断
echo ""
echo "⏳ 服务正在运行中... (按 Ctrl+C 停止)"

# 设置信号处理
cleanup() {
    echo ""
    echo "🛑 正在停止服务..."
    
    if [ -f ".backend.pid" ]; then
        BACKEND_PID=$(cat .backend.pid)
        kill $BACKEND_PID 2>/dev/null && echo "✅ 后端服务已停止"
        rm -f .backend.pid
    fi
    
    if [ -f ".frontend.pid" ]; then
        FRONTEND_PID=$(cat .frontend.pid)
        kill $FRONTEND_PID 2>/dev/null && echo "✅ 前端服务已停止"
        rm -f .frontend.pid
    fi
    
    echo "👋 AuraWell 服务已停止"
    exit 0
}

trap cleanup SIGINT SIGTERM

# 保持脚本运行
while true; do
    sleep 1
done
