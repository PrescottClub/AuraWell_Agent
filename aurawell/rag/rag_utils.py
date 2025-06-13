from os import getenv
from dotenv import load_dotenv
import os
import re
from datetime import datetime
"""
env_reader() 环境变量测试方法，如果能正确读取，则返回True，否则返回False，建议将这个工具文件放置在和rag模组相同的文件夹下。
process_list(list) 用于处理在文档识别中产生的非预期字符。非预期字符会影响词嵌入模型最终的表现，导致向量生成不准确，所以有必要去除它们。
get_file_type(file_path) 用于解析文档的后缀，配合阿里云的文档解析服务使用，也可以用于文件合法性审查
"""
def env_reader() -> bool:
    try:
        # 获取当前文件的绝对路径
        current_file_path = os.path.abspath(__file__)
        # 获取当前文件所在目录（即 aurawell/rag）
        current_dir = os.path.dirname(current_file_path)
        # 获取项目根目录（假设 rag_utils.py 在 aurawell/rag/ 目录下）
        project_root = os.path.dirname(os.path.dirname(current_dir))
        # 构建 .env 文件的完整路径
        dotenv_path = os.path.join(project_root, '.env')

        # 加载指定路径下的 .env 文件
        load_dotenv(dotenv_path=dotenv_path)

        # 读取环境变量
        access_key_id = getenv("ALIBABA_CLOUD_ACCESS_KEY_ID")
        access_key_secret = getenv("ALIBABA_CLOUD_ACCESS_KEY_SECRET")
        dash_scope_key = getenv("DASHSCOPE_API_KEY")
        # 打印结果（调试用）
        print("AccessKey ID:", access_key_id)
        print("AccessKey Secret:", access_key_secret)
        print("DashScope API key: ", dash_scope_key)
        # 检查环境变量是否有效
        if access_key_id and access_key_secret:
            return True
        else:
            return False

    except Exception as e:
        print(f"环境变量读取失败: {str(e)}")
        return False

def process_list(input_list:list)->list:
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


def export_strings_to_files(self, raw_text):
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

def get_file_type(file_path:str)->str:
    try:
        # 检查输入是否为空或非字符串
        if not file_path or not isinstance(file_path, str):
            return "Unknown"

        # 获取文件扩展名并转为小写
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()

        if not ext:
            return "Unknown"

        # 文件类型映射字典
        file_type_mapping = {
            # 文本文件
            '.txt': 'Text',
            '.md': 'Markdown',
            '.rtf': 'Rich Text',

            # 文档文件
            '.pdf': 'pdf',
            '.doc': 'doc',
            '.docx': 'docx',
            '.odt': 'OpenDocument Text',
            '.xls': 'xls',
            '.xlsx': 'xlsx',
            '.ppt': '.ppt',
            '.pptx': '.pptx',

            # 图像文件
            '.jpg': 'Image',
            '.jpeg': 'Image',
            '.png': 'Image',
            '.gif': 'Image',
            '.bmp': 'Image',
            '.svg': 'Vector Image',
            '.tiff': 'Image',

            # 音频文件
            '.mp3': 'Audio',
            '.wav': 'Audio',
            '.flac': 'Audio',
            '.aac': 'Audio',
            '.ogg': 'Audio',

            # 视频文件
            '.mp4': 'Video',
            '.avi': 'Video',
            '.mov': 'Video',
            '.mkv': 'Video',
            '.flv': 'Video',

            # 压缩文件
            '.zip': 'Archive',
            '.rar': 'Archive',
            '.7z': 'Archive',
            '.tar': 'Archive',
            '.gz': 'Compressed File',

            # 程序文件
            '.py': 'Python Script',
            '.js': 'JavaScript File',
            '.java': 'Java Source',
            '.c': 'C Source',
            '.cpp': 'C++ Source',
            '.cs': 'C# Source',
            '.html': 'HTML Document',
            '.css': 'Stylesheet',
            '.php': 'PHP Script',

            # 数据文件
            '.json': 'JSON File',
            '.xml': 'XML File',
            '.csv': 'CSV File',
            '.sql': 'SQL Script',
            '.db': 'Database',
        }

        return file_type_mapping.get(ext, "Unknown")

    except IOError:
        # 捕获所有可能的异常
        print(f"Can not open this file: {file_path}")
        return "Can not open this file"


if  __name__ == "__main__":
    print(env_reader())