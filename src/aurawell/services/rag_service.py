"""
RAG Service - 特种突击队
用于与阿里云函数计算RAG模块进行快速、精准的情报获取作战
"""

import json
import logging
from typing import List, Dict, Any, Optional
from fastapi import HTTPException

# 导入统一配置系统
from ..config.settings import get_settings

# 阿里云FC SDK
try:
    from alibabacloud_fc20230330.client import Client as FC20230330Client
    from alibabacloud_fc20230330 import models as fc_20230330_models
    from alibabacloud_tea_openapi import models as open_api_models
    from alibabacloud_credentials.client import Client as CredClient
    from alibabacloud_credentials import models as cred_models
except ImportError as e:
    logging.error(f"阿里云SDK导入失败: {e}")
    FC20230330Client = None

logger = logging.getLogger(__name__)


class RAGService:
    """RAG特种突击队 - 专注于快速、精准的文档检索任务"""

    def __init__(self):
        """初始化突击队装备"""
        self.fc_client = None
        self.config = None
        self.settings = get_settings()
        self._initialize_equipment()
    
    def _initialize_equipment(self):
        """装备检查和初始化"""
        try:
            # 从统一配置系统获取RAG配置
            self.config = self.settings.get_rag_config()

            # 验证必需配置
            if not self.config.get('access_key_id') or not self.config.get('access_key_secret'):
                logger.warning("RAG服务凭证未配置，将在实际调用时报错")
                return

            if not self.config.get('endpoint'):
                logger.warning("RAG服务端点未配置，将在实际调用时报错")
                return

            if FC20230330Client is None:
                logger.error("阿里云SDK未安装，RAG服务不可用")
                return

            # 初始化凭证
            cred_config = cred_models.Config(
                type='access_key',
                access_key_id=self.config['access_key_id'],
                access_key_secret=self.config['access_key_secret']
            )
            cred_client = CredClient(cred_config)

            # 初始化FC客户端
            config = open_api_models.Config(
                credential=cred_client,
                endpoint=f"https://{self.config['endpoint']}"
            )
            self.fc_client = FC20230330Client(config)

            logger.info(f"RAG突击队装备就绪，目标函数: {self.config['function_name']}")

        except Exception as e:
            logger.error(f"RAG突击队装备初始化失败: {e}")
            self.fc_client = None
    
    async def retrieve_from_rag(self, user_query: str, k: int = 3) -> List[str]:
        """
        核心突击任务：从RAG模块检索相关文档
        
        Args:
            user_query: 用户查询（渗透目标）
            k: 返回文档数量（情报份数）
            
        Returns:
            List[str]: 检索到的文档列表（战果）
            
        Raises:
            HTTPException: 任务失败时的标准求救信号
        """
        if not self.fc_client:
            logger.error("RAG突击队装备未就绪")
            raise HTTPException(
                status_code=503, 
                detail="RAG服务暂时不可用，请检查配置"
            )
        
        try:
            # 构造渗透载荷
            payload = {
                "action": "RetrieveTopK",
                "query": {
                    "user_query": user_query,
                    "k": k
                }
            }
            
            logger.info(f"RAG突击开始，目标: {user_query[:50]}...")
            
            # 执行突击任务
            invoke_request = fc_20230330_models.InvokeFunctionRequest(
                body=json.dumps(payload).encode('utf-8')
            )
            
            response = self.fc_client.invoke_function(self.config['function_name'], invoke_request)
            
            # 解析战果
            if response.status_code != 200:
                logger.error(f"RAG突击失败，状态码: {response.status_code}")
                raise HTTPException(
                    status_code=502,
                    detail=f"RAG服务响应异常: {response.status_code}"
                )
            
            # 解析响应体
            response_body = response.body.decode('utf-8')
            response_data = json.loads(response_body)
            
            # 提取核心情报
            if response_data.get('statusCode') == 200:
                results = response_data.get('results', [])
                logger.info(f"RAG突击成功，获得情报 {len(results)} 份")
                return results
            else:
                error_msg = response_data.get('body', '未知错误')
                logger.error(f"RAG函数执行失败: {error_msg}")
                raise HTTPException(
                    status_code=502,
                    detail=f"RAG检索失败: {error_msg}"
                )
                
        except HTTPException:
            # 重新抛出HTTP异常
            raise
        except Exception as e:
            logger.error(f"RAG突击遭遇意外情况: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"RAG服务内部错误: {str(e)}"
            )
    
    def health_check(self) -> bool:
        """装备状态检查"""
        return self.fc_client is not None
    
    def get_status(self) -> Dict[str, Any]:
        """获取突击队状态报告"""
        return {
            "service_ready": self.health_check(),
            "endpoint": self.config.get('endpoint') if self.config else None,
            "function_name": self.config.get('function_name') if self.config else None,
            "sdk_available": FC20230330Client is not None,
            "config_loaded": self.config is not None,
            "timeout": self.config.get('timeout') if self.config else None,
            "max_retries": self.config.get('max_retries') if self.config else None
        }


# 全局突击队实例
_rag_service_instance = None


def get_rag_service() -> RAGService:
    """获取RAG突击队实例（单例模式）"""
    global _rag_service_instance
    if _rag_service_instance is None:
        _rag_service_instance = RAGService()
    return _rag_service_instance
