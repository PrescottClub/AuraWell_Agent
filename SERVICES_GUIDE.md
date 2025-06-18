# AuraWell 服务管理指南

## 🎯 概述

AuraWell 健康管理系统包含前端和后端两个主要服务，本指南提供了完整的服务管理方法。

## 🚀 快速启动

### 方法一：使用启动脚本（推荐）

```bash
# 启动所有服务
./start_services.sh

# 停止所有服务
./stop_services.sh
```

### 方法二：手动启动

```bash
# 1. 启动后端服务
API_PORT=8001 python run_api_server.py

# 2. 启动前端服务（新终端）
cd frontend
npm run dev
```

## 📊 服务信息

### 后端API服务
- **端口**: 8001 (默认)
- **地址**: http://127.0.0.1:8001/
- **API文档**: http://127.0.0.1:8001/docs
- **健康检查**: http://127.0.0.1:8001/api/v1/health

### 前端服务
- **端口**: 5173 (默认)
- **地址**: http://localhost:5173/
- **技术栈**: Vue 3 + Vite

### 数据库
- **类型**: SQLite
- **文件**: aurawell.db
- **表数量**: 17个表
- **支持**: 异步操作

## 🛠️ 管理工具

### 1. 服务状态检查
```bash
python check_services.py
```

功能：
- ✅ 检查前后端服务状态
- ✅ 测试数据库连接
- ✅ 验证API端点
- ✅ 显示详细状态信息

### 2. 数据库管理
```bash
# 查看数据库状态
python database_manager.py status

# 备份数据库
python database_manager.py backup

# 查看表数据
python database_manager.py show user_profiles 5

# 导出数据库结构
python database_manager.py export schema.json

# 重置数据库（谨慎使用）
python database_manager.py reset
```

### 3. 数据库初始化
```bash
python init_database.py
```

功能：
- 🔧 创建数据库表结构
- 🔍 验证数据库完整性
- 💾 自动备份现有数据
- 📊 显示初始化结果

## 🔧 配置文件

### 环境配置 (.env)
```env
# 数据库配置
DATABASE_URL=sqlite+aiosqlite:///./aurawell.db

# DeepSeek AI配置
DEEPSEEK_API_KEY=your_api_key_here

# 应用配置
DEBUG=True
LOG_LEVEL=INFO
```

### 前端配置 (frontend/package.json)
- 开发服务器端口：5173
- 构建工具：Vite
- 框架：Vue 3

## 🚨 故障排除

### 常见问题

#### 1. 端口被占用
```bash
# 查看端口占用
lsof -i :8001  # 后端
lsof -i :5173  # 前端

# 停止占用进程
kill <PID>
```

#### 2. 数据库连接失败
```bash
# 检查数据库文件
ls -la aurawell.db

# 重新初始化数据库
python init_database.py
```

#### 3. 前端依赖问题
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

#### 4. 后端启动失败
```bash
# 检查Python环境
python --version

# 检查依赖
pip list | grep fastapi
pip list | grep sqlalchemy

# 查看详细错误
python run_api_server.py
```

### 日志查看

#### 后端日志
- 控制台输出：实时显示API请求和错误
- 日志级别：INFO（可在.env中配置）

#### 前端日志
- 浏览器控制台：开发者工具 → Console
- 网络请求：开发者工具 → Network

## 📈 性能监控

### 系统性能
```bash
# 查看系统性能指标
curl http://127.0.0.1:8001/api/v1/system/performance
```

### 数据库性能
```bash
# 查看数据库状态
python database_manager.py status
```

## 🔒 安全注意事项

### 开发环境
- ✅ 使用本地数据库
- ✅ API密钥通过环境变量配置
- ✅ 调试模式仅在开发环境启用

### 生产环境建议
- 🔐 使用HTTPS
- 🔐 配置防火墙规则
- 🔐 定期备份数据库
- 🔐 监控系统资源

## 📝 开发工作流

### 1. 日常开发
```bash
# 启动开发环境
./start_services.sh

# 检查服务状态
python check_services.py

# 开发完成后停止服务
./stop_services.sh
```

### 2. 数据库变更
```bash
# 备份现有数据
python database_manager.py backup

# 应用变更
python init_database.py

# 验证变更
python database_manager.py status
```

### 3. 测试
```bash
# 运行后端测试
pytest tests/

# 运行前端测试
cd frontend
npm test
```

## 🎉 总结

AuraWell 提供了完整的服务管理工具链：

✅ **一键启动/停止** - 使用脚本快速管理服务
✅ **状态监控** - 实时检查服务健康状态  
✅ **数据库管理** - 完整的数据库操作工具
✅ **故障排除** - 详细的问题诊断指南
✅ **性能监控** - 系统性能指标查看

通过这些工具，您可以轻松管理和维护AuraWell健康管理系统！
