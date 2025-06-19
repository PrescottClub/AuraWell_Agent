"""
这是阿里云FC函数调用的入口文件, 为了方便本地测试, 其需要调用位于本文件同级文件夹的requirements.txt
而多个requirements.txt可能会对项目的维护造成不必要的困难, 所以它不会被上传到Github上, 如需要测试, 请按照以下提示自行创建
alibabacloud-docmind-api20220711>=1.4.3
alibabacloud-credentials>1.0.0
dashvector>=1.0.19
openai>=1.60.1
numpy>=1.24.1
python-dotenv==1.1.0
"""

import os
import json
from RAGExtension import Document, UserRetrieve


def handler(event, context):
    """
    FC函数入口，根据传入的参数调用RAGExtension.py中对外暴露的方法

    Args:
        event: 包含调用参数的字典，格式为：
            {
                "action": "FileExport/FileAnalysation/RetrieveTopK",
                "query": {
                    # 根据不同action包含不同参数
                }
            }
        context: 函数计算上下文对象

    Returns:
        dict: 包含状态码和结果的字典
    """
    try:
        # 解析事件参数
        event_data = json.loads(event)
        action = event_data.get("action")
        query_params = event_data.get("query", {})

        # 执行对应操作
        if action == "FileExport":
            file_path = query_params.get("file_path")
            if not file_path:
                return {"statusCode": 400, "body": "缺少 file_path 参数"}

            doc = Document()
            result = doc.file_Parsing(file_path)

            # 将结果写入临时文件（FC环境限制）
            output_path = "/tmp/parsed_content.md"
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(result)

            return {
                "statusCode": 200,
                "body": "文件解析成功",
                "output_file": output_path
            }

        elif action == "FileAnalysation":
            file_path = query_params.get("file_path")
            if not file_path:
                return {"statusCode": 400, "body": "缺少 file_path 参数"}

            doc = Document()
            success = doc.file2VectorDB(file_path)

            if success:
                return {"statusCode": 200, "body": "文件已成功存入向量数据库"}
            else:
                return {"statusCode": 500, "body": "文件存入向量数据库失败"}

        elif action == "RetrieveTopK":
            user_query = query_params.get("user_query")
            k = query_params.get("k", 5)

            if not user_query:
                return {"statusCode": 400, "body": "缺少 user_query 参数"}

            if not isinstance(k, int) or k <= 0:
                return {"statusCode": 400, "body": "k 参数必须为正整数"}

            retriever = UserRetrieve()
            results = retriever.retrieve_topK(user_query, k)

            return {
                "statusCode": 200,
                "body": "检索成功",
                "results": results
            }

        else:
            return {"statusCode": 400, "body": "无效的 action 参数"}

    except Exception as e:
        return {"statusCode": 500, "body": f"发生错误: {str(e)}"}

