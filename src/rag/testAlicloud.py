"""
该文件中的DocVectorised仅用于内部调试，不建议在正式部署中使用本模块中的方法

"""
from alibabacloud_docmind_api20220711.client import Client as docmind_api20220711Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_docmind_api20220711 import models as docmind_api20220711_models
from alibabacloud_tea_util.client import Client as UtilClient
from alibabacloud_tea_util import models as util_models
from alibabacloud_credentials.client import Client as CredClient
from alibabacloud_credentials.client import Client as CredentialsClient
from alibabacloud_credentials.models import Config as CredentialsConfig
import dashvector
from dashvector import Doc
import numpy as np
from numpy.f2py.crackfortran import dimensionpattern
from openai import OpenAI
from dotenv import load_dotenv
import os
import time
import re
from datetime import datetime
class DocVectorised:
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
        access_key_id = os.getenv("ALIBABA_CLOUD_ACCESS_KEY_ID")
        access_key_secret = os.getenv("ALIBABA_CLOUD_ACCESS_KEY_SECRET")
        self.dash_scope_key = os.getenv("DASHSCOPE_API_KEY")
        self.dash_vector_key = os.getenv("DASH_VECTOR_API")
        # 构造 Credential，直接从本地读取，在正式部署时需要更改
        cred_config = CredentialsConfig(
            type="access_key",
            access_key_id=access_key_id,
            access_key_secret=access_key_secret
        )
        # 加载完毕，现在可以初始化类
        self.cred = CredClient(config=cred_config)
        self.config = open_api_models.Config(
            # 通过credentials获取配置中的AccessKey ID
            access_key_id=self.cred.get_credential().get_access_key_id(),
            # 通过credentials获取配置中的AccessKey Secret
            access_key_secret=self.cred.get_credential().get_access_key_secret()
        )
        # 访问的域名
        self.config.endpoint = f'docmind-api.cn-hangzhou.aliyuncs.com'
        self.client = docmind_api20220711Client(self.config)
    def _api_test(self,file_path:str):

        request = docmind_api20220711_models.SubmitDocParserJobAdvanceRequest(
            # file_url_object : 本地文件流
            file_url_object=open(file_path, "rb"),
            # # file_name ：文件名称。名称必须包含文件类型
            # file_name='reference01.pdf',
            # file_name_extension : 文件后缀格式。与文件名二选一
            file_name_extension='pdf'
        )
        runtime = util_models.RuntimeOptions()
        try:
            # 复制代码运行请自行打印 API 的返回值
            response = self.client.submit_doc_parser_job_advance(request, runtime)
            # API返回值格式层级为 body -> data -> 具体属性。可根据业务需要打印相应的结果。如下示例为打印返回的业务id格式
            # 获取属性值均以小写开头，
            return response
        except Exception as error:
            # 如有需要，请打印 error
            UtilClient.assert_as_string(error)
            # print(str(error))
            return "Something goes wrong"
    def _query_test(self, job_id:str):
        request = docmind_api20220711_models.QueryDocParserStatusRequest(
            # id :  任务提交接口返回的id
            id=job_id
        )
        try:
            # 复制代码运行请自行打印 API 的返回值
            response = self.client.query_doc_parser_status(request)
            # API返回值格式层级为 body -> data -> 具体属性。可根据业务需要打印相应的结果。获取属性值均以小写开头
            # 获取返回结果。建议先把response.body.data转成json，然后再从json里面取具体需要的值。
            print("查询结果为: ")
            print(response.body)
            print(f"执行状态为:{response.body.data.status}")
            return response.body.data.status
        except Exception as error:
            # 如有需要，请打印 error
            UtilClient.assert_as_string(error)
    def _content_vectorised(self, raw_content):
        discard_type = ()
        discard_subtype = ("doc_title", "title", "para_title")  # 返回值中，忽略其中sub_title为这些值的内容，因为它们通常不对应任何具体内容
        # raw_content 指的是PDF文档解析服务返回值中的data字段，其余的输入都会导致错误
        query_list = []
        layouts = raw_content.get("layouts", []) if raw_content.get("layouts", None) is not None else []
        for layout in layouts:
            if layout.get("subType", "Unknown") in discard_subtype:
                continue
            elif layout.get("type", "Unknown") == "table": # 对返回内容中被标记为table的元素进行特别处理，以去除在识别过程中产生的非预期字符
                table_content = layout.get("markdownContent", "");
                table_content = table_content.split("\n")
                table_content = process_list(table_content)
                for s in table_content:
                    if type(s) == type("hello"):
                        query_list.append(s)
                    else:
                        continue

            markdown = layout.get("markdownContent", None) if layout.get("markdownContent", None) is not None else ""
            query_list.append(markdown)
        print(f"The length of query_list is: {len(query_list)}")
        client = OpenAI(
            api_key=self.dash_scope_key,  # 直接配置api key以访问阿里云提供的服务
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"  # 百炼服务的base_url
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
    def _user_query_vectorised(self, raw_user_query:str):
        client = OpenAI(
            api_key=self.dash_scope_key,  # 直接配置api key以访问阿里云提供的服务
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"  # 百炼服务的base_url
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
    def _vectorDB_storing_process(self, vector_pairs:list):
        client = dashvector.Client(
            api_key=self.dash_vector_key,
            endpoint="vrs-cn-6sa4axaiv0001c.dashvector.cn-shanghai.aliyuncs.com"
        )
        collection = client.get(name='simple_collection')
        for i in range(len(vector_pairs)):
            ret = collection.insert(
                Doc(
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

    def retrieve_test(self,user_input: str):
        relate_words = []
        client = dashvector.Client(
            api_key=self.dash_vector_key,
            endpoint="vrs-cn-6sa4axaiv0001c.dashvector.cn-shanghai.aliyuncs.com"
        )
        collection = client.get(name='simple_collection')
        vectorised_user_input = self._user_query_vectorised(user_input)
        ret = collection.query(
            vector=vectorised_user_input[1]
        )
        # 判断query接口是否成功
        if ret:
            print('query success')
            print(len(ret))
            # for doc in ret:
            #     print(doc)
            #     print(doc.id)
            #     print(doc.vector)
            #     print(doc.fields)

        ret = collection.query(
            vector=vectorised_user_input[1],
            topk=10,
            output_fields=['raw_text', 'sub_title'],
            include_vector=True
        )
        return ret
    def _analysation_test(self, job_id:str):
        request = docmind_api20220711_models.GetDocParserResultRequest(
            # id :  任务提交接口返回的id
            id=job_id,
            layout_step_size=100, #
            layout_num=0
        )
        try:
            # 复制代码运行请自行打印 API 的返回值
            response = self.client.get_doc_parser_result(request)
            # API返回值格式层级为 body -> data -> 具体属性。可根据业务需要打印相应的结果。获取属性值均以小写开头
            # 获取返回结果。建议先把response.body.data转成json，然后再从json里面取具体需要的值。
            print(response.body)
            return response.body.data
        except Exception as error:
            # 如有需要，请打印 error
            UtilClient.assert_as_string(error)
            print(str(error))
    def assemble(self, raw_text)->str:
        """
        从阿里云 DocMind API 返回的 data 字段中提取所有 markdownContent，
        拼接成一个完整的 Markdown 字符串，并：
        - 去除空白行
        - 合并连续的文本块
        """
        full_markdown = ""
        # ✅ 正确访问 layouts 属性
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
    def export_strings_to_files(self,raw_text):
            discard_type = ("doc_title", "title", "para_title")
            try:
                """
                从阿里云 DocMind API 返回的 data 字段中提取所有 markdownContent，
                拼接成一个完整的 Markdown 字符串，并：
                - 去除空白行
                - 合并连续的文本块
                """
                full_markdown = ""
                # ✅ 正确访问 layouts 属性
                query_list = []
                layouts = raw_text.get("layouts", []) if raw_text.get("layouts", None) is not None else []
                for layout in layouts:
                    if layout.get("subType", "Unknown") in discard_type:
                        continue
                    elif layout.get("type", "Unknown") == "table":
                        table_content = layout.get("markdownContent", "NONE");
                        table_content = table_content.split("\n")
                        table_content = process_list(table_content)
                        print(table_content, end=";")
                    markdown = layout.get("markdownContent", None) if layout.get("markdownContent", None) is not None else ""
                    query_list.append(markdown)
                # 创建目标目录（如果不存在）
                output_dir = "./testMaterial/"
                os.makedirs(output_dir, exist_ok=True)

                # 获取当前日期作为文件名前缀
                date_prefix = datetime.now().strftime("%Y%m%d")

                # 遍历列表中的每个字符串元素
                final_content = ""
                for i, content in enumerate(query_list):
                    # 跳过非字符串元素
                    if not isinstance(content, str):
                        continue
                    else:
                        final_content += content
                        final_content += ";\n"
                    # 生成文件名：日期_序号.txt
                filename = f"{date_prefix}_{i + 1}.txt"
                file_path = os.path.join(output_dir, filename)

                try:
                    # 写入文件内容
                    with open(file_path, 'w', encoding='utf-8') as file:
                        file.write(final_content)
                    print(f"成功创建文件: {file_path}")

                except Exception as e:
                    print(f"写入文件 {filename} 失败: {str(e)}")

                return True

            except Exception as e:
                print(f"导出过程中发生错误: {str(e)}")
                return False

def process_list(input_list):
    result = []
    for item in input_list:
        if isinstance(item, str):
            # 去除首尾空白
            stripped = item.strip()
            # 删除HTML标签
            stripped = re.sub(r'<[^>]*>', '', stripped)
            # 检查长度并添加到结果
            if len(stripped) >= 5:
                result.append(stripped)
    return result
def env_reader()->bool:
    # 获取当前文件的绝对路径
    current_file_path = os.path.abspath(__file__)
    # 获取当前文件所在目录（即 aurawell/rag）
    current_dir = os.path.dirname(current_file_path)
    # 获取项目根目录（假设 testAlicloud.py 在 aurawell/rag/ 目录下）
    project_root = os.path.dirname(os.path.dirname(current_dir))
    # 构建 .env 文件的完整路径
    dotenv_path = os.path.join(project_root, '.env')
    # 加载指定路径下的 .env 文件
    load_dotenv(dotenv_path=dotenv_path)
    # 测试读取环境变量
    access_key_id = os.getenv("ALIBABA_CLOUD_ACCESS_KEY_ID")
    access_key_secret = os.getenv("ALIBABA_CLOUD_ACCESS_KEY_SECRET")
    print("AccessKey ID:", access_key_id)
    print("AccessKey Secret:", access_key_secret)
    return True

if __name__ == '__main__':
    obj = DocVectorised()
    # job_response = obj._api_test("./testMaterial/中国居民膳食指南2022.pdf")
    job_id = "docmind-20250612-90d0601c1658474cbe9dcd485068f4af"
    # print(job_id)
    job_status = obj._query_test(job_id)
    # print(job_status)
    time_wait = 0.0
    while job_status != "success" and time_wait < 60:
        time.sleep(0.5)
        time_wait += 0.5
        job_status = obj._query_test(job_id)
        print(job_status)

    result = obj._analysation_test(job_id)
    assembled_markdown = obj.assemble(result)
    obj.export_strings_to_files(result)
    # print(assembled_markdown)
    vectorList= obj._content_vectorised(result)

    # print(type(vectorList))
    # print(len(vectorList))
    print(type(vectorList[0][1]))
    print(vectorList[0][1])
    # if obj._vectorDB_storing_process(vectorList):
    #     print("插入操作成功")
    # else:
    #     print("插入操作失败")
    sample_query = "每日营养摄入建议"
    # sample_vector = obj._user_query_vectorised(sample_query)
    sample_vector = obj.retrieve_test(sample_query)
    print(type(sample_vector))
    print(type(sample_vector.output))
    print(type(sample_vector.output[0]))
    print(sample_vector.output[0].fields)
    print(type(sample_vector.output[0].fields))
    print(sample_vector.output[0].fields["raw_text"])
    # print(sample_vector)
