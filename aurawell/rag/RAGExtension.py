"""
增强检索方法，通过向量相似度查找，检索数据库中前K个和用户查询相关的字段，也提供将文档解析并上传至向量数据库的方法
该拓展使用阿里巴巴提供的云服务，使用前请务必通过pip命令安装好对应的库
目前通过.env解析密钥，未来将通过KMS密钥管理系统解析密钥
"""
from typing import Any
from rag_utils import get_file_type, process_list
from alibabacloud_docmind_api20220711.client import Client as docmind_api20220711Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_docmind_api20220711 import models as docmind_api20220711_models
from alibabacloud_tea_util.client import Client as UtilClient
from alibabacloud_tea_util import models as util_models
from alibabacloud_credentials.client import Client as CredClient
from alibabacloud_credentials.client import Client as CredentialsClient
from alibabacloud_credentials.models import Config as CredentialsConfig
from dashvector import Doc
from numpy.f2py.crackfortran import dimensionpattern
from openai import OpenAI
from dotenv import load_dotenv
import os
import time
import re
import dashvector
import numpy as np

class Document:
    def __init__(self):
        """
        从项目的根目录处加载.env文件，这个类需要读取的api key有：
        ALIBABA_CLOUD_ACCESS_KEY_ID=SECRET
        ALIBABA_CLOUD_ACCESS_KEY_SECRET=SECRET
        DASHSCOPE_API_KEY=SECRET
        正式部署时不能从.env文件中读取密钥，而是通过阿里巴巴的密钥管理系统管理密钥
        """
        # 获取当前文件的绝对路径
        current_file_path = os.path.abspath(__file__)
        # 获取当前文件所在目录（即 aurawell/rag）
        current_dir = os.path.dirname(current_file_path)
        # 获取项目根目录
        project_root = os.path.dirname(os.path.dirname(current_dir))
        # 构建 .env 文件的完整路径
        dotenv_path = os.path.join(project_root, '.env')
        # 加载指定路径下的 .env 文件
        load_dotenv(dotenv_path=dotenv_path)
        self.access_key_id = os.getenv("ALIBABA_CLOUD_ACCESS_KEY_ID")
        self.access_key_secret = os.getenv("ALIBABA_CLOUD_ACCESS_KEY_SECRET")
        self.dash_scope_key = os.getenv("DASHSCOPE_API_KEY")
        self.dash_vector_key = os.getenv("DASH_VECTOR_API")

        # 访问的域名
        # 阿里云docmind服务的节点地址，写成类属性是为了方便未来更换
        self.docmind_endpoint = f'docmind-api.cn-hangzhou.aliyuncs.com'
        # 阿里云的向量数据库服务的节点地址
        self.vectorDB_endpoint = "vrs-cn-6sa4axaiv0001c.dashvector.cn-shanghai.aliyuncs.com"
        self.bailian_endpoint = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    def __doc_analysation(self, file_path:str):
        """
        使用阿里云的docmind服务对文档进行解析，返回解析结果
        :param file_path: 文档路径
        :return: 解析结果
        """
        # 构造 Credential，直接从本地读取，在正式部署时需要更改
        cred_config = CredentialsConfig(
            type="access_key",
            access_key_id=self.access_key_id,
            access_key_secret=self.access_key_secret
        )
        # 加载完毕，现在可以初始化类
        cred = CredClient(config=cred_config)
        config = open_api_models.Config(
            # 通过credentials获取配置中的AccessKey ID
            access_key_id=cred.get_credential().get_access_key_id(),
            # 通过credentials获取配置中的AccessKey Secret
            access_key_secret=cred.get_credential().get_access_key_secret()
        )
        client = docmind_api20220711Client(config)
        config.endpoint = self.docmind_endpoint
        request = docmind_api20220711_models.SubmitDocParserJobAdvanceRequest(
            # file_url_object : 本地文件流
            file_url_object=open(file_path, "rb"),
            # 文档类型是必须上传的参数
            file_name_extension=get_file_type(file_path)
        )
        runtime = util_models.RuntimeOptions()
        response = client.submit_doc_parser_job_advance(request, runtime)
        job_id = response.body.data.id
        request = docmind_api20220711_models.QueryDocParserStatusRequest(
            # id :  任务提交接口返回的id
            id=job_id
        )
        response = client.query_doc_parser_status(request)
        service_status = response.body.data.status
        wait_time = 0.0 # 目前没有想到一个合适的检测超时的办法，先就这么将就一下吧
        while service_status != "success" and wait_time < 60:
            time.sleep(0.5)
            wait_time += 0.5
            response = client.query_doc_parser_status(request)
            service_status = response.body.data.status
        request = docmind_api20220711_models.GetDocParserResultRequest(
            # id :  任务提交接口返回的id
            id=job_id,
            layout_step_size=100,
            layout_num=0
        )
        # 复制代码运行请自行打印 API 的返回值
        response = client.get_doc_parser_result(request)
        # API返回值格式层级为 body -> data -> 具体属性。可根据业务需要打印相应的结果。获取属性值均以小写开头
        # 获取返回结果。建议先把response.body.data转成json，然后再从json里面取具体需要的值。
        print(response.body)
        return response.body.data
    def file_Parsing(self, file_path:str)->str:
        """
        从阿里云 DocMind API 返回的 data 字段中提取所有 markdownContent，
        拼接成一个完整的 Markdown 字符串，并：
        - 去除空白行
        - 合并连续的文本块
        """
        raw_text = self.__doc_analysation(file_path)
        full_markdown = ""
        layouts = raw_text.get("layouts",  []) if raw_text.get("layouts",  None) is not None else []
        for layout in layouts:
            markdown = layout.get("markdownContent", None) if layout.get("markdownContent", None) is not None else ""
            full_markdown += markdown
        # 按行分割
        lines = full_markdown.splitlines()
        cleaned_lines = []
        buffer = ""
        for line in lines:
            stripped_line = line.strip()
            if stripped_line == "":  # 空行
                if buffer:
                    cleaned_lines.append(buffer)
                    buffer = ""
            else:
                buffer += " " + stripped_line if buffer else stripped_line
        # 添加最后可能存在的段落
        if buffer:
            cleaned_lines.append(buffer)
        return "\n".join(cleaned_lines)
    def __content_vectorised(self, raw_content):
        # raw_content 对应的是文档解析方法返回的 response.body.data
        discard_type = () # 返回值中，忽略其中type对应的值中为这些值的内容，因为它们通常不对应任何具体内容
        discard_subtype = ("doc_title", "title", "para_title")  # 返回值中，忽略其中sub_title对应的值中为这些值的内容，因为它们通常不对应任何具体内容
        # raw_content 指的是PDF文档解析服务返回值中的data字段，其余的输入都会导致错误
        query_list = []
        layouts = raw_content.get("layouts", []) if raw_content.get("layouts", None) is not None else []
        for layout in layouts:
            if layout.get("subType", "Unknown") in discard_subtype:
                continue
            elif layout.get("type", "Unknown") == "table": # 对返回内容中被标记为table的元素进行特别处理，以去除在识别过程中产生的非预期字符
                table_content = layout.get("markdownContent", "")
                table_content = table_content.split("\n")
                table_content = process_list(table_content)
                for s in table_content:
                    if type(s) == type("hello"):
                        query_list.append(s) # 将表格中的每一个格子中的内容加入至列表中
                    else:
                        continue

            markdown = layout.get("markdownContent", None) if layout.get("markdownContent", None) is not None else ""
            query_list.append(markdown)
        print(f"The length of query_list is: {len(query_list)}")
        client = OpenAI(
            api_key=self.dash_scope_key,  # 直接配置api key以访问阿里云提供的服务
            base_url=self.bailian_endpoint  # 百炼服务的base_url
        )

        # 阿里云的词嵌入接口一次性最多接受10个字符串输入，所以要分开来上传
        vector_list = []
        for i in range(0,len(query_list)-10,10):
            completion = client.embeddings.create(
                model="text-embedding-v4",
                input=query_list[i:i+10], # 一次性批上传10个文本块至阿里云百炼API
                dimensions=1024,  # 指定向量维度（仅 text-embedding-v3及 text-embedding-v4支持该参数）
                encoding_format="float"
            )
            vector_list.append(completion.data)
        flatten_vector_list = [
            np.array(item.embedding,dtype=float)
            for sublist in vector_list
            for item in sublist
        ]
        rawcontent_vector_pair = list(zip(query_list, flatten_vector_list))
        return rawcontent_vector_pair
        # print(completion.model_dump_json())
        # return vector_list, query_list # 同时返回原文内容和其对应的向量
    def file2VectorDB(self, file_path:str)->bool:
        response = self.__doc_analysation(file_path)
        vector_pairs = self.__content_vectorised(response)
        client = dashvector.Client(
            api_key=self.dash_vector_key,
            endpoint=self.vectorDB_endpoint
        )
        collection = client.get(name='simple_collection')
        for i in range(len(vector_pairs)):
            ret = collection.insert(
                Doc(
                    # 测试时，需要指定id，使用覆盖操作防止数据库存储因测试而增大，导致不必要的花销
                    id=str(i),
                    vector=vector_pairs[i][1],
                    fields={
                        "raw_text":  vector_pairs[i][0],
                        "sub_title": "test"
                    }
                )
            )
            assert ret # 判断插入操作是否成功
        return True

class UserRetrieve:
    def __init__(self):
        """
        从项目的根目录处加载.env文件，这个类需要读取的api key有：
        ALIBABA_CLOUD_ACCESS_KEY_ID=SECRET
        ALIBABA_CLOUD_ACCESS_KEY_SECRET=SECRET
        DASHSCOPE_API_KEY=SECRET
        正式部署时不能从.env文件中读取密钥，而是通过阿里巴巴的密钥管理系统管理密钥
        """
        # 获取当前文件的绝对路径
        current_file_path = os.path.abspath(__file__)
        # 获取当前文件所在目录（即 aurawell/rag）
        current_dir = os.path.dirname(current_file_path)
        # 获取项目根目录
        project_root = os.path.dirname(os.path.dirname(current_dir))
        # 构建 .env 文件的完整路径
        dotenv_path = os.path.join(project_root, '.env')
        # 加载指定路径下的 .env 文件
        load_dotenv(dotenv_path=dotenv_path)
        self.dash_scope_key = os.getenv("DASHSCOPE_API_KEY")
        self.dash_vector_key = os.getenv("DASH_VECTOR_API")

        # 访问的域名
        # 阿里云的向量数据库服务的节点地址
        self.vectorDB_endpoint = "vrs-cn-6sa4axaiv0001c.dashvector.cn-shanghai.aliyuncs.com"
        self.bailian_endpoint = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    def __user_query_vectorised(self, raw_user_query:str):
        # 目前阿里云已经推出DashScope调用，但是OpenAI兼容方法对应的文档更清晰，先用着
        client = OpenAI(
            api_key=self.dash_scope_key,  # 直接配置api key以访问阿里云提供的服务
            base_url=self.bailian_endpoint  # 百炼服务的base_url
        )
        completion = client.embeddings.create(
            model="text-embedding-v4",
            input=raw_user_query,  # 一次性批上传10个文本块至阿里云百炼API
            dimensions=1024,  # 指定向量维度（仅 text-embedding-v3及 text-embedding-v4支持该参数）
            encoding_format="float"
        )
        print(type(completion.data)) # 请注意，返回值是一个长度为1的列表，因此需要取列表的第一个元素，然后再转化
        embeded_result = (raw_user_query , np.array(completion.data[0].embedding, dtype=float))
        return embeded_result
    def retrieve_topK(self, user_query:str, k:int):
        relate_words = []
        client = dashvector.Client(
            api_key=self.dash_vector_key,
            endpoint=self.vectorDB_endpoint
        )
        collection = client.get(name='simple_collection')
        vectorised_user_input = self.__user_query_vectorised(user_query)


        ret = collection.query(
            vector=vectorised_user_input[1],
            topk=k,
            output_fields=['raw_text', 'sub_title'],
            include_vector=True
        )
        if ret:
            print("query success")
        retrieve_result = []
        for content in ret.output:
            retrieve_result.append(content.fields["raw_text"])
        return  retrieve_result

if __name__ == "__main__":
    test_user = UserRetrieve()
    retrieve_list = test_user.retrieve_topK("每日营养建议", 3)
    print(len(retrieve_list))
    print(retrieve_list)