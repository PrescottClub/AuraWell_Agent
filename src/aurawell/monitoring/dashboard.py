"""
AuraWell监控仪表板
基于FastAPI的Web监控界面，展示系统性能指标和健康状态
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

# 项目内部导入
try:
    from ..database import get_database_manager
    from ..core.deepseek_client import DeepSeekClient
    from .performance_monitor import PerformanceMonitor
except ImportError:
    # 开发环境下的导入处理
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent.parent.parent))

logger = logging.getLogger(__name__)


class MonitoringDashboard:
    """监控仪表板主类"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8001):
        self.host = host
        self.port = port
        self.app = FastAPI(
            title="AuraWell监控仪表板",
            description="系统性能监控和健康状态展示",
            version="1.0.0"
        )
        self.performance_monitor = PerformanceMonitor()
        self._setup_routes()
        self._setup_static_files()
    
    def _setup_static_files(self):
        """设置静态文件服务"""
        # 创建静态文件目录
        static_dir = Path(__file__).parent / "static"
        static_dir.mkdir(exist_ok=True)
        
        # 创建模板目录
        templates_dir = Path(__file__).parent / "templates"
        templates_dir.mkdir(exist_ok=True)
        
        # 如果目录存在，挂载静态文件
        if static_dir.exists():
            self.app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
        
        self.templates = Jinja2Templates(directory=str(templates_dir))
    
    def _setup_routes(self):
        """设置路由"""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def dashboard_home(request: Request):
            """仪表板首页"""
            try:
                # 获取系统概览数据
                overview_data = await self._get_system_overview()
                
                # 渲染仪表板页面
                return self._render_dashboard_html(overview_data)
                
            except Exception as e:
                logger.error(f"仪表板首页加载失败: {e}")
                return HTMLResponse(
                    content=self._render_error_page(str(e)),
                    status_code=500
                )
        
        @self.app.get("/api/metrics")
        async def get_metrics():
            """获取系统指标API"""
            try:
                metrics = await self._collect_all_metrics()
                return JSONResponse(content=metrics)
            except Exception as e:
                logger.error(f"指标收集失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/health")
        async def health_check():
            """健康检查API"""
            try:
                health_status = await self._check_system_health()
                return JSONResponse(content=health_status)
            except Exception as e:
                logger.error(f"健康检查失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/performance")
        async def get_performance_data():
            """获取性能数据API"""
            try:
                performance_data = await self.performance_monitor.get_performance_summary()
                return JSONResponse(content=performance_data)
            except Exception as e:
                logger.error(f"性能数据获取失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/logs")
        async def get_recent_logs(limit: int = 100):
            """获取最近日志API"""
            try:
                logs = await self._get_recent_logs(limit)
                return JSONResponse(content=logs)
            except Exception as e:
                logger.error(f"日志获取失败: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    
    async def _get_system_overview(self) -> Dict[str, Any]:
        """获取系统概览数据"""
        try:
            # 数据库连接状态
            db_status = await self._check_database_connection()
            
            # AI模型状态
            ai_status = await self._check_ai_model_status()
            
            # 性能指标
            performance_metrics = await self.performance_monitor.get_current_metrics()
            
            # 用户统计
            user_stats = await self._get_user_statistics()
            
            return {
                "timestamp": datetime.now().isoformat(),
                "database": db_status,
                "ai_model": ai_status,
                "performance": performance_metrics,
                "users": user_stats,
                "system_uptime": self._get_system_uptime()
            }
            
        except Exception as e:
            logger.error(f"系统概览数据获取失败: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}
    
    async def _check_database_connection(self) -> Dict[str, Any]:
        """检查数据库连接状态"""
        try:
            db_manager = get_database_manager()
            
            # 执行简单查询测试连接
            async with db_manager.get_session() as session:
                result = await session.execute("SELECT 1")
                result.fetchone()
            
            return {
                "status": "healthy",
                "message": "数据库连接正常",
                "last_check": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"数据库连接失败: {e}",
                "last_check": datetime.now().isoformat()
            }
    
    async def _check_ai_model_status(self) -> Dict[str, Any]:
        """检查AI模型状态"""
        try:
            client = DeepSeekClient()
            
            # 发送测试请求
            test_response = await client.chat_completion(
                messages=[{"role": "user", "content": "健康检查"}],
                max_tokens=10
            )
            
            return {
                "status": "healthy",
                "message": "AI模型响应正常",
                "model": client.model,
                "last_check": datetime.now().isoformat(),
                "test_response_length": len(test_response.get("content", ""))
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"AI模型检查失败: {e}",
                "last_check": datetime.now().isoformat()
            }
    
    async def _get_user_statistics(self) -> Dict[str, Any]:
        """获取用户统计信息"""
        try:
            db_manager = get_database_manager()
            
            async with db_manager.get_session() as session:
                # 总用户数
                total_users_result = await session.execute("SELECT COUNT(*) FROM user_profiles")
                total_users = total_users_result.scalar()
                
                # 活跃用户数（最近7天有活动）
                seven_days_ago = datetime.now() - timedelta(days=7)
                active_users_result = await session.execute(
                    "SELECT COUNT(DISTINCT user_id) FROM activity_summaries WHERE date >= ?",
                    [seven_days_ago.date()]
                )
                active_users = active_users_result.scalar()
                
                return {
                    "total_users": total_users or 0,
                    "active_users_7d": active_users or 0,
                    "last_updated": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"用户统计获取失败: {e}")
            return {
                "total_users": 0,
                "active_users_7d": 0,
                "error": str(e),
                "last_updated": datetime.now().isoformat()
            }
    
    def _get_system_uptime(self) -> str:
        """获取系统运行时间"""
        # 简化实现，返回当前时间
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    async def _collect_all_metrics(self) -> Dict[str, Any]:
        """收集所有系统指标"""
        return {
            "system_overview": await self._get_system_overview(),
            "performance_metrics": await self.performance_monitor.get_performance_summary(),
            "timestamp": datetime.now().isoformat()
        }
    
    async def _check_system_health(self) -> Dict[str, Any]:
        """检查系统整体健康状态"""
        health_checks = {
            "database": await self._check_database_connection(),
            "ai_model": await self._check_ai_model_status(),
        }
        
        # 计算整体健康状态
        healthy_services = sum(1 for check in health_checks.values() if check["status"] == "healthy")
        total_services = len(health_checks)
        
        overall_status = "healthy" if healthy_services == total_services else "degraded"
        if healthy_services == 0:
            overall_status = "critical"
        
        return {
            "overall_status": overall_status,
            "healthy_services": healthy_services,
            "total_services": total_services,
            "services": health_checks,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _get_recent_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取最近的日志记录"""
        try:
            # 读取日志文件
            log_file = Path("logs/aurawell.log")
            if not log_file.exists():
                return []
            
            # 读取最后N行
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 返回最近的日志行
            recent_lines = lines[-limit:] if len(lines) > limit else lines
            
            logs = []
            for i, line in enumerate(recent_lines):
                logs.append({
                    "id": i,
                    "timestamp": datetime.now().isoformat(),  # 简化实现
                    "message": line.strip(),
                    "level": "INFO"  # 简化实现
                })
            
            return logs
            
        except Exception as e:
            logger.error(f"日志读取失败: {e}")
            return [{"error": str(e), "timestamp": datetime.now().isoformat()}]
    
    def _render_dashboard_html(self, data: Dict[str, Any]) -> str:
        """渲染仪表板HTML页面"""
        html_template = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AuraWell监控仪表板</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
        .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
        .metric-card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .metric-title {{ font-size: 18px; font-weight: bold; margin-bottom: 10px; color: #333; }}
        .metric-value {{ font-size: 24px; font-weight: bold; color: #667eea; }}
        .status-healthy {{ color: #28a745; }}
        .status-error {{ color: #dc3545; }}
        .refresh-btn {{ background: #667eea; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; }}
        .refresh-btn:hover {{ background: #5a6fd8; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏥 AuraWell监控仪表板</h1>
            <p>系统健康状态实时监控 | 最后更新: {data.get('timestamp', 'N/A')}</p>
            <button class="refresh-btn" onclick="location.reload()">🔄 刷新数据</button>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-title">📊 数据库状态</div>
                <div class="metric-value {'status-healthy' if data.get('database', {}).get('status') == 'healthy' else 'status-error'}">
                    {data.get('database', {}).get('status', 'unknown').upper()}
                </div>
                <p>{data.get('database', {}).get('message', 'N/A')}</p>
            </div>
            
            <div class="metric-card">
                <div class="metric-title">🤖 AI模型状态</div>
                <div class="metric-value {'status-healthy' if data.get('ai_model', {}).get('status') == 'healthy' else 'status-error'}">
                    {data.get('ai_model', {}).get('status', 'unknown').upper()}
                </div>
                <p>{data.get('ai_model', {}).get('message', 'N/A')}</p>
            </div>
            
            <div class="metric-card">
                <div class="metric-title">👥 用户统计</div>
                <div class="metric-value">{data.get('users', {}).get('total_users', 0)}</div>
                <p>总用户数 | 活跃用户(7天): {data.get('users', {}).get('active_users_7d', 0)}</p>
            </div>
            
            <div class="metric-card">
                <div class="metric-title">⏱️ 系统运行时间</div>
                <div class="metric-value">运行中</div>
                <p>{data.get('system_uptime', 'N/A')}</p>
            </div>
        </div>
        
        <div style="margin-top: 20px; text-align: center; color: #666;">
            <p>📡 API端点: <a href="/api/metrics">/api/metrics</a> | <a href="/api/health">/api/health</a> | <a href="/api/performance">/api/performance</a></p>
        </div>
    </div>
    
    <script>
        // 自动刷新功能
        setInterval(() => {{
            fetch('/api/health')
                .then(response => response.json())
                .then(data => {{
                    console.log('健康检查更新:', data);
                }})
                .catch(error => console.error('健康检查失败:', error));
        }}, 30000); // 每30秒检查一次
    </script>
</body>
</html>
"""
        return html_template
    
    def _render_error_page(self, error_message: str) -> str:
        """渲染错误页面"""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>AuraWell监控仪表板 - 错误</title>
    <style>
        body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
        .error {{ color: #dc3545; font-size: 18px; }}
    </style>
</head>
<body>
    <h1>🚨 监控仪表板错误</h1>
    <div class="error">{error_message}</div>
    <p><a href="/">返回首页</a></p>
</body>
</html>
"""
    
    async def start_server(self):
        """启动监控服务器"""
        logger.info(f"🚀 启动AuraWell监控仪表板: http://{self.host}:{self.port}")
        
        config = uvicorn.Config(
            app=self.app,
            host=self.host,
            port=self.port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()


# 便捷启动函数
async def start_monitoring_dashboard(host: str = "0.0.0.0", port: int = 8001):
    """启动监控仪表板"""
    dashboard = MonitoringDashboard(host, port)
    await dashboard.start_server()


if __name__ == "__main__":
    # 直接运行监控仪表板
    asyncio.run(start_monitoring_dashboard())
