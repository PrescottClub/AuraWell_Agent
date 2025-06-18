import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import os
import re
import time
import sqlite3
from rag_utils import get_download_path

def fetch_nutrition_papers(max_results=10, days_ago=None):
    """
    从arXiv检索营养学相关论文
    
    参数:
    max_results (int): 返回的最大论文数量 (默认10)
    days_ago (int): 仅检索最近N天的论文 (可选)
    
    返回:
    list: 包含论文信息的字典列表
    """
    # 构建查询参数
    base_params = {
        "search_query": "all:nutrition",  # 核心营养学关键词
        "sortBy": "submittedDate",        # 按提交日期排序
        "sortOrder": "descending"         # 最新优先
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
        
        # 发送API请求
        with urllib.request.urlopen(api_url, timeout=30) as response:
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
        
        # 提取PDF链接
        for link in entry.findall('atom:link', namespace):
            if link.get('title') == 'pdf' and link.get('rel') == 'related':
                paper['pdf_url'] = link.get('href')
                break
        
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
        # 下载文件
        urllib.request.urlretrieve(pdf_url, file_path)
        print(f"已下载: {file_path}")
        return file_path
    except Exception as e:
        print(f"下载失败: {str(e)}")
        return None
def init_database(db_path="nutrition_library.db"):
    """
    初始化文献管理数据库
    
    返回:
    sqlite3.Connection: 数据库连接对象
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建文献表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS papers (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        published DATE NOT NULL,
        authors TEXT,
        summary TEXT,
        pdf_path TEXT,
        added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    return conn
def save_to_database(paper, pdf_path, conn):
    """
    将论文信息保存到数据库
    
    参数:
    paper (dict): 论文信息字典
    pdf_path (str): PDF文件路径
    conn: SQLite数据库连接
    """
    cursor = conn.cursor()
    
    # 检查是否已存在
    cursor.execute("SELECT id FROM papers WHERE id = ?", (paper['id'],))
    if cursor.fetchone():
        print(f"论文 {paper['id']} 已存在于数据库")
        return False
    
    # 插入新记录
    authors_str = "; ".join(paper['authors'])
    cursor.execute('''
    INSERT INTO papers (id, title, published, authors, summary, pdf_path)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        paper['id'],
        paper['title'],
        paper['published'],
        authors_str,
        paper['summary'],
        pdf_path
    ))
    
    conn.commit()
    print(f"已保存到数据库: {paper['title']}")
    return True
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
def main_workflow():
    """主工作流程：检索-下载-存储-导出"""
    # 创建文献数据库
    db_conn = init_database()
    
    # 检索营养学论文
    print("正在检索营养学最新论文...")
    results = fetch_nutrition_papers(max_results=5, days_ago=30)
    
    if not results:
        print("未找到相关论文")
        return
    
    print(f"\n找到 {len(results)} 篇营养学相关论文:")
    
    # 使用跨平台路径
    download_dir = get_download_path()
    print(f"使用下载目录: {download_dir}")
    
    # 处理每篇论文
    for paper in results:
        print(f"\n处理论文: {paper['title']}")
        
        # 下载PDF
        pdf_path = None
        if paper['pdf_url']:
            pdf_path = download_pdf(paper['pdf_url'], save_dir=download_dir)
        
        # 保存到数据库
        if pdf_path:
            save_to_database(paper, pdf_path, db_conn)
        else:
            print("未下载PDF，跳过数据库存储")
        
        # 生成RIS引用文件
        generate_ris(paper)
    
    # 关闭数据库连接
    db_conn.close()
    print("\n文献管理流程完成！")
    
    # 提供使用建议
    print("\n下一步建议:")
    print("1. 查看 nutrition_papers/ 目录下载的PDF文献")
    print("2. 使用文献管理软件导入 exports/ 目录的RIS文件")
    print("3. 使用SQLite查看器打开 nutrition_library.db 管理文献数据库")
if __name__ == "__main__":
    main_workflow()
