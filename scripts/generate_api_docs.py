#!/usr/bin/env python3
"""
AuraWell API文档自动生成脚本
基于FastAPI的OpenAPI规范生成静态HTML文档
"""

import json
import os
import sys
import asyncio
from pathlib import Path
from typing import Dict, Any

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

try:
    from fastapi import FastAPI
    from fastapi.openapi.utils import get_openapi
    import uvicorn
except ImportError:
    print("❌ 缺少依赖包，请安装: pip install fastapi uvicorn")
    sys.exit(1)


class APIDocGenerator:
    """API文档生成器"""
    
    def __init__(self, output_dir: str = "docs/api"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def create_fastapi_app(self) -> FastAPI:
        """创建FastAPI应用实例用于文档生成"""
        app = FastAPI(
            title="AuraWell API",
            description="AuraWell智能健康助手API文档",
            version="3.0.0",
            docs_url="/docs",
            redoc_url="/redoc"
        )
        
        # 导入并注册所有路由
        try:
            from aurawell.api.routes import health, auth, conversation, family
            
            app.include_router(health.router, prefix="/api/v1/health", tags=["健康管理"])
            app.include_router(auth.router, prefix="/api/v1/auth", tags=["用户认证"])
            app.include_router(conversation.router, prefix="/api/v1/conversation", tags=["对话管理"])
            app.include_router(family.router, prefix="/api/v1/family", tags=["家庭管理"])
            
        except ImportError as e:
            print(f"⚠️ 部分路由模块导入失败: {e}")
            # 创建示例路由用于文档生成
            self._create_example_routes(app)
            
        return app
    
    def _create_example_routes(self, app: FastAPI):
        """创建示例路由用于文档生成"""
        from fastapi import APIRouter
        from pydantic import BaseModel
        
        # 健康管理路由示例
        health_router = APIRouter()
        
        class HealthAdviceRequest(BaseModel):
            message: str
            user_id: str
            context: Dict[str, Any] = {}
        
        class HealthAdviceResponse(BaseModel):
            success: bool
            advice: str
            recommendations: list
            
        @health_router.post("/advice", response_model=HealthAdviceResponse)
        async def get_health_advice(request: HealthAdviceRequest):
            """获取个性化健康建议"""
            pass
            
        @health_router.get("/metrics/{user_id}")
        async def get_health_metrics(user_id: str):
            """获取用户健康指标"""
            pass
            
        # 用户认证路由示例
        auth_router = APIRouter()
        
        class LoginRequest(BaseModel):
            username: str
            password: str
            
        @auth_router.post("/login")
        async def login(request: LoginRequest):
            """用户登录"""
            pass
            
        @auth_router.post("/logout")
        async def logout():
            """用户登出"""
            pass
            
        # 对话管理路由示例
        conversation_router = APIRouter()
        
        @conversation_router.get("/history/{user_id}")
        async def get_conversation_history(user_id: str, limit: int = 50):
            """获取对话历史"""
            pass
            
        @conversation_router.post("/message")
        async def send_message(message: str, user_id: str):
            """发送消息"""
            pass
            
        # 注册路由
        app.include_router(health_router, prefix="/api/v1/health", tags=["健康管理"])
        app.include_router(auth_router, prefix="/api/v1/auth", tags=["用户认证"])
        app.include_router(conversation_router, prefix="/api/v1/conversation", tags=["对话管理"])
    
    def generate_openapi_spec(self, app: FastAPI) -> Dict[str, Any]:
        """生成OpenAPI规范"""
        return get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )
    
    def save_openapi_json(self, openapi_spec: Dict[str, Any]):
        """保存OpenAPI JSON文件"""
        json_file = self.output_dir / "openapi.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(openapi_spec, f, ensure_ascii=False, indent=2)
        print(f"✅ OpenAPI JSON已保存到: {json_file}")
    
    def generate_html_docs(self, openapi_spec: Dict[str, Any]):
        """生成HTML文档"""
        # Swagger UI HTML模板
        swagger_html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>AuraWell API Documentation</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui.css" />
    <style>
        html {{
            box-sizing: border-box;
            overflow: -moz-scrollbars-vertical;
            overflow-y: scroll;
        }}
        *, *:before, *:after {{
            box-sizing: inherit;
        }}
        body {{
            margin:0;
            background: #fafafa;
        }}
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui-bundle.js"></script>
    <script src="https://unpkg.com/swagger-ui-dist@4.15.5/swagger-ui-standalone-preset.js"></script>
    <script>
        window.onload = function() {{
            const ui = SwaggerUIBundle({{
                spec: {json.dumps(openapi_spec, ensure_ascii=False)},
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "StandaloneLayout"
            }});
        }};
    </script>
</body>
</html>
"""
        
        # 保存Swagger UI HTML
        swagger_file = self.output_dir / "swagger.html"
        with open(swagger_file, 'w', encoding='utf-8') as f:
            f.write(swagger_html)
        print(f"✅ Swagger UI文档已保存到: {swagger_file}")
        
        # ReDoc HTML模板
        redoc_html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>AuraWell API Documentation - ReDoc</title>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
    <style>
        body {{
            margin: 0;
            padding: 0;
        }}
    </style>
</head>
<body>
    <redoc spec-url="data:application/json;base64,{self._encode_spec_base64(openapi_spec)}"></redoc>
    <script src="https://cdn.jsdelivr.net/npm/redoc@2.0.0/bundles/redoc.standalone.js"></script>
</body>
</html>
"""
        
        # 保存ReDoc HTML
        redoc_file = self.output_dir / "redoc.html"
        with open(redoc_file, 'w', encoding='utf-8') as f:
            f.write(redoc_html)
        print(f"✅ ReDoc文档已保存到: {redoc_file}")
    
    def _encode_spec_base64(self, spec: Dict[str, Any]) -> str:
        """将OpenAPI规范编码为base64"""
        import base64
        spec_json = json.dumps(spec, ensure_ascii=False)
        return base64.b64encode(spec_json.encode('utf-8')).decode('utf-8')
    
    def generate_postman_collection(self, openapi_spec: Dict[str, Any]):
        """生成Postman集合"""
        # 简化的Postman集合生成
        collection = {
            "info": {
                "name": "AuraWell API",
                "description": "AuraWell智能健康助手API集合",
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
            },
            "item": []
        }
        
        # 从OpenAPI规范提取路径并转换为Postman请求
        for path, methods in openapi_spec.get("paths", {}).items():
            for method, details in methods.items():
                if method.upper() in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                    item = {
                        "name": details.get("summary", f"{method.upper()} {path}"),
                        "request": {
                            "method": method.upper(),
                            "header": [],
                            "url": {
                                "raw": f"{{{{base_url}}}}{path}",
                                "host": ["{{base_url}}"],
                                "path": path.strip("/").split("/")
                            }
                        }
                    }
                    collection["item"].append(item)
        
        # 保存Postman集合
        postman_file = self.output_dir / "AuraWell_API.postman_collection.json"
        with open(postman_file, 'w', encoding='utf-8') as f:
            json.dump(collection, f, ensure_ascii=False, indent=2)
        print(f"✅ Postman集合已保存到: {postman_file}")
    
    def generate_all_docs(self):
        """生成所有文档格式"""
        print("🚀 开始生成AuraWell API文档...")
        
        # 创建FastAPI应用
        app = self.create_fastapi_app()
        
        # 生成OpenAPI规范
        openapi_spec = self.generate_openapi_spec(app)
        
        # 保存各种格式的文档
        self.save_openapi_json(openapi_spec)
        self.generate_html_docs(openapi_spec)
        self.generate_postman_collection(openapi_spec)
        
        print(f"\n📚 文档生成完成！输出目录: {self.output_dir.absolute()}")
        print("📖 可用文档格式:")
        print(f"   - OpenAPI JSON: {self.output_dir}/openapi.json")
        print(f"   - Swagger UI: {self.output_dir}/swagger.html")
        print(f"   - ReDoc: {self.output_dir}/redoc.html")
        print(f"   - Postman集合: {self.output_dir}/AuraWell_API.postman_collection.json")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AuraWell API文档生成器")
    parser.add_argument("--output", "-o", default="docs/api", help="输出目录 (默认: docs/api)")
    parser.add_argument("--format", "-f", choices=["all", "json", "html", "postman"], 
                       default="all", help="生成格式 (默认: all)")
    
    args = parser.parse_args()
    
    # 创建文档生成器
    generator = APIDocGenerator(args.output)
    
    if args.format == "all":
        generator.generate_all_docs()
    else:
        app = generator.create_fastapi_app()
        openapi_spec = generator.generate_openapi_spec(app)
        
        if args.format == "json":
            generator.save_openapi_json(openapi_spec)
        elif args.format == "html":
            generator.generate_html_docs(openapi_spec)
        elif args.format == "postman":
            generator.generate_postman_collection(openapi_spec)


if __name__ == "__main__":
    main()
