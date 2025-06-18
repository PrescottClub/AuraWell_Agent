from alibabacloud_docmind_api20220711.client import Client as docmind_api20220711Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_docmind_api20220711 import models as docmind_api20220711_models
from alibabacloud_tea_util.client import Client as UtilClient
from alibabacloud_tea_util import models as util_models
from alibabacloud_credentials.client import Client as CredClient
from alibabacloud_credentials.client import Client as CredentialsClient
from alibabacloud_credentials.models import Config as CredentialsConfig
from dotenv import load_dotenv
import os
import json
class DocVectorised:
    def __init__(self):
        """
        从项目的根目录处加载.env文件，这个类需要读取的api key有：
        ALIBABA_CLOUD_ACCESS_KEY_ID=SECRET
        ALIBABA_CLOUD_ACCESS_KEY_SECRET=SECRET
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
    def _api_test(self,file_path:str):
        self.client = docmind_api20220711Client(self.config)
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
        client = docmind_api20220711Client(self.config)
        request = docmind_api20220711_models.QueryDocParserStatusRequest(
            # id :  任务提交接口返回的id
            id=job_id
        )
        try:
            # 复制代码运行请自行打印 API 的返回值
            response = client.query_doc_parser_status(request)
            # API返回值格式层级为 body -> data -> 具体属性。可根据业务需要打印相应的结果。获取属性值均以小写开头
            # 获取返回结果。建议先把response.body.data转成json，然后再从json里面取具体需要的值。
            print("查询结果为: ")
            print(response.body)
            print(f"执行状态为:{response.body.data.status}")
        except Exception as error:
            # 如有需要，请打印 error
            UtilClient.assert_as_string(error)
    def _analysation_test(self, job_id:str):
        client = docmind_api20220711Client(self.config)
        request = docmind_api20220711_models.GetDocParserResultRequest(
            # id :  任务提交接口返回的id
            id=job_id,
            layout_step_size=100,
            layout_num=0
        )
        try:
            # 复制代码运行请自行打印 API 的返回值
            response = client.get_doc_parser_result(request)
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
            full_markdown += markdown + "\n"
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
def env_reader()->None:
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


if __name__ == '__main__':
    obj = DocVectorised()

    result = obj._analysation_test("docmind-20250611-59752df113a54ef38eb1f25ce880f83f")

    assembled_markdown = obj.assemble(result)
    print(assembled_markdown)