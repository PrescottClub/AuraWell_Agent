#!/bin/bash

# AuraWell 服务停止脚本
# 用于停止所有运行中的前后端服务

echo "🛑 停止 AuraWell 健康管理系统"
echo "=================================="

# 停止通过PID文件记录的服务
stop_by_pid() {
    local pid_file=$1
    local service_name=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null
            echo "✅ $service_name 已停止 (PID: $pid)"
        else
            echo "⚠️  $service_name 进程不存在 (PID: $pid)"
        fi
        rm -f "$pid_file"
    else
        echo "ℹ️  未找到 $service_name 的PID文件"
    fi
}

# 停止指定端口的服务
stop_by_port() {
    local port=$1
    local service_name=$2
    
    local pids=$(lsof -ti :$port 2>/dev/null)
    if [ -n "$pids" ]; then
        echo "🔍 发现 $service_name 在端口 $port 运行"
        for pid in $pids; do
            kill $pid 2>/dev/null
            echo "✅ 已停止进程 $pid"
        done
    else
        echo "ℹ️  端口 $port 没有运行的 $service_name"
    fi
}

# 停止PID文件记录的服务
echo "📋 检查PID文件..."
stop_by_pid ".backend.pid" "后端服务"
stop_by_pid ".frontend.pid" "前端服务"

# 停止常用端口的服务
echo ""
echo "🔍 检查常用端口..."

# 检查后端常用端口
for port in 8000 8001 8002 8003; do
    stop_by_port $port "后端服务"
done

# 检查前端常用端口
for port in 3000 5173 5174 5175; do
    stop_by_port $port "前端服务"
done

# 停止特定的Python和Node进程
echo ""
echo "🔍 检查特定进程..."

# 停止运行API服务器的Python进程
api_pids=$(ps aux | grep "run_api_server.py" | grep -v grep | awk '{print $2}')
if [ -n "$api_pids" ]; then
    echo "🔍 发现API服务器进程"
    for pid in $api_pids; do
        kill $pid 2>/dev/null
        echo "✅ 已停止API服务器进程 $pid"
    done
else
    echo "ℹ️  未发现API服务器进程"
fi

# 停止前端开发服务器
vite_pids=$(ps aux | grep "vite" | grep -v grep | awk '{print $2}')
if [ -n "$vite_pids" ]; then
    echo "🔍 发现Vite开发服务器进程"
    for pid in $vite_pids; do
        kill $pid 2>/dev/null
        echo "✅ 已停止Vite进程 $pid"
    done
else
    echo "ℹ️  未发现Vite开发服务器进程"
fi

# 清理临时文件
echo ""
echo "🧹 清理临时文件..."
rm -f .backend.pid .frontend.pid
echo "✅ 临时文件已清理"

# 最终检查
echo ""
echo "🔍 最终状态检查..."

# 检查是否还有相关进程
remaining_processes=0

for port in 8000 8001 8002 8003 5173 5174 5175 3000; do
    if lsof -i :$port &> /dev/null; then
        echo "⚠️  端口 $port 仍有进程运行"
        remaining_processes=1
    fi
done

if [ $remaining_processes -eq 0 ]; then
    echo "✅ 所有AuraWell服务已成功停止"
else
    echo "⚠️  部分服务可能仍在运行，请手动检查"
    echo ""
    echo "💡 手动检查命令:"
    echo "   lsof -i :8001  # 检查后端"
    echo "   lsof -i :5173  # 检查前端"
    echo "   ps aux | grep run_api_server.py"
    echo "   ps aux | grep vite"
fi

echo ""
echo "👋 AuraWell 服务停止完成！"
