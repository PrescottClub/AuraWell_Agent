import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import os
import re
import time
import ssl
from rag_utils import get_download_path

def fetch_papers_by_keyword(keyword, max_results=10, days_ago=None):
    """
    根据关键词从arXiv检索相关论文

    参数:
    keyword (str): 搜索关键词
    max_results (int): 返回的最大论文数量 (默认10)
    days_ago (int): 仅检索最近N天的论文 (可选)

    返回:
    list: 包含论文信息的字典列表
    """
    # 构建查询参数 - 处理多词关键词
    # 如果关键词包含空格，用引号包围或用AND连接
    if ' ' in keyword:
        search_term = f'all:"{keyword}"'  # 用引号包围多词关键词
    else:
        search_term = f"all:{keyword}"

    base_params = {
        "search_query": search_term,       # 使用处理后的关键词
        "sortBy": "submittedDate",         # 按提交日期排序
        "sortOrder": "descending"          # 最新优先
    }

    # 添加时间范围过滤
    if days_ago:
        date_str = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        base_params["search_query"] += f" AND submittedDate:[{date_str} TO NOW]"

    # 添加结果限制
    query_params = {**base_params, "start": 0, "max_results": max_results}

    try:
        # 构建请求URL
        api_url = "http://export.arxiv.org/api/query?" + urllib.parse.urlencode(query_params)

        # 创建SSL上下文，忽略证书验证（仅用于测试）
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        # 发送API请求
        request = urllib.request.Request(api_url)
        with urllib.request.urlopen(request, timeout=30, context=ssl_context) as response:
            xml_data = response.read().decode('utf-8')

        # 解析XML结果
        return parse_arxiv_xml(xml_data)

    except Exception as e:
        print(f"API请求失败: {str(e)}")
        return []

def parse_arxiv_xml(xml_string):
    """
    解析arXiv返回的XML数据
    
    返回包含论文信息的字典列表
    """
    root = ET.fromstring(xml_string)
    namespace = {'atom': 'http://www.w3.org/2005/Atom'}
    papers = []
    
    for entry in root.findall('atom:entry', namespace):
        paper = {
            "title": entry.find('atom:title', namespace).text.strip(),
            "id": entry.find('atom:id', namespace).text.split('/')[-1],
            "published": entry.find('atom:published', namespace).text,
            "summary": entry.find('atom:summary', namespace).text.strip(),
            "authors": [a.find('atom:name', namespace).text 
                        for a in entry.findall('atom:author', namespace)],
            "pdf_url": None
        }
        
        # 提取PDF链接 - 修复链接提取逻辑
        for link in entry.findall('atom:link', namespace):
            if link.get('title') == 'pdf':
                paper['pdf_url'] = link.get('href')
                break

        # 如果没找到PDF链接，尝试从ID构建PDF URL
        if not paper['pdf_url'] and paper['id']:
            paper['pdf_url'] = f"https://arxiv.org/pdf/{paper['id']}.pdf"
        
        papers.append(paper)
    
    return papers
def download_pdf(pdf_url, save_dir=None):
    """
    下载论文PDF到指定目录
    
    参数:
    pdf_url (str): PDF文件的URL
    save_dir (str): 保存目录（可选），默认使用跨平台路径
    
    返回:
    str: 下载的文件路径，失败返回None
    """
    if not pdf_url:
        print("错误：未提供有效的PDF URL")
        return None
    
    # 使用默认路径或自定义路径
    if save_dir is None:
        save_dir = get_download_path()
    
    # 创建保存目录
    os.makedirs(save_dir, exist_ok=True)
    
    # 从URL提取文件名
    filename = re.search(r'/([^/]+\.pdf)$', pdf_url)
    if not filename:
        filename = f"paper_{int(time.time())}.pdf"
    else:
        filename = filename.group(1)
    
    file_path = os.path.join(save_dir, filename)
    
    try:
        # 创建SSL上下文，忽略证书验证（仅用于测试）
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        # 创建opener with SSL context
        opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ssl_context))
        urllib.request.install_opener(opener)

        # 下载文件
        urllib.request.urlretrieve(pdf_url, file_path)
        print(f"已下载: {file_path}")
        return file_path
    except Exception as e:
        print(f"下载失败: {str(e)}")
        return None

def generate_ris(paper, save_dir="exports"):
    """
    生成RIS格式文献引用文件
    
    参数:
    paper (dict): 论文信息字典
    save_dir (str): 保存目录
    
    返回:
    str: RIS文件路径
    """
    os.makedirs(save_dir, exist_ok=True)
    filename = f"{paper['id']}.ris"
    file_path = os.path.join(save_dir, filename)
    
    # RIS格式模板
    ris_content = f"""TY  - JOUR
TI  - {paper['title']}
AU  - {paper['authors'][0]}  # 只使用第一作者
PY  - {paper['published'][:4]}  # 仅年份
AB  - {paper['summary'][:500]}  # 摘要截断
UR  - https://arxiv.org/abs/{paper['id']}
DO  - 10.48550/arXiv.{paper['id']}
ER  - -"""
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(ris_content)
    
    print(f"已生成RIS引用文件: {file_path}")
    return file_path
def export_papers_by_keyword(keyword, k=10, save_dir=None):
    """
    根据关键词搜索并导出k个相关文献到指定目录

    参数:
    keyword (str): 搜索关键词
    k (int): 导出的文献数量 (默认10)
    save_dir (str): 保存目录，默认为项目根目录下的 nutrition_article 文件夹

    返回:
    list: 成功下载的文献信息列表
    """
    # 设置保存目录
    if save_dir is None:
        save_dir = get_download_path()

    print(f"正在搜索关键词 '{keyword}' 相关的论文...")

    # 检索论文
    results = fetch_papers_by_keyword(keyword, max_results=k)

    if not results:
        print(f"未找到与关键词 '{keyword}' 相关的论文")
        return []

    print(f"\n找到 {len(results)} 篇与 '{keyword}' 相关的论文:")
    print(f"保存目录: {save_dir}")

    downloaded_papers = []

    # 处理每篇论文
    for i, paper in enumerate(results, 1):
        print(f"\n[{i}/{len(results)}] 处理论文: {paper['title'][:80]}...")

        # 下载PDF
        if paper['pdf_url']:
            pdf_path = download_pdf(paper['pdf_url'], save_dir=save_dir)
            if pdf_path:
                downloaded_papers.append({
                    'title': paper['title'],
                    'authors': paper['authors'],
                    'published': paper['published'],
                    'pdf_path': pdf_path,
                    'arxiv_id': paper['id']
                })
        else:
            print("  未找到PDF链接，跳过下载")

    print(f"\n导出完成！成功下载 {len(downloaded_papers)} 篇论文到 {save_dir}")

    # 显示下载的论文列表
    if downloaded_papers:
        print("\n已下载的论文:")
        for paper in downloaded_papers:
            print(f"  - {paper['title'][:60]}... ({paper['arxiv_id']})")

    return downloaded_papers

def main_workflow():
    """主工作流程示例：使用默认关键词搜索营养学论文"""
    export_papers_by_keyword("nutrition", k=5)
if __name__ == "__main__":
    main_workflow()
