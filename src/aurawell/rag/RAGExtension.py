"""
增强检索方法，通过向量相似度查找，检索数据库中前K个和用户查询相关的字段，也提供将文档解析并上传至向量数据库的方法
该拓展使用阿里巴巴提供的云服务，使用前请务必通过pip命令安装好对应的库
目前通过.env解析密钥，未来将通过KMS密钥管理系统解析密钥
rag_utils是一个辅助RAGExtension核心逻辑运行的工具类，其本身不会调用API
"""
try:
    from .rag_utils import get_file_type, process_list
    from .oss_utils import OSSManager
    from .file_index_manager import FileIndexManager
except ImportError:
    from rag_utils import get_file_type, process_list
    from oss_utils import OSSManager
    from file_index_manager import FileIndexManager
from alibabacloud_docmind_api20220711.client import Client as docmind_api20220711Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_docmind_api20220711 import models as docmind_api20220711_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_credentials.client import Client as CredClient
from alibabacloud_credentials.models import Config as CredentialsConfig
from dashvector import Doc

from openai import OpenAI
from dotenv import load_dotenv
import uuid
import os
import time
import dashvector
import numpy as np
import platform
import re
import math
import tempfile
from datetime import datetime, timedelta, timezone

def normalize_file_path(file_path: str) -> str:
    """
    跨平台文件路径标准化处理

    Args:
        file_path (str): 输入的文件路径

    Returns:
        str: 标准化后的绝对路径
    """
    # 将路径转换为绝对路径
    abs_path = os.path.abspath(file_path)

    # 标准化路径分隔符
    normalized_path = os.path.normpath(abs_path)

    return normalized_path

def load_api_keys():
    """
    从.env文件或环境变量中加载API密钥
    优先尝试从.env文件加载，如果失败则从环境变量加载

    Returns:
        dict: 包含所有API密钥的字典，如果某个密钥未找到则值为None
        bool: 是否成功加载了所有必需的密钥
    """
    keys = {
        "ALIBABA_CLOUD_ACCESS_KEY_ID": None,
        "ALIBABA_CLOUD_ACCESS_KEY_SECRET": None,
        "DASHSCOPE_API_KEY": None,
        "ALIBABA_QWEN_API_KEY": None,
        "DASH_VECTOR_API": None
    }

    # 方法1: 尝试从.env文件加载
    try:
        # 获取当前文件的绝对路径
        current_file_path = os.path.abspath(__file__)
        # 获取当前文件所在目录（即 src/aurawell/rag）
        current_dir = os.path.dirname(current_file_path)
        # 获取项目根目录（向上三级：rag -> aurawell -> src -> 项目根目录）
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
        # 构建 .env 文件的完整路径
        dotenv_path = os.path.join(project_root, '.env')

        # 如果.env文件存在，尝试加载
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path=dotenv_path)
            print(f"✅ 尝试从.env文件加载密钥: {dotenv_path}")
        else:
            print(f"⚠️  .env文件不存在: {dotenv_path}")
    except Exception as e:
        print(f"⚠️  从.env文件加载密钥失败: {e}")

    # 方法2: 从环境变量读取（包括.env加载后的环境变量）
    for key in keys.keys():
        value = os.getenv(key)
        if value:
            keys[key] = value
            print(f"✅ 成功加载密钥: {key}")
        else:
            print(f"❌ 未找到密钥: {key}")

    # 检查是否所有必需的密钥都已加载
    missing_keys = [key for key, value in keys.items() if not value]
    success = len(missing_keys) == 0

    if success:
        print("🎉 所有API密钥加载成功")
    else:
        print(f"⚠️  缺少以下密钥: {missing_keys}")

    return keys, success

def detect_language(text: str) -> str:
    """
    检测文本语言，返回 'chinese' 或 'english'
    如果不确定则默认返回 'chinese'

    Args:
        text (str): 待检测的文本

    Returns:
        str: 'chinese' 或 'english'
    """
    if not text or not isinstance(text, str):
        return 'chinese'

    # 统计中文字符数量
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    # 统计英文字符数量（字母）
    english_chars = len(re.findall(r'[a-zA-Z]', text))

    # 如果中文字符占比超过30%，认为是中文
    total_chars = len(text.strip())
    if total_chars == 0:
        return 'chinese'

    chinese_ratio = chinese_chars / total_chars
    english_ratio = english_chars / total_chars

    # 如果中文字符比例大于英文字符比例，且中文字符比例超过0.1，则认为是中文
    if chinese_ratio > english_ratio and chinese_ratio > 0.1:
        return 'chinese'
    elif english_ratio > 0.3:  # 英文字符比例超过30%认为是英文
        return 'english'
    else:
        return 'chinese'  # 默认返回中文

def translate_text(text: str, target_language: str, api_key: str, base_url: str) -> str:
    """
    使用阿里云大语言模型进行文本翻译

    Args:
        text (str): 待翻译的文本
        target_language (str): 目标语言 ('chinese' 或 'english')
        api_key (str): API密钥
        base_url (str): API基础URL

    Returns:
        str: 翻译后的文本
    """
    try:
        client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )

        if target_language == 'chinese':
            system_prompt = "你是一个专业的英译中翻译专家。请将用户输入的英文文本翻译成中文，保持原意不变。只返回翻译结果，不要添加任何解释。"
            user_prompt = f"请将以下英文翻译成中文：{text}"
        else:  # target_language == 'english'
            system_prompt = "You are a professional Chinese-to-English translator. Please translate the user's Chinese text into English while maintaining the original meaning. Only return the translation result without any explanations."
            user_prompt = f"请将以下中文翻译成英文：{text}"

        completion = client.chat.completions.create(
            model="qwen-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=1024
        )

        translated_text = completion.choices[0].message.content.strip()
        return translated_text

    except Exception as e:
        print(f"翻译失败: {e}")
        return text  # 翻译失败时返回原文

class Document:
    def __init__(self):
        """
        从.env文件或环境变量中加载API密钥，这个类需要读取的api key有：
        ALIBABA_CLOUD_ACCESS_KEY_ID=SECRET
        ALIBABA_CLOUD_ACCESS_KEY_SECRET=SECRET
        DASHSCOPE_API_KEY=SECRET
        DASH_VECTOR_API=SECRET

        优先从.env文件加载，如果失败则从环境变量加载
        """
        print("🔄 Document类初始化：开始加载API密钥...")

        # 加载API密钥
        keys, success = load_api_keys()

        if not success:
            raise ValueError("❌ 无法加载必需的API密钥，请检查.env文件或环境变量设置")

        # 设置实例变量
        self.access_key_id = keys["ALIBABA_CLOUD_ACCESS_KEY_ID"]
        self.access_key_secret = keys["ALIBABA_CLOUD_ACCESS_KEY_SECRET"]
        self.dash_scope_key = keys["DASHSCOPE_API_KEY"]
        self.qwen_api_key = keys["ALIBABA_QWEN_API_KEY"] or keys["DASHSCOPE_API_KEY"]  # 优先使用QWEN密钥，回退到DASHSCOPE
        self.dash_vector_key = keys["DASH_VECTOR_API"]

        # 访问的域名
        # 阿里云docmind服务的节点地址，写成类属性是为了方便未来更换
        self.docmind_endpoint = f'docmind-api.cn-hangzhou.aliyuncs.com'
        # 阿里云的向量数据库服务的节点地址
        self.vectorDB_endpoint = "vrs-cn-6sa4axaiv0001c.dashvector.cn-shanghai.aliyuncs.com"
        self.bailian_endpoint = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        self.region_id = "cn-hangzhou"

        print("✅ Document类初始化完成")
    def __doc_analysation(self, file_path:str):
        """
        使用阿里云的docmind服务对文档进行解析，返回解析结果
        :param file_path: 文档路径
        :return: 解析结果
        """
        # 标准化文件路径，确保跨平台兼容性
        normalized_path = normalize_file_path(file_path)

        # 检查文件是否存在
        if not os.path.exists(normalized_path):
            raise FileNotFoundError(f"文件不存在: {normalized_path}")

        # 检查文件格式是否支持
        file_extension = get_file_type(normalized_path)
        supported_formats = ["pdf", "docx", "xlsx"]
        if file_extension not in supported_formats:
            raise ValueError(f"不支持的文件格式: {file_extension}. 仅支持: {supported_formats}")
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
        config.read_timeout = 2400 # 10页以上的文件可能真的要上传30分钟以上，实在是很难绷
        config.connect_timeout = 1200 # 人在珀斯，连接不稳定，所以只能先这么设置
        config.endpoint = self.docmind_endpoint
        client = docmind_api20220711Client(config)
        request = docmind_api20220711_models.SubmitDocParserJobAdvanceRequest(
            # file_url_object : 本地文件流
            file_url_object=open(normalized_path, "rb"),
            # 文档类型是必须上传的参数
            file_name_extension=get_file_type(normalized_path)
        )
        runtime = util_models.RuntimeOptions(
            read_timeout=24000,
            connect_timeout=12000
        )
        response = client.submit_doc_parser_job_advance(request, runtime)
        print(response.body) # 查看到底是什么返回

        # 检查响应是否成功
        if response.body.data is None:
            print(f"Error: {response.body}")
            raise Exception(f"Document parsing failed: {response.body}")

        job_id = response.body.data.id
        request = docmind_api20220711_models.QueryDocParserStatusRequest(
            # id :  任务提交接口返回的id
            id=job_id
        )
        response = client.query_doc_parser_status(request)
        service_status = response.body.data.status
        wait_time = 0.0 # 目前没有想到一个合适的检测超时的办法，先就这么将就一下吧
        while service_status != "success" and wait_time < 2400:
            time.sleep(0.5)
            wait_time += 0.5
            response = client.query_doc_parser_status(request)
            service_status = response.body.data.status
            print(service_status)
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

    def __is_reference_content(self, text: str) -> bool:
        """
        判断文本是否为文献引用内容

        Args:
            text (str): 待检测的文本

        Returns:
            bool: True 如果是引用内容，False 否则
        """
        if not text or not isinstance(text, str):
            return False

        text = text.strip()

        # 如果文本太短，不太可能是引用
        if len(text) < 10:
            return False

        # 检测引用的特征模式
        import re

        # 模式1: 以方括号数字开头的引用 [1], [19], [1-3] 等
        bracket_number_pattern = r'^\[\d+(-\d+)?\]'
        if re.match(bracket_number_pattern, text):
            return True

        # 模式2: 包含DOI的引用
        doi_pattern = r'DOI\s*:\s*10\.\d+/'
        if re.search(doi_pattern, text, re.IGNORECASE):
            return True

        # 模式3: 包含期刊引用格式的文本
        # 检测格式：作者名,标题[J].期刊名,年份,卷(期):页码
        journal_pattern = r'[^,]+,.*?\[J\]\..*?,\d{4},.*?:'
        if re.search(journal_pattern, text):
            return True

        # 模式4: 包含多个作者的引用格式 (姓名,姓名,等.)
        multiple_authors_pattern = r'[^,]+,[^,]+,等\.'
        if re.search(multiple_authors_pattern, text):
            return True

        # 模式5: 包含英文期刊引用格式
        # 检测格式：Author A, Author B, et al. Title[J]. Journal, Year, Volume(Issue): Pages.
        english_journal_pattern = r'[A-Z][a-z]+\s+[A-Z]{1,3},.*?et\s+al\..*?\[J\]\..*?,\s*\d{4}'
        if re.search(english_journal_pattern, text):
            return True

        # 模式6: 包含ISBN或ISSN的引用
        isbn_issn_pattern = r'(ISBN|ISSN)\s*[:：]\s*[\d-]+'
        if re.search(isbn_issn_pattern, text, re.IGNORECASE):
            return True

        # 模式7: 检测引用中常见的标点符号密度
        # 引用通常包含大量的逗号、句号、冒号等
        punctuation_count = sum(1 for char in text if char in ',.;:()[]{}')
        if len(text) > 50 and punctuation_count / len(text) > 0.15:
            # 进一步检查是否包含年份
            year_pattern = r'\b(19|20)\d{2}\b'
            if re.search(year_pattern, text):
                return True

        return False

    def get_recent_files_from_oss(self, days: int = 30) -> list:
        """
        从OSS云存储中读取在指定天数内上传的文件

        Args:
            days (int): 天数，默认30天

        Returns:
            list: 文件记录列表
        """
        try:
            file_manager = FileIndexManager()
            recent_files = file_manager.get_files_uploaded_in_days(days)

            print(f"✅ 从OSS获取到 {len(recent_files)} 个在 {days} 天内上传的文件")
            return recent_files

        except Exception as e:
            print(f"❌ 从OSS获取最近文件失败: {e}")
            return []

    def download_file_from_oss(self, oss_key: str, local_path: str = None) -> str:
        """
        从OSS下载文件到本地临时位置

        Args:
            oss_key (str): OSS中的文件键名
            local_path (str): 本地保存路径，如果为None则使用临时文件

        Returns:
            str: 本地文件路径，失败返回None
        """
        try:
            oss_manager = OSSManager()

            if local_path is None:
                # 创建临时文件
                suffix = os.path.splitext(oss_key)[1] or '.tmp'
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
                local_path = temp_file.name
                temp_file.close()

            success = oss_manager.download_file(oss_key, local_path)

            if success:
                print(f"✅ 文件从OSS下载成功: {oss_key} -> {local_path}")
                return local_path
            else:
                print(f"❌ 文件从OSS下载失败: {oss_key}")
                return None

        except Exception as e:
            print(f"❌ 从OSS下载文件失败: {e}")
            return None

    def upload_parsed_content_to_oss(self, content: str, filename: str) -> bool:
        """
        将解析的文件内容以markdown形式上传到OSS

        Args:
            content (str): 解析后的文档内容
            filename (str): 原始文件名

        Returns:
            bool: 上传是否成功
        """
        try:
            oss_manager = OSSManager()

            # 构建markdown文件的OSS键名
            base_name = os.path.splitext(filename)[0]
            markdown_key = f"parsed_content/{base_name}.md"

            # 添加时间戳和元数据
            timestamp = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")
            markdown_content = f"""# 解析文档: {filename}

**解析时间**: {timestamp}
**原始文件**: {filename}

---

{content}
"""

            success = oss_manager.upload_string_as_file(markdown_content, markdown_key)

            if success:
                print(f"✅ 解析内容上传到OSS成功: {markdown_key}")
            else:
                print(f"❌ 解析内容上传到OSS失败: {markdown_key}")

            return success

        except Exception as e:
            print(f"❌ 上传解析内容到OSS失败: {e}")
            return False

    def content_filter(self, file_path: str, is_oss_key: bool = False) -> list:
        """
        使用大语言模型分析文档内容，提取高信息密度文本，并将结果向量化存储到数据库

        Args:
            file_path (str): 文档路径或OSS键名
            is_oss_key (bool): 是否为OSS键名

        Returns:
            list: 包含提取的高密度信息段落的列表，每个元素都是字符串
        """
        temp_file_path = None
        try:
            # 1. 如果是OSS键名，先下载到本地
            if is_oss_key:
                temp_file_path = self.download_file_from_oss(file_path)
                if not temp_file_path:
                    print(f"❌ 无法从OSS下载文件: {file_path}")
                    return []
                actual_file_path = temp_file_path
                original_filename = os.path.basename(file_path)
            else:
                actual_file_path = file_path
                original_filename = os.path.basename(file_path)

            # 2. 使用现有方法解析文档
            raw_content = self.__doc_analysation(actual_file_path)

            # 3. 提取文档的完整文本内容
            full_text = self.file_Parsing(actual_file_path)

            if not full_text or len(full_text.strip()) < 10:
                print("文档内容为空或过短，无法进行内容过滤")
                return []

            # 3. 使用大语言模型提取高密度信息
            client = OpenAI(
                api_key=self.qwen_api_key,
                base_url=self.bailian_endpoint
            )

            # 构建提示词
            system_prompt = """你是一位医学文献信息提取专家。请仔细阅读以下文本，从中提取所有**高密度信息段落**，包括但不限于：

- 膳食建议
- 推荐摄入量
- 健康建议
- 具体食物种类与克数
- 饮水与运动指导
- 营养标准与指标
- 食品标签解读要点
- 分餐与卫生建议
- 膳食宝塔结构
- 特定人群推荐（如孕妇、儿童、老年人）

提取要求如下：

1. **高密度信息**：具备明确数值、指导建议、可执行内容
2. **去除低密度信息**：如背景介绍、定义、政策说明、意义阐述等
3. **保留原文格式**，但只提取核心段落
4. 使用 `;;` 分隔每一个提取出来的信息段

现在请处理以下文本："""

            user_prompt = full_text

            # 调用大语言模型
            completion = client.chat.completions.create(
                model="qwen-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                top_p=0.9,
                max_tokens=2048
            )

            # 4. 处理大语言模型的返回结果
            llm_response = completion.choices[0].message.content.strip()

            if not llm_response:
                print("大语言模型返回空结果")
                return []

            # 5. 按 ";;" 分割文本
            segments = llm_response.split(";;")

            # 6. 清理和过滤分割后的文本段
            filtered_segments = []
            for segment in segments:
                cleaned_segment = segment.strip()
                # 过滤掉长度小于3的段落
                if len(cleaned_segment) >= 3:
                    filtered_segments.append(cleaned_segment)

            print(f"成功提取 {len(filtered_segments)} 个高密度信息段落")

            # 7. 将过滤后的段落向量化并存储到数据库
            if filtered_segments:
                self._vectorize_and_store_segments(filtered_segments)

            # 8. 如果是OSS文件，上传解析内容
            if is_oss_key and full_text:
                try:
                    self.upload_parsed_content_to_oss(full_text, original_filename)
                except Exception as e:
                    print(f"⚠️  上传解析内容失败: {e}")

            return filtered_segments

        except Exception as e:
            print(f"❌ 内容过滤过程中发生错误: {e}")
            return []
        finally:
            # 清理临时文件
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                    print(f"🗑️  清理临时文件: {temp_file_path}")
                except Exception as e:
                    print(f"⚠️  清理临时文件失败: {e}")

    def _vectorize_and_store_segments(self, segments: list):
        """
        将文本段落向量化并存储到向量数据库

        Args:
            segments (list): 文本段落列表
        """
        try:
            client = OpenAI(
                api_key=self.dash_scope_key,
                base_url=self.bailian_endpoint
            )

            # 连接向量数据库
            vector_client = dashvector.Client(
                api_key=self.dash_vector_key,
                endpoint=self.vectorDB_endpoint
            )
            collection = vector_client.get(name='simple_collection')

            # 批量处理向量化（每次最多10个）
            for i in range(0, len(segments), 10):
                batch = segments[i:i+10]

                # 向量化当前批次
                completion = client.embeddings.create(
                    model="text-embedding-v4",
                    input=batch,
                    dimensions=1024,
                    encoding_format="float"
                )

                # 存储到向量数据库
                for j, embedding_data in enumerate(completion.data):
                    segment_text = batch[j]
                    vector = np.array(embedding_data.embedding, dtype=float)

                    ret = collection.insert(
                        Doc(
                            id=str(uuid.uuid4()),
                            vector=vector,
                            fields={
                                "raw_text": segment_text,
                                "sub_title": "filtered_content"
                            }
                        )
                    )

                    if not ret:
                        print(f"向量存储失败: {segment_text[:50]}...")

            print(f"成功将 {len(segments)} 个段落向量化并存储到数据库")

        except Exception as e:
            print(f"向量化和存储过程中发生错误: {e}")

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
                        # 检查是否为引用内容，如果是则跳过
                        if not self.__is_reference_content(s):
                            query_list.append(s) # 将表格中的每一个格子中的内容加入至列表中
                    else:
                        continue

            markdown = layout.get("markdownContent", None) if layout.get("markdownContent", None) is not None else ""
            # 检查markdown内容是否为引用，如果不是引用才添加到列表中
            if markdown and not self.__is_reference_content(markdown):
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
                # 目前项目启用的DashVector仅支持固定长度的向量，根据简单调查，选择1024维这个比较通用的选择
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
    def file2VectorDB(self, file_path: str, use_content_filter: bool = True, is_oss_key: bool = False, update_index: bool = True) -> bool:
        """
        将文档解析并上传至向量数据库

        Args:
            file_path (str): 文档路径或OSS键名
            use_content_filter (bool): 是否使用内容过滤功能，默认为True
            is_oss_key (bool): 是否为OSS键名
            update_index (bool): 是否更新文件索引的向量化状态

        Returns:
            bool: 操作是否成功
        """
        try:
            filename = os.path.basename(file_path) if not is_oss_key else os.path.basename(file_path)

            if use_content_filter:
                # 使用新的内容过滤方法
                filtered_segments = self.content_filter(file_path, is_oss_key=is_oss_key)
                if filtered_segments:
                    print(f"✅ 使用内容过滤方法成功处理文档，提取了 {len(filtered_segments)} 个高密度信息段落")

                    # 更新向量化状态
                    if update_index and is_oss_key:
                        try:
                            file_manager = FileIndexManager()
                            file_manager.update_vectorization_status(filename, True)
                        except Exception as e:
                            print(f"⚠️  更新向量化状态失败: {e}")

                    return True
                else:
                    print("⚠️ 内容过滤未提取到有效信息，回退到原始方法")
                    # 如果内容过滤失败，回退到原始方法
                    use_content_filter = False

            if not use_content_filter:
                # 使用原始方法
                actual_file_path = file_path
                temp_file_path = None

                try:
                    # 如果是OSS键名，先下载到本地
                    if is_oss_key:
                        temp_file_path = self.download_file_from_oss(file_path)
                        if not temp_file_path:
                            print(f"❌ 无法从OSS下载文件: {file_path}")
                            return False
                        actual_file_path = temp_file_path

                    response = self.__doc_analysation(actual_file_path)
                    vector_pairs = self.__content_vectorised(response)
                    client = dashvector.Client(
                        api_key=self.dash_vector_key,
                        endpoint=self.vectorDB_endpoint
                    )
                    collection = client.get(name='simple_collection')
                    for i in range(len(vector_pairs)):
                        ret = collection.insert(
                            Doc(
                                id=str(uuid.uuid4()),
                                vector=vector_pairs[i][1],
                                fields={
                                    "raw_text": vector_pairs[i][0],
                                    "sub_title": "original_content"
                                }
                            )
                        )
                        assert ret  # 判断插入操作是否成功
                    print(f"✅ 使用原始方法成功处理文档，存储了 {len(vector_pairs)} 个文本段落")

                    # 更新向量化状态
                    if update_index and is_oss_key:
                        try:
                            file_manager = FileIndexManager()
                            file_manager.update_vectorization_status(filename, True)
                        except Exception as e:
                            print(f"⚠️  更新向量化状态失败: {e}")

                finally:
                    # 清理临时文件
                    if temp_file_path and os.path.exists(temp_file_path):
                        try:
                            os.unlink(temp_file_path)
                        except Exception as e:
                            print(f"⚠️  清理临时文件失败: {e}")

            return True

        except Exception as e:
            print(f"❌ 文档处理失败: {e}")
            return False

    def batch_process_recent_files(self, days: int = 30, use_content_filter: bool = True) -> dict:
        """
        批量处理OSS中最近上传的文件

        Args:
            days (int): 处理最近几天的文件，默认30天
            use_content_filter (bool): 是否使用内容过滤功能

        Returns:
            dict: 处理结果统计
        """
        try:
            # 获取最近上传的文件
            recent_files = self.get_recent_files_from_oss(days)

            if not recent_files:
                print(f"⚠️  未找到最近 {days} 天内上传的文件")
                return {"total": 0, "processed": 0, "failed": 0, "skipped": 0}

            # 过滤出未向量化的文件
            unvectorized_files = [f for f in recent_files if not f.get("vectorized", False)]

            print(f"📊 处理统计:")
            print(f"  - 最近 {days} 天内上传的文件: {len(recent_files)}")
            print(f"  - 未向量化的文件: {len(unvectorized_files)}")

            if not unvectorized_files:
                print("✅ 所有最近上传的文件都已向量化")
                return {"total": len(recent_files), "processed": 0, "failed": 0, "skipped": len(recent_files)}

            # 批量处理文件
            results = {"total": len(unvectorized_files), "processed": 0, "failed": 0, "skipped": 0}

            for i, file_record in enumerate(unvectorized_files, 1):
                filename = file_record["filename"]
                oss_key = file_record["oss_key"]

                print(f"\n[{i}/{len(unvectorized_files)}] 处理文件: {filename}")

                try:
                    success = self.file2VectorDB(
                        oss_key,
                        use_content_filter=use_content_filter,
                        is_oss_key=True,
                        update_index=True
                    )

                    if success:
                        results["processed"] += 1
                        print(f"✅ 文件处理成功: {filename}")
                    else:
                        results["failed"] += 1
                        print(f"❌ 文件处理失败: {filename}")

                except Exception as e:
                    results["failed"] += 1
                    print(f"❌ 文件处理异常: {filename}, 错误: {e}")

            print(f"\n🎉 批量处理完成!")
            print(f"📊 处理结果:")
            print(f"  - 总文件数: {results['total']}")
            print(f"  - 处理成功: {results['processed']}")
            print(f"  - 处理失败: {results['failed']}")
            print(f"  - 跳过文件: {results['skipped']}")

            return results

        except Exception as e:
            print(f"❌ 批量处理失败: {e}")
            return {"total": 0, "processed": 0, "failed": 0, "skipped": 0}

class UserRetrieve:
    def __init__(self):
        """
        从.env文件或环境变量中加载API密钥，这个类需要读取的api key有：
        DASHSCOPE_API_KEY=SECRET
        DASH_VECTOR_API=SECRET

        优先从.env文件加载，如果失败则从环境变量加载
        """
        print("🔄 UserRetrieve类初始化：开始加载API密钥...")

        # 加载API密钥
        keys, success = load_api_keys()

        # UserRetrieve只需要部分密钥
        required_keys = ["DASH_VECTOR_API"]
        # 检查是否有可用的API密钥（DASHSCOPE_API_KEY 或 ALIBABA_QWEN_API_KEY）
        has_llm_key = keys.get("DASHSCOPE_API_KEY") or keys.get("ALIBABA_QWEN_API_KEY")

        missing_keys = [key for key in required_keys if not keys.get(key)]
        if missing_keys or not has_llm_key:
            missing_keys.append("DASHSCOPE_API_KEY 或 ALIBABA_QWEN_API_KEY")
            raise ValueError(f"❌ UserRetrieve类缺少必需的API密钥: {missing_keys}")

        # 设置实例变量
        self.dash_scope_key = keys["DASHSCOPE_API_KEY"]
        self.qwen_api_key = keys["ALIBABA_QWEN_API_KEY"] or keys["DASHSCOPE_API_KEY"]  # 优先使用QWEN密钥
        self.dash_vector_key = keys["DASH_VECTOR_API"]

        # 访问的域名
        # 阿里云的向量数据库服务的节点地址
        self.vectorDB_endpoint = "vrs-cn-6sa4axaiv0001c.dashvector.cn-shanghai.aliyuncs.com"
        self.bailian_endpoint = "https://dashscope.aliyuncs.com/compatible-mode/v1"

        print("✅ UserRetrieve类初始化完成")
    def __user_query_vectorised(self, raw_user_query: str):
        """
        增强的用户查询向量化方法，支持中英文检测和翻译

        Args:
            raw_user_query (str): 用户原始查询

        Returns:
            dict: 包含原文和翻译副本的向量化结果
                {
                    'original': {'text': str, 'vector': np.array, 'language': str},
                    'translated': {'text': str, 'vector': np.array, 'language': str}
                }
        """
        # 1. 使用新的翻译服务进行语言检测和翻译
        try:
            from ..services.translation_service import get_translation_service
            translation_service = get_translation_service()
            translation_result = translation_service.query_translation(raw_user_query)

            # 提取翻译结果
            original_text = translation_result['original']['text']
            original_language = translation_result['original']['language']
            translated_text = translation_result['translated']['text']
            translated_language = translation_result['translated']['language']

            print(f"🔍 检测到查询语言: {original_language}")
            print(f"📝 原文: {original_text}")
            print(f"🔄 翻译: {translated_text}")

        except Exception as e:
            print(f"⚠️ 新翻译服务失败，回退到原有翻译方法: {e}")
            # 回退到原有的翻译方法
            detected_language = detect_language(raw_user_query)
            print(f"🔍 检测到查询语言: {detected_language}")

            if detected_language == 'chinese':
                translated_query = translate_text(
                    raw_user_query,
                    'english',
                    self.qwen_api_key,
                    self.bailian_endpoint
                )
                translated_language = 'english'
            else:
                translated_query = translate_text(
                    raw_user_query,
                    'chinese',
                    self.qwen_api_key,
                    self.bailian_endpoint
                )
                translated_language = 'chinese'

            # 统一变量名
            original_text = raw_user_query
            original_language = detected_language
            translated_text = translated_query

        # 3. 对原文和翻译副本进行向量化
        client = OpenAI(
            api_key=self.dash_scope_key,
            base_url=self.bailian_endpoint
        )

        # 批量向量化原文和翻译
        completion = client.embeddings.create(
            model="text-embedding-v4",
            input=[original_text, translated_text],
            dimensions=1024,
            encoding_format="float"
        )

        # 4. 构建返回结果
        result = {
            'original': {
                'text': original_text,
                'vector': np.array(completion.data[0].embedding, dtype=float),
                'language': original_language
            },
            'translated': {
                'text': translated_text,
                'vector': np.array(completion.data[1].embedding, dtype=float),
                'language': translated_language
            }
        }

        return result
    def retrieve_topK(self, user_query: str, k: int):
        """
        增强的TopK检索方法，支持中英文双语检索

        Args:
            user_query (str): 用户查询
            k (int): 返回结果数量

        Returns:
            list: 检索到的相关文本列表，每个元素都是字符串
        """
        # 1. 获取用户查询的向量化结果（包含原文和翻译）
        vectorised_queries = self.__user_query_vectorised(user_query)

        # 2. 连接向量数据库
        client = dashvector.Client(
            api_key=self.dash_vector_key,
            endpoint=self.vectorDB_endpoint
        )
        collection = client.get(name='simple_collection')

        # 3. 计算每次检索的数量（向上取整）
        k_per_query = math.ceil(k / 2)
        print(f"🔍 每个查询检索 {k_per_query} 个结果，总共检索 {k} 个结果")

        # 4. 使用原文进行检索
        print(f"🔍 使用原文检索: {vectorised_queries['original']['text']}")
        ret_original = collection.query(
            vector=vectorised_queries['original']['vector'],
            topk=k_per_query,
            output_fields=['raw_text', 'sub_title'],
            include_vector=True
        )

        # 5. 使用翻译副本进行检索
        print(f"🔍 使用翻译检索: {vectorised_queries['translated']['text']}")
        ret_translated = collection.query(
            vector=vectorised_queries['translated']['vector'],
            topk=k_per_query,
            output_fields=['raw_text', 'sub_title'],
            include_vector=True
        )

        # 6. 合并检索结果
        retrieve_result = []
        seen_texts = set()  # 用于去重

        # 添加原文检索结果
        if ret_original and ret_original.output:
            print(f"✅ 原文检索成功，获得 {len(ret_original.output)} 个结果")
            for content in ret_original.output:
                text = content.fields["raw_text"]
                if text not in seen_texts:
                    retrieve_result.append(text)
                    seen_texts.add(text)
        else:
            print("⚠️ 原文检索失败或无结果")

        # 添加翻译检索结果
        if ret_translated and ret_translated.output:
            print(f"✅ 翻译检索成功，获得 {len(ret_translated.output)} 个结果")
            for content in ret_translated.output:
                text = content.fields["raw_text"]
                if text not in seen_texts:
                    retrieve_result.append(text)
                    seen_texts.add(text)
        else:
            print("⚠️ 翻译检索失败或无结果")

        print(f"🎉 总共检索到 {len(retrieve_result)} 个唯一结果")
        return retrieve_result

if __name__ == "__main__":
    # test_user = UserRetrieve()
    # retrieve_list = test_user.retrieve_topK("每日营养建议", 3)
    # print(len(retrieve_list))
    # print(retrieve_list)

    # 使用跨平台路径处理
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sample_doc_path = os.path.join(current_dir, "testMaterials", "中国成年人肉类食物摄入与代谢综合征的相关性研究.pdf")

    obj = Document()
    result = obj.file2VectorDB(sample_doc_path)
    print(result)

